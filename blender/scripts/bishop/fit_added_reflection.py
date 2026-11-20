"""Fit a restrained new reflector through the saved Standard sRGB response."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--response',required=True);p.add_argument('--out',required=True)
p.add_argument('--core-weight',type=float,default=1);p.add_argument('--white-only',action='store_true')
a=p.parse_args();source=ROOT/a.response;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
manifest=json.loads((source/'manifest.json').read_text())
base=np.load(source/'base.npy');added=np.load(source/'added.npy');response=np.maximum(added[:,:,:3]-base[:,:,:3],0)
reference=np.array(Image.open(ROOT/'assets/bishop/reference.png').convert('RGB'),dtype=np.float32)/255
mask=base[:,:,3]>.995
def display(rgb):
    rgb=np.maximum(rgb,0);return np.clip(np.where(rgb<=.0031308,12.92*rgb,1.055*rgb**(1/2.4)-.055),0,1)
yy,xx=np.mgrid[:base.shape[0],:base.shape[1]]
tip=(((xx-497)/15)**2+((yy-430)/12)**2<1)&mask
context=(xx>445)&(xx<560)&(yy>390)&(yy<475)&mask
spill=mask&~context
# Missing glint is local; protect all already-lit surfaces from extra spill.
weight=np.where(tip,1.,np.where(context,.25,0))*mask
core=tip&(reference[:,:,1]>245/255)
weight[core]*=a.core_weight
active=weight>0;before=display(base[:,:,:3]);target=reference[active];b=base[:,:,:3][active];r=response[active]
def loss(power,color):
    pred=display(b+power*r*color);error=np.abs(pred-target)
    huber=np.where(error<.06,.5*error*error,.06*(error-.03))
    return float((huber*weight[active,None]).sum()/weight[active].sum())
fits=[]
for color in ([[1,1,1]] if a.white_only else [[1,1,1],[1,1,.9],[1,.9,.7]]):
    powers=np.r_[0,np.geomspace(1e-5,1000,161)]
    losses=[loss(power,np.array(color)) for power in powers]
    power=float(powers[int(np.argmin(losses))])
    for _ in range(2):
        powers=np.linspace(power*.75,power*1.25+1e-6,51)
        losses=[loss(value,np.array(color)) for value in powers];power=float(powers[int(np.argmin(losses))])
    fits.append({'color':color,'coefficient':power,'loss':loss(power,np.array(color))})
best=min(fits,key=lambda item:item['loss']);prediction=display(base[:,:,:3]+best['coefficient']*response*np.array(best['color']))
spec=manifest['config']['lights'][0].copy();spec['energy']=best['coefficient']*manifest['basis_energy'];spec['color']=best['color']
cfg={'source':manifest['source'],'variant':out.name,'samples':manifest['samples'],'adaptive_sampling':manifest.get('adaptive_sampling',True),'lights':[spec],
     'hypothesis':'A confined real reflection restores the missing slit-tip glint while retaining the accepted geometry, pigment and other lights.'}
(out/'lighting-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
report={'response':a.response,'fits':fits,'chosen':best,'weighted_loss_before':loss(0,np.array([1,1,1])),
        'spill_scope':'Only the captured crop; a full render is still required.' if manifest.get('render_border_pixels') else 'Full captured bishop foreground.',
        'core_weight':a.core_weight,'white_only':a.white_only,'reference_core_pixels':int(core.sum()),
        'tip_pixels':int(tip.sum()),'predicted_tip_rgb_error_before':float(np.abs(before[tip]-reference[tip]).mean()*255),
        'predicted_tip_rgb_error_after':float(np.abs(prediction[tip]-reference[tip]).mean()*255),
        'predicted_spill_mean_8bit':float(np.abs(prediction[spill]-before[spill]).mean()*255),
        'predicted_spill_p99_8bit':float(np.quantile(np.abs(prediction[spill]-before[spill]),.99)*255),
        'predicted_spill_max_8bit':float(np.max(np.abs(prediction[spill]-before[spill]))*255),
        'predicted_spill_pixels_over_5_levels':int((np.max(np.abs(prediction-before),axis=2)[spill]>5/255).sum()),
        'note':'Diagnostic prediction; capture noise and clipping affect this fit. Judge only after an actual full-scene render.'}
(out/'fit.json').write_text(json.dumps(report,indent=2)+'\n')
canvas=Image.new('RGB',(1200,440),'#161b20');draw=ImageDraw.Draw(canvas)
for i,(label,pixels) in enumerate([('Reference',reference),('Current response',before),('Predicted added reflection',prediction)]):
    tile=Image.fromarray(np.uint8(np.rint(pixels[390:475,455:555]*255))).resize((400,340),Image.Resampling.NEAREST)
    canvas.paste(tile,(i*400,65));draw.text((i*400+12,20),label,fill='white')
canvas.save(out/'prediction.png');print(json.dumps(report,indent=2))

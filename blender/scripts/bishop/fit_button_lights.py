"""Fit two real reflector RGB powers through Standard sRGB, including highlight clipping."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--responses',required=True);p.add_argument('--out',required=True)
p.add_argument('--response-blur',type=int,default=0);p.add_argument('--glints-only',action='store_true')
p.add_argument('--max-red-green',type=float,help='Limit poorly constrained clipped red power relative to green, keeping a plausible warm white reflector.')
a=p.parse_args();directory=ROOT/a.responses;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
manifest=json.loads((directory/'manifest.json').read_text());base=np.load(directory/'base.npy')[:,:,:3]
responses=np.stack([np.maximum(np.load(directory/f'reflector-{i}.npy')[:,:,:3]-base,0) for i in (1,2)])
if a.response_blur:responses=np.stack([blur(response,a.response_blur) for response in responses])
mask=np.load(directory/'mask.npy')[:,:,0]>.99;mask=blur(mask.astype(np.float32),radius=2)>.999
target=np.array(Image.open(ROOT/'assets/bishop/reference.png').convert('RGB'),dtype=np.float32)/255
def display(rgb):
    rgb=np.maximum(rgb,0);return np.clip(np.where(rgb<=.0031308,rgb*12.92,1.055*np.power(rgb,1/2.4)-.055),0,1)
base_display=display(base)
# Fit the reference glints and their surrounding area; the diffuse pigment is fixed.
support=np.maximum(responses.max((0,3)),np.max(target-base_display,axis=2))
weight=(.15+.85*np.clip(support/.2,0,1))*mask
if a.glints_only:
    yy,xx=np.mgrid[:mask.shape[0],:mask.shape[1]]
    glints=(((xx-516)/22)**2+((yy-235)/25)**2<1)|(((xx-481)/14)**2+((yy-247)/12)**2<1)
    weight*=np.where(glints,1,.04)
active=weight>0;weights=weight[active];t=target[active];b=base[active];A=responses[:,active,:]
prior=np.array([lamp['energy']/manifest['basis_energy']*np.array(lamp['color']) for lamp in manifest['original_lights']])
coeff=prior.copy()
def loss(channel,values):
    pred=display(b[:,channel]+values@A[:,:,channel])
    err=np.abs(pred-t[:,channel]);huber=np.where(err<.04,.5*err*err,.04*(err-.02))
    return float(np.sum(weights*huber)/weights.sum())
for channel in range(3):
    for sweep in range(4):
        for light in range(2):
            center=coeff[light,channel]
            candidates=np.unique(np.r_[0,np.geomspace(.01,12,65),center]) if sweep==0 else np.linspace(max(0,center*.65-.03),center*1.35+.03,33)
            losses=[]
            for value in candidates:
                trial=coeff[:,channel].copy();trial[light]=value;losses.append(loss(channel,trial))
            coeff[light,channel]=candidates[int(np.argmin(losses))]
unconstrained=coeff.copy()
if a.max_red_green:
    assert a.max_red_green>=1
    coeff[:,0]=np.minimum(coeff[:,0],coeff[:,1]*a.max_red_green)
lights=[]
for i,lamp in enumerate(manifest['original_lights']):
    strength=float(coeff[i].max());spec={'name':lamp['name'],'energy':manifest['basis_energy']*strength,'color':(coeff[i]/max(strength,1e-9)).tolist()}
    if manifest.get('lighting_config'):
        shape=next(s for s in manifest['lighting_config']['lights'] if s['name']==lamp['name'])
        spec={**shape,**spec}
    lights.append(spec)
cfg={'source':manifest['source'],'variant':out.name,'samples':48,'lights':lights,'hypothesis':'Measured two-reflector RGB response, optimized through Standard sRGB clipping. Geometry, texture and the fixed camera stay unchanged. Lamp shape/pose changes, when present, are explicitly recorded in the light specifications.'}
(out/'lighting-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
prediction=display(base+np.einsum('lc,lxyc->xyc',coeff,responses));old_prediction=display(base+np.einsum('lc,lxyc->xyc',prior,responses))
np.save(out/'predicted-display.npy',prediction)
record={'responses':a.responses,'response_blur':a.response_blur,'glints_only':a.glints_only,'max_red_green':a.max_red_green,'unconstrained_coefficients':unconstrained.tolist(),'coefficients':coeff.tolist(),'prior_coefficients':prior.tolist(),'weighted_channel_loss_before':[loss(c,prior[:,c]) for c in range(3)],'weighted_channel_loss_after':[loss(c,coeff[:,c]) for c in range(3)],'fit_pixels':int(active.sum()),'caveat':'Prediction is a diagnostic. Accept only after an actual full-scene BSDF render and visual comparison.'}
(out/'fit.json').write_text(json.dumps(record,indent=2)+'\n')
canvas=Image.new('RGB',(900,330),'#171b21');d=ImageDraw.Draw(canvas)
prior_label='Shape at prior power' if manifest.get('lighting_config') else 'Previous prediction'
for i,(label,im) in enumerate([('Reference',target),(prior_label,old_prediction),('Fitted prediction',prediction)]):
    crop=np.uint8(np.rint(im[152:288,414:570]*255));tile=Image.fromarray(crop).resize((300,262));canvas.paste(tile,(300*i,50));d.text((300*i+10,12),label,fill='white')
canvas.save(out/'prediction.png');print(json.dumps(record,indent=2))

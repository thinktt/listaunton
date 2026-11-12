"""Fit confined collar lamp powers; prediction requires a fresh full render."""
import argparse, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--folder',default='build/bishop-mission/111-collar-spots')
p.add_argument('--out',default='scripts/bishop/lighting-112.json')
a=p.parse_args();folder=ROOT/a.folder
manifest=json.loads((folder/'manifest.json').read_text());cfg=manifest['config']
box=manifest['border'];x0,y0,x1,y1=box
ref=np.array(Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA'),dtype=np.float32)[y0:y1,x0:x1]/255
base=np.load(folder/'base.npy')[y0:y1,x0:x1]
target=ref[:,:,:3]
mask=(ref[:,:,3]>.5)&(target.max(2)>12/255)&(base[:,:,3]>.999)
mask=blur(mask.astype(np.float32),3)>.999
core=mask&(target[:,:,0]>210/255)&(target[:,:,1]>150/255)&(target[:,:,2]>70/255)
weight=np.where(core,2,1)[mask].astype(np.float32)
color=np.array([1,.97,.88],dtype=np.float32)
responses=[]
for i in range(len(cfg['lights'])):
    response=np.load(folder/('lamp-'+str(i+1)+'.npy'))[y0:y1,x0:x1,:3]-base[:,:,:3]
    responses.append(np.maximum(blur(response,1),0)*color)
responses=np.array(responses)
fit_responses=responses[:,mask,:]
b=base[:,:,:3][mask];t=target[mask]
def srgb(x):
    return np.clip(np.where(x<=.0031308, x*12.92, 1.055*np.maximum(x,0)**(1/2.4)-.055),0,1)
def loss(linear):
    return float((np.abs(srgb(linear)-t).mean(1)*weight).sum()/weight.sum()*255)
factors=np.zeros(len(responses),dtype=np.float32)
current=b.copy()
for step in [1,.25,.05,.01]:
    for sweep in range(3):
        previous=factors.copy()
        for i in range(len(factors)):
            rest=current-factors[i]*fit_responses[i]
            values=np.arange(max(0,factors[i]-4*step),min(6,factors[i]+4*step)+step/2,step)
            costs=[loss(rest+v*fit_responses[i]) for v in values]
            factors[i]=values[np.argmin(costs)]
            current=rest+factors[i]*fit_responses[i]
        if np.array_equal(previous,factors):break
prediction=srgb(base[:,:,:3]+np.tensordot(factors,responses,axes=1))
def metrics(values):
    e=np.abs(values-target)
    return dict(rgb_mae_8bit=float(e[mask].mean()*255),core_mae_8bit=float(e[core].mean()*255))
for spec,factor in zip(cfg['lights'],factors):spec['energy']*=float(factor)
cfg['lights']=[spec for spec in cfg['lights'] if spec['energy']>.01]
cfg['fit']=dict(responses=a.folder,box=box,power_factors=factors.tolist(),
              weighted_error_before=loss(b),weighted_error_after=loss(current),
              before=metrics(srgb(base[:,:,:3])),prediction=metrics(prediction),
              note='Prediction only. Fixed coordinates, bounded nonnegative lamp power, same color and placement. No reference edits.')
(ROOT/a.out).write_text(json.dumps(cfg,indent=2)+'\n',newline='\n')
canvas=Image.new('RGB',(1800,490),'#171b21');draw=ImageDraw.Draw(canvas)
for i,(label,pixels) in enumerate([('Selected white 3',target),('Accepted 013 actual pass',srgb(base[:,:,:3])),('PREDICTION localized collar lamps',prediction)]):
    im=Image.fromarray(np.uint8(np.clip(pixels,0,1)*255+.5)).resize((600,429),Image.Resampling.LANCZOS)
    canvas.paste(im,(600*i,40));draw.text((600*i+10,12),label,fill='white')
canvas.save(folder/'fit-prediction.png')
(folder/'fit.json').write_text(json.dumps(cfg['fit'],indent=2)+'\n',newline='\n')
print(json.dumps(cfg['fit'],indent=2))

"""Fit nonnegative diffuse light powers and one shared tint to measured BSDF passes."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--capture',required=True);p.add_argument('--out',required=True)
a=p.parse_args();folder=ROOT/a.capture;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
meta=json.loads((folder/'manifest.json').read_text());size=meta['size']
reference=np.array(Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA'),dtype=np.float32)/255
linear=np.where(reference[:,:,:3]<=.04045,reference[:,:,:3]/12.92,((reference[:,:,:3]+.055)/1.055)**2.4)
def resize(ar):return np.array(Image.fromarray(ar.astype(np.float32),mode='F').resize((size,size),Image.Resampling.BILINEAR))
ref=np.stack([resize(linear[:,:,i]) for i in range(3)],axis=2)
alpha=resize(reference[:,:,3]);base=np.load(folder/'preserved-reflections.npy')
response=np.stack([np.maximum(np.load(folder/f'basis-{i:02d}.npy')[:,:,:3]-base[:,:,:3],0) for i in range(len(meta['basis']['directions']))])
mask=(alpha>.99)&(base[:,:,3]>.999)&(ref.max(2)>.005)&(ref.max(2)<.85)
mask=blur(mask.astype(np.float32),3)>.999
target=blur(np.maximum(ref-base[:,:,:3],0),2)
smooth=np.stack([blur(v,2) for v in response])
matrices=[smooth[:,:,:,c][:,mask].T.astype(np.float64) for c in range(3)]
targets=[target[:,:,c][mask].astype(np.float64) for c in range(3)]
grams=[m.T@m for m in matrices];rhs=[m.T@v for m,v in zip(matrices,targets)]
count=len(response);tint=np.ones(3);power=np.zeros(count)
for outer in range(12):
    gram=sum(t*t*g for t,g in zip(tint,grams));b=sum(t*v for t,v in zip(tint,rhs))
    ridge=.001*np.trace(gram)/count;gram+=np.eye(count)*ridge
    for iteration in range(2000):
        previous=power.copy()
        for k in range(count):power[k]=np.clip(power[k]+(b[k]-gram[k]@power)/gram[k,k],0,20)
        if np.max(np.abs(power-previous))<1e-7:break
    for c in range(3):
        prediction=matrices[c]@power
        tint[c]=np.clip(np.dot(prediction,targets[c])/max(np.dot(prediction,prediction),1e-12),.25,4)
    gain=tint.mean();tint/=gain;power*=gain
prediction=base[:,:,:3]+np.einsum('k,kijc,c->ijc',power,response,tint)
def srgb(value):return np.clip(np.where(value<=.0031308,12.92*value,1.055*np.maximum(value,0)**(1/2.4)-.055),0,1)
def mae(value):return float(np.abs(srgb(value)[mask]-srgb(ref)[mask]).mean()*255)
max_tint=float(tint.max());color=(tint/max_tint).tolist()
lamps=[{'name':f'Study diffuse {i:02d}','direction':direction,'energy':float(power[i]*max_tint),'color':color} for i,direction in enumerate(meta['basis']['directions'])]
result={'source':meta['source'],'source_sha256':meta['source_sha256'],'capture':a.capture,'basis':meta['basis'],
 'lights':lamps,'shared_tint':tint.tolist(),'fitting_pixels':int(mask.sum()),
 'predicted_rgb_error_8bit':mae(prediction),'regularization':'Nonnegative energies, shared lamp tint, weak L2 penalty. No per-pixel lights or reference composition in the saved material.',
 'prediction_only':True,'reference_sha256':hashlib.sha256((ROOT/'assets/bishop/reference.png').read_bytes()).hexdigest()}
(out/'fit.json').write_text(json.dumps(result,indent=2)+'\n')
canvas=Image.new('RGB',(size*3,size+40),'#171b21');draw=ImageDraw.Draw(canvas)
control=np.array(Image.open(ROOT/'build/bishop-mission/100-coherent-pigment/wood.png').convert('RGB').resize((size,size),Image.Resampling.LANCZOS))
for i,(label,ar) in enumerate([('Reference',np.uint8(np.rint(srgb(ref)*255))),('Continuous pigment / old lights',control),('Response prediction — not a render',np.uint8(np.rint(srgb(prediction)*255)))]):
    canvas.paste(Image.fromarray(ar),(i*size,40));draw.text((i*size+8,12),label,fill='white')
canvas.save(out/'prediction.png');print(json.dumps({'predicted_rgb_error_8bit':result['predicted_rgb_error_8bit'],'shared_tint':result['shared_tint'],'active_lights':sum(v['energy']>.01 for v in lamps)},indent=2))

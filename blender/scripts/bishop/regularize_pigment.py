"""Build a continuous broad pigment field, keeping bounded existing fine grain.

Unlike hidden-only fills, all broad pigment values may move. The original
projection confidence softly constrains the field. References are never edited.
The result is an isolated texture candidate that requires actual BSDF rendering.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--coverage',required=True);p.add_argument('--out',required=True)
p.add_argument('--screen-weight',type=float,default=.05);p.add_argument('--grain-radius',type=int,default=12);p.add_argument('--grid-width',type=int,default=128)
p.add_argument('--iterations',type=int,default=5000)
p.add_argument('--grain-source',help='Optional inferred atlas: replace old low-confidence fine residue with its zero-mean grain.')
a=p.parse_args();source=ROOT/a.source;coverage_path=ROOT/a.coverage;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
original=np.array(Image.open(source).convert('RGBA'));rgb=original[:,:,:3].astype(np.float32)/255
linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);log=np.log(np.maximum(linear,.0001))
coverage=np.clip(np.load(coverage_path),0,1);assert coverage.shape==(2048,2048)==original.shape[:2]
result=log.copy();records={};mask=np.zeros(coverage.shape,bool)
inferred_log=None
if a.grain_source:
    srgb=np.array(Image.open(ROOT/a.grain_source).convert('RGB'),dtype=np.float32)/255
    inferred_log=np.log(np.maximum(np.where(srgb<=.04045,srgb/12.92,((srgb+.055)/1.055)**2.4),.0001))
def resize(ar,size):return np.array(Image.fromarray(ar.astype(np.float32),mode='F').resize(size,Image.Resampling.BILINEAR))
for name,(v0,v1) in {'body':(.01,.70),'button':(.73,.88)}.items():
    y0,y1=int((1-v1)*2048),int((1-v0)*2048)+1;x0,x1=int(.01*2048),int(.99*2048)+1;sl=np.s_[y0:y1,x0:x1]
    old=log[sl];broad=blur(old,a.grain_radius,2);fine=np.clip(old-broad,-.4,.3)
    if inferred_log is not None:
        clean_fine=np.clip(inferred_log[sl]-blur(inferred_log[sl],a.grain_radius,2),-.22,.22)
        fine_confidence=coverage[sl]**8
        fine=fine*fine_confidence[:,:,None]+clean_fine*(1-fine_confidence[:,:,None])
    width=a.grid_width;height=max(24,round(width*old.shape[0]/old.shape[1]));size=(width,height)
    data=np.stack([resize(broad[:,:,c],size) for c in range(3)],axis=2)
    confidence=resize(coverage[sl]**4,size);weight=a.screen_weight*confidence
    # A weak screen fixes the nullspace of isolated/no-confidence rows without
    # imposing the old dark procedural exterior as a boundary condition.
    center=np.median(data[confidence>.8],axis=0);anchor=.00005
    field=np.broadcast_to(center,data.shape).copy();yy,xx=np.mgrid[:height,:width];parity=(xx+yy)%2
    for iteration in range(a.iterations):
        maximum=0
        for color in [0,1]:
            neighbours=np.roll(field,1,1)+np.roll(field,-1,1)+np.r_[field[:1],field[:-1]]+np.r_[field[1:],field[-1:]]
            target=(neighbours+weight[:,:,None]*data+anchor*center)/(4+weight[:,:,None]+anchor)
            active=parity==color;delta=1.7*(target-field);maximum=max(maximum,float(np.abs(delta[active]).max()));field[active]+=delta[active]
        if maximum<1e-5:break
    continuous=np.stack([resize(field[:,:,c],(old.shape[1],old.shape[0])) for c in range(3)],axis=2)
    result[sl]=continuous+fine;mask[sl]=True
    records[name]={'grid':[width,height],'iterations':iteration+1,'max_final_update_log_rgb':maximum,
        'confidence_mean':float(confidence.mean()),'center_linear_rgb':np.exp(center).tolist(),
        'broad_log_rgb_mean_change':float(np.abs(continuous-broad).mean())}
value=np.exp(result);srgb=np.where(value<=.0031308,12.92*value,1.055*np.power(value,1/2.4)-.055)
new=original.copy();new[:,:,:3]=np.uint8(np.rint(np.clip(srgb,0,1)*255));new[~mask]=original[~mask]
Image.fromarray(new).save(out/'albedo.png')
canvas=Image.new('RGB',(1024,550),'#171b21');d=ImageDraw.Draw(canvas)
for i,(label,ar) in enumerate([('Accepted pigment',original),('Regularized broad pigment',new)]):
    canvas.paste(Image.fromarray(ar).convert('RGB').resize((512,512)),(512*i,38));d.text((512*i+10,12),label,fill='white')
canvas.save(out/'atlas-comparison.png')
report={'source':a.source,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'coverage':a.coverage,'coverage_sha256':hashlib.sha256(coverage_path.read_bytes()).hexdigest(),
 'output_sha256':hashlib.sha256((out/'albedo.png').read_bytes()).hexdigest(),'parameters':vars(a),'regions':records,
 'method':'Screened periodic Poisson broad log-linear pigment field with soft original-confidence constraints, plus bounded existing fine grain. All broad colors may move. Caps and unused atlas areas unchanged.',
 'status':'Unaccepted interpretation; render fixed and rear views and measure any original/reference regression.'}
if a.grain_source:
    report['grain_source_sha256']=hashlib.sha256((ROOT/a.grain_source).read_bytes()).hexdigest()
    report['method']+=' Low-confidence old fine residue replaced with inferred grain, using original confidence to the eighth power.'
(out/'regularization.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

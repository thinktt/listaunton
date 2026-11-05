"""Continue visible boundary colors smoothly around hidden turned surfaces."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--visibility',required=True);p.add_argument('--out',required=True)
p.add_argument('--grid-width',type=int,default=256);p.add_argument('--iterations',type=int,default=2000)
p.add_argument('--protection-threshold',type=float,default=.002);p.add_argument('--dilation',type=int,default=8);p.add_argument('--feather',type=int,default=24)
a=p.parse_args();source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
original=np.array(Image.open(source).convert('RGBA'));rgb=original[:,:,:3].astype(np.float32)/255
linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);log=np.log(np.maximum(linear,.0001))
visibility=np.load(ROOT/a.visibility);assert visibility.shape==original.shape[:2]==(2048,2048)
result=log.copy();weightmap=np.zeros(visibility.shape,dtype=np.float32);record={}
def grow(m):return m|np.roll(m,1,1)|np.roll(m,-1,1)|np.r_[m[:1],m[:-1]]|np.r_[m[1:],m[-1:]]
def resize(array,size):return np.array(Image.fromarray(array.astype(np.float32),mode='F').resize(size,Image.Resampling.BILINEAR))
for name,(v0,v1) in {'body':(.01,.70),'button':(.73,.88)}.items():
    y0,y1=int((1-v1)*2048),int((1-v0)*2048)+1;x0,x1=int(.01*2048),int(.99*2048)+1;sl=np.s_[y0:y1,x0:x1]
    old=log[sl];protected=visibility[sl]>a.protection_threshold
    for _ in range(a.dilation):protected=grow(protected)
    broad=blur(old,8,2);fine=old-broad
    width=a.grid_width;height=max(24,round(width*old.shape[0]/old.shape[1]));size=(width,height)
    coarse=np.stack([resize(broad[:,:,c],size) for c in range(3)],axis=2)
    fixed=resize(protected.astype(np.float32),size)>.25;assert fixed.any() and (~fixed).any()
    field=coarse.copy();field[~fixed]=np.median(coarse[fixed],axis=0)
    yy,xx=np.mgrid[:height,:width];parity=(xx+yy)%2
    # Red/black SOR with a periodic azimuth and zero-flux ends. Visible colors
    # are Dirichlet constraints, so the hidden field meets their actual values.
    residual=None
    for iteration in range(a.iterations):
        maximum=0
        for color in [0,1]:
            average=(np.roll(field,1,1)+np.roll(field,-1,1)+np.r_[field[:1],field[:-1]]+np.r_[field[1:],field[-1:]])*.25
            active=(~fixed)&(parity==color);delta=1.65*(average-field)
            maximum=max(maximum,float(np.max(np.abs(delta[active]))));field[active]+=delta[active]
        if maximum<2e-5:break
    target=np.stack([resize(field[:,:,c],(old.shape[1],old.shape[0])) for c in range(3)],axis=2)+.8*fine
    expanded=protected.copy();distance=np.zeros(protected.shape,dtype=np.float32)
    for _ in range(a.feather):distance+=(~expanded)/a.feather;expanded=grow(expanded)
    weight=np.clip(distance,0,1);weight=weight*weight*(3-2*weight);weight[protected]=0
    result[sl]=old+(target-old)*weight[:,:,None];weightmap[sl]=weight
    record[name]={'grid':[width,height],'iterations':iteration+1,'last_update_max_log_rgb':maximum,
        'protected_texels':int(protected.sum()),'edited_texels':int((weight>0).sum())}
linear=np.exp(result);srgb=np.where(linear<=.0031308,linear*12.92,1.055*np.power(linear,1/2.4)-.055)
new=original.copy();new[:,:,:3]=np.uint8(np.rint(np.clip(srgb,0,1)*255));new[weightmap==0]=original[weightmap==0]
assert np.array_equal(new[weightmap==0],original[weightmap==0]);Image.fromarray(new).save(out/'albedo.png');np.save(out/'hidden-weight.npy',weightmap)
canvas=Image.new('RGB',(1024,550),'#171b21');d=ImageDraw.Draw(canvas)
for i,(label,value) in enumerate([('Previous atlas',original),('Boundary-matched hidden color',new)]):
    canvas.paste(Image.fromarray(value).convert('RGB').resize((512,512)),(i*512,38));d.text((i*512+8,12),label,fill='white')
canvas.save(out/'atlas-comparison.png')
report={'source':a.source,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'visibility':a.visibility,
    'visibility_sha256':hashlib.sha256((ROOT/a.visibility).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((out/'albedo.png').read_bytes()).hexdigest(),
    'protected_texels_exactly_preserved':True,'parameters':vars(a),'regions':record,
    'method':'Periodic harmonic continuation of broad log-linear pigment, constrained by visible boundary colors, retaining 80% of existing fine grain. Hidden interpretation, not recovered artwork. Actual BSDF rendering and fixed-view validation still required.'}
(out/'extension.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

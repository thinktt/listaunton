"""Continue the fitted walnut across unseen surfaces with reflected UV samples.

Visibility is authoring data only. The result is a fixed material atlas, never
a camera-dependent shader. Repeated/mirrored grain is an artistic completion.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
from derive_wood import ROOT,linear,display,sample,ramp
from lathe_projection import visible_tiles

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def nearest_seeds(valid):
    # Jump flooding on a small periodic cylinder; deterministic and dependency-free.
    h,w=valid.shape;yy,xx=np.indices((h,w),dtype=np.float32)
    sx=np.where(valid,xx,-1);sy=np.where(valid,yy,-1)
    best=np.where(valid,0,np.inf)
    for step in (256,128,64,32,16,8,4,2,1,1):
        for dx,dy in ((-step,-step),(0,-step),(step,-step),(-step,0),(step,0),(-step,step),(0,step),(step,step)):
            qx=np.roll(sx,(dy,dx),(0,1));qy=np.roll(sy,(dy,dx),(0,1))
            delta=np.abs(qx-xx);delta=np.minimum(delta,w-delta)
            d=delta*delta+(qy-yy)**2
            allowed=(qx>=0)&(qy>=0)
            if dy>0:allowed[:dy]=False
            if dy<0:allowed[dy:]=False
            choose=allowed&(d<best)
            sx=np.where(choose,qx,sx);sy=np.where(choose,qy,sy);best=np.where(choose,d,best)
    assert (sx>=0).all()
    return sx,sy,np.sqrt(best)

def run(cfg):
    out=ROOT/cfg['output'];out.mkdir(parents=True,exist_ok=True)
    src=ROOT/cfg['pigment'];assert sha(src)==cfg['pigment_sha256']
    color=np.asarray(Image.open(src).convert('RGB'));size=len(color)
    measurement=ROOT/cfg['measurement']
    meridian=np.load(measurement/'meridian.npy');depth=np.load(measurement/'depth.npy')[:,:,0]
    cam=json.loads((ROOT/'assets/pawn/camera.json').read_text())
    cov=np.zeros((size,size),np.float32)
    for rows,x,y,z,px,py,w in visible_tiles(meridian,depth,cam,size):cov[rows]=w
    mask=Image.fromarray(np.uint8(cov>.985)*255)
    if cfg.get('peel_pixels',0):mask=mask.filter(ImageFilter.MinFilter(2*cfg['peel_pixels']+1))
    small=512
    valid=np.asarray(mask.resize((small,small),Image.Resampling.BOX))>250
    sx,sy,dist=nearest_seeds(valid)
    def up(a):return np.asarray(Image.fromarray(a.astype(np.float32),'F').resize((size,size),Image.Resampling.BILINEAR))
    yy,xx=np.indices((size,size),dtype=np.float32)
    # Interpolate displacement rather than coordinates across the cylinder seam.
    y0,x0=np.indices((small,small),dtype=np.float32)
    du=(sx-x0+small/2)%small-small/2
    dx=up(du)*(size/small);dy=up(sy-y0)*(size/small)
    length=np.maximum(np.hypot(dx,dy),1)
    extension=np.minimum(length,cfg.get('reflection_cap',180))/length
    qx=(xx+dx+dx*extension*cfg.get('reflection_scale',.8))%size
    qy=np.clip(yy+dy+dy*extension*cfg.get('reflection_scale',.8),0,size-1.0001)
    retain=np.asarray(mask,np.float32)/255
    blend=ramp(up(dist)*(size/small),0,cfg.get('blend_pixels',40))*(1-retain)
    def convert(arr,encoding):
        a=arr.astype(np.float32)/255
        return linear(a) if encoding=='sRGB' else a
    results={}
    for key,spec in cfg['maps'].items():
        p=ROOT/spec['source'];assert sha(p)==spec['sha256']
        prior=np.asarray(Image.open(p).convert('RGB'));a=convert(prior,spec['encoding'])
        target=sample(a,qx.astype(np.float64),qy.astype(np.float64))
        if spec.get('neutral') is not None:target[:]=np.array(spec['neutral'],np.float32)/255
        # Long-distance repetition is deliberately bounded; the front retains
        # its measured pattern, the unknown side receives adjacent real grain.
        new=a*(1-blend[:,:,None])+target*blend[:,:,None]
        if spec['encoding']=='sRGB':new=display(new)
        encoded=np.uint8(np.rint(np.clip(new,0,1)*255));encoded[retain==1]=prior[retain==1]
        destination=out/(key+'.png');Image.fromarray(encoded).save(destination)
        results[key]={'path':destination.relative_to(ROOT).as_posix(),'sha256':sha(destination),
            'changed_fraction':float(np.any(encoded!=prior,2).mean()),'protected_changed':int(np.any(encoded[retain==1]!=prior[retain==1],1).sum())}
    Image.fromarray(np.uint8(blend*255)).save(out/'completion-weight.png')
    (out/'completion.json').write_text(json.dumps({'config':cfg,'results':results},indent=2)+'\n')
    print(json.dumps(results))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path)
    a=p.parse_args();run(json.loads(a.config.read_text()))

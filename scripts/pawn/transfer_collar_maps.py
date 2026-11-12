"""Re-register existing collar maps on changed geometry, leaving other texels exact.

This transfers material fields, not the photograph or shaded beauty image.
Newly visible underside keeps its existing wood; an old stem hit cannot supply
collar pigment. Existing unseen/backside texture is preserved.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from derive_wood import ROOT,sample,ramp,linear,display
from lathe_projection import visible_tiles

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run(cfg):
    folder=ROOT/cfg['measurement'];record=json.loads((folder/'measurement.json').read_text())
    old=np.load(folder/'old.npy');newdepth=np.load(folder/'new.npy')[:,:,0]
    profile=np.load(folder/'new-meridian.npy');previous=np.load(ROOT/cfg['old_meridian'])
    assert sha(ROOT/cfg['old_meridian'])==cfg['old_meridian_sha256']
    camera=json.loads((ROOT/'assets/pawn/camera.json').read_text())
    matrix=np.array(camera['projectionMatrix']).reshape(4,4)@np.array(camera['worldToCamera']).reshape(4,4)
    results={}
    for item in cfg['maps']:
        src=ROOT/item['source'];assert sha(src)==item['source_sha256']
        pixels=np.asarray(Image.open(src).convert('RGB'));result=pixels.copy();size=len(pixels)
        assert pixels.shape==(size,size,3)
        values=pixels.astype(float)/255
        if item.get('srgb'):values=linear(values)
        total=0.;largest=0.
        for rows,x,y,z,px,py,visible in visible_tiles(profile,newdepth,camera,size):
            uvz=sample(old,px,py);v=1-(rows+.5)/size
            oldr=np.interp(v,previous[:,0],previous[:,1])[:,None]
            oldz=np.interp(v,previous[:,0],previous[:,2])[:,None]
            r=np.hypot(x,y);ox=x*oldr/np.maximum(r,1e-9);oy=y*oldr/np.maximum(r,1e-9)
            opx=(matrix[0,0]*ox+matrix[0,1]*oy+matrix[0,2]*oldz+matrix[0,3]+1)*camera['width']/2-.5
            opy=(1-matrix[1,0]*ox-matrix[1,1]*oy-matrix[1,2]*oldz-matrix[1,3])*camera['height']/2-.5
            shift=np.hypot(px-opx,py-opy)
            weight=visible*ramp(shift,.1,.5)*ramp(uvz[:,:,3],.99,1)
            weight*=ramp(z,1.73,1.77)*(1-ramp(z,1.93,1.96))
            weight*=ramp(uvz[:,:,2],1.77,1.80)*(1-ramp(uvz[:,:,2],1.93,1.96))
            weight*=cfg.get('strength',1)
            transferred=sample(values,uvz[:,:,0]*size-.5,(1-uvz[:,:,1])*size-.5)
            mixed=values[rows]*(1-weight[:,:,None])+transferred*weight[:,:,None]
            if item.get('srgb'):mixed=display(mixed)
            encoded=np.uint8(np.rint(np.clip(mixed,0,1)*255))
            encoded[weight==0]=pixels[rows][weight==0]
            result[rows]=encoded;total+=float(weight.sum());largest=max(largest,float(shift.max()))
        out=ROOT/item['output'];out.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(result).save(out)
        results[item['name']]={'output':item['output'],'sha256':sha(out),'changed_fraction':float(np.mean(np.any(result!=pixels,axis=2))),
            'mean_transfer_weight':total/size**2,'maximum_projection_displacement_pixels':largest}
    report={'config':cfg,'coordinate_capture':record,'results':results,
        'note':'Only old collar material is transferred where the changed surface is visible. No image brightness, light or reference pixels are fitted.'}
    (ROOT/cfg['record']).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args()
    run(json.loads(a.config.read_text(encoding='utf8')))

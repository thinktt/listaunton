"""Bake continuous object-space walnut and a soft reference-detail constraint.

Ordinary static UV maps: appearance never depends on the viewing camera.
The original camera is used only to retain the observed grain during authoring.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from derive_wood import ROOT,linear,display,sample,ramp,blur

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(cfg):
    out=ROOT/cfg['output'];out.mkdir(parents=True,exist_ok=True)
    tilepath=ROOT/cfg['tile'];assert sha(tilepath)==cfg['tile_sha256']
    tile=linear(np.asarray(Image.open(tilepath).convert('RGB'),np.float32)/255)
    tile_med=np.median(tile[::3,::3].reshape(-1,3),axis=0)
    maps={}
    for key,spec in cfg['maps'].items():
        path=ROOT/spec['source'];assert sha(path)==spec['sha256']
        raw=np.asarray(Image.open(path).convert('RGB'),np.float32)/255
        maps[key]=linear(raw) if spec['encoding']=='sRGB' else raw
    prior=maps['pigment'];size=len(prior)
    reliable=(prior[:,:,0]>.045)&(prior[:,:,0]<.26)
    median=np.median(prior[reliable],axis=0)
    measurement=ROOT/cfg['measurement'];profile=np.load(measurement/'meridian.npy');depth=np.load(measurement/'depth.npy')[:,:,0]
    camera=json.loads((ROOT/'assets/pawn/camera.json').read_text())
    view=np.array(camera['worldToCamera']).reshape(4,4)
    projection=np.array(camera['projectionMatrix']).reshape(4,4)@view
    theta=((np.arange(size)+.5)/size+.25)*2*np.pi
    cs,sn=np.cos(theta),np.sin(theta)
    wood=np.empty_like(prior);retain=np.zeros((size,size),np.float32);erase=np.zeros((size,size),np.float32)
    f=cfg.get('frequency',.65)
    def tiled(a,b):
        u=1-np.abs(a%2-1);v=1-np.abs(b%2-1)
        return sample(tile,u*(tile.shape[1]-1),v*(tile.shape[0]-1))
    for first in range(0,size,64):
        rows=np.arange(first,min(first+64,size));v=1-(rows+.5)/size
        r,z,nr,nz=[np.interp(v,profile[:,0],profile[:,i])[:,None] for i in (1,2,3,4)]
        x,y=r*cs,r*sn
        nx,ny=nr*cs,nr*sn
        wx,wy,wz=np.abs(nx)**4,np.abs(ny)**4,np.abs(nz)**4
        divisor=np.maximum(wx+wy+wz,1e-6)
        # Blend three actual planar projections by the geometric normal. This
        # avoids axial smearing at the ball poles, foot, and turned shoulders.
        a=tiled(.31+f*y,.17+f*z+np.zeros_like(y))
        b=tiled(.41+f*x,.27+f*z+np.zeros_like(x))
        c=tiled(.53+f*x,.37+f*y)
        field=(a*wx[:,:,None]+b*wy[:,:,None]+c*wz[:,:,None])/divisor[:,:,None]
        wood[rows]=field*median/tile_med
        project=lambda row:row[0]*x+row[1]*y+row[2]*z+row[3]
        px=(project(projection[0])+1)*camera['width']/2-.5
        py=(1-project(projection[1]))*camera['height']/2-.5
        dz=np.abs(sample(depth,px,py)+project(view[2]))
        facing=(nx*view[2,0]+ny*view[2,1]+nz*view[2,2])/np.maximum(np.hypot(nr,nz),.01)
        retain[rows]=(1-ramp(dz,*cfg.get('depth_range',[.003,.03])))*ramp(facing,*cfg['facing_range'])*cfg.get('reference_weight',1)
        for band in cfg.get('erase_height_bands',[]):
            a,b,c,d=band['height']
            erase[rows]=np.maximum(erase[rows],ramp(z,a,b)*(1-ramp(z,c,d))*band.get('strength',1))
    # Broad continuous transitions extend into the unreliable projected fringe.
    retain=np.clip(blur(retain,r=cfg.get('blend_radius',12),passes=2),0,1)
    generated={'pigment':wood,'relief':wood}
    fine=np.mean(wood/median,axis=2)
    generated['finish']=np.stack((np.clip(85/255+(fine-1)*.025,0,1),np.clip(108/255+(fine-1)*.02,0,1),np.ones_like(fine)),axis=2)
    generated['slopes']=np.broadcast_to(np.array([128,128,255])/255,wood.shape)
    results={}
    for key,prior_map in maps.items():
        weight=(retain*(1-erase))[:,:,None]
        new=prior_map*weight+generated[key]*(1-weight)
        if cfg['maps'][key]['encoding']=='sRGB':new=display(new)
        path=out/(key+'.png');Image.fromarray(np.uint8(np.rint(np.clip(new,0,1)*255))).save(path)
        results[key]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
    Image.fromarray(np.uint8(retain*255)).save(out/'reference-weight.png')
    report={'config':cfg,'results':results,'source_median_linear':median.tolist(),'generated_median_linear':tile_med.tolist(),
        'mean_reference_weight':float(retain.mean()),'method':'Static, normal-blended object-space texture with soft retained reference detail. Generated texture is an interpretation, not historical evidence.'}
    (out/'completion.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(results))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args();run(json.loads(a.config.read_text()))

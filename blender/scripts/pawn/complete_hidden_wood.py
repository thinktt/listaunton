"""Complete unseen walnut without editing conservatively protected reference texels.

This produces one ordinary static UV texture. Visibility is used at authoring
time only; there is no camera-dependent shading or image pasted over a render.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from derive_wood import ROOT, linear, display, sample, ramp, blur


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def complete(cfg):
    source=ROOT/cfg['source']; assert digest(source)==cfg['source_sha256']
    prior=np.asarray(Image.open(source).convert('RGB'))
    size=len(prior); assert prior.shape==(size,size,3)
    measure=ROOT/cfg['measurement']
    profile=np.load(measure/'meridian.npy');depth=np.load(measure/'depth.npy')[:,:,0]
    camera=json.loads((ROOT/'assets/pawn/camera.json').read_text())
    view=np.array(camera['worldToCamera']).reshape(4,4)
    projection=np.array(camera['projectionMatrix']).reshape(4,4)@view
    theta=((np.arange(size)+.5)/size+.25)*2*np.pi
    cs,sn=np.cos(theta),np.sin(theta)
    protected=np.zeros((size,size),bool); coverage=np.zeros((size,size),np.float32)
    hidden=np.empty((size,size,3),np.float32)
    tile=linear(np.asarray(Image.open(ROOT/'assets/queen/walnut-fine-albedo.png').convert('RGB'),np.float32)/255)
    if cfg.get('grain_patch'):
        x0,y0,x1,y1=cfg['grain_patch']
        tile=linear(prior[y0:y1,x0:x1].astype(np.float32)/255)
        low=blur(tile,r=20,passes=3)
        tile=np.clip(tile/np.maximum(low,.0001),.35,2.8)
    tile_median=np.median(tile[::4,::4].reshape(-1,3),axis=0)
    for first in range(0,size,64):
        rows=np.arange(first,min(first+64,size));v=1-(rows+.5)/size
        r,z,nr,nz=[np.interp(v,profile[:,0],profile[:,i])[:,None] for i in (1,2,3,4)]
        x,y=r*cs,r*sn
        project=lambda row:row[0]*x+row[1]*y+row[2]*z+row[3]
        px=(project(projection[0])+1)*camera['width']/2-.5
        py=(1-project(projection[1]))*camera['height']/2-.5
        dz=np.abs(sample(depth,px,py)+project(view[2]))
        facing=(nr*cs*view[2,0]+nr*sn*view[2,1]+nz*view[2,2])/np.maximum(np.hypot(nr,nz),.01)
        protected[rows]=(dz<cfg.get('protect_depth',.065))&(facing>cfg.get('protect_facing',-.10))
        coverage[rows]=(1-ramp(dz,.008,.035))*ramp(facing,.10,.50)
        frequency=cfg.get('grain_frequency',1)
        tx=1-np.abs((.45+frequency*(.63*x+.25*y))%2-1)
        ty=1-np.abs((.20+frequency*(.59*z+.12*y+.035*np.sin(7*x)))%2-1)
        hidden[rows]=sample(tile,tx*(tile.shape[1]-1),ty*(tile.shape[0]-1))/tile_median
    protected=np.asarray(Image.fromarray(protected.astype('uint8')*255).filter(ImageFilter.MaxFilter(9)))>0
    # A broad safety fringe starts at zero outside the hard protected region.
    mask_image=Image.fromarray((~protected).astype('uint8')*255)
    allowed=np.asarray(mask_image.filter(ImageFilter.GaussianBlur(cfg.get('blend_pixels',40))),np.float32)/255
    allowed=ramp(allowed,.52,.98)*(~protected)
    pigment=linear(prior.astype(np.float32)/255)
    valid=(coverage>.85)&(pigment[:,:,0]>.035)&(pigment[:,:,0]<.45)
    median=np.median(pigment[valid],axis=0)
    # Complete low-frequency log pigment as a screened harmonic field.
    # Matching boundary colors avoids a new outline at the protected fringe;
    # the mild screen gradually returns unknown areas to plausible walnut.
    small=256
    def resized(a):
        return np.asarray(Image.fromarray(a.astype(np.float32),'F').resize((small,small),Image.Resampling.BOX))
    fixed=resized(protected.astype(np.float32))>.05
    low=np.stack([resized(np.log(np.maximum(pigment[:,:,c],.0001))) for c in range(3)],2)
    log_target=np.log(median)[None,None,:]
    field=low.copy();screen=cfg.get('screen',.007)
    for _ in range(cfg.get('iterations',1800)):
        up=np.concatenate((field[:1],field[:-1]));down=np.concatenate((field[1:],field[-1:]))
        neighbor=(up+down+np.roll(field,1,1)+np.roll(field,-1,1))*.25
        field=np.where(fixed[:,:,None],low,(neighbor+screen*log_target)/(1+screen))
    smooth=np.stack([np.asarray(Image.fromarray(field[:,:,c],'F').resize((size,size),Image.Resampling.BICUBIC)) for c in range(3)],2)
    # Unseen fine grain follows the continuous object-space walnut field.
    detail=np.clip(hidden,.25,3)**cfg.get('grain_strength',.75)
    completed=np.exp(smooth)*detail
    output=display(pigment*(1-allowed[:,:,None])+completed*allowed[:,:,None])
    output=np.uint8(np.rint(np.clip(output,0,1)*255));output[protected]=prior[protected]
    out=ROOT/cfg['output'];out.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(output).save(out)
    if cfg.get('bump_source'):
        bump_path=ROOT/cfg['bump_source'];assert digest(bump_path)==cfg['bump_source_sha256']
        bump=np.asarray(Image.open(bump_path).convert('RGB'));assert bump.shape==prior.shape
        # Same fine wood structures in pigment and physical bump on unknown
        # surfaces. The protected reference relief stays byte-identical.
        mix=display(linear(bump.astype(np.float32)/255)*(1-allowed[:,:,None])+completed*allowed[:,:,None])
        new_bump=np.uint8(np.rint(np.clip(mix,0,1)*255));new_bump[protected]=bump[protected]
        Image.fromarray(new_bump).save(out.parent/'bump-completed.png')
    folder=out.parent
    Image.fromarray(np.uint8(allowed*255)).save(folder/'completion-weight.png')
    Image.fromarray(np.uint8(coverage*255)).save(folder/'reference-coverage.png')
    report={'config':cfg,'median_linear_pigment':median.tolist(),'protected_fraction':float(protected.mean()),
        'changed_fraction':float(np.any(output!=prior,2).mean()),'protected_changed_texels':int(np.any(output[protected]!=prior[protected],1).sum()),
        'sha256':digest(out),'maximum_display_change':int(np.abs(output.astype(int)-prior.astype(int)).max())}
    (folder/'completion.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('config',type=Path);a=parser.parse_args()
    complete(json.loads(a.config.read_text(encoding='utf8')))

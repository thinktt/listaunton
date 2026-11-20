"""Carry fine cheek grain through the actual eye islands in the inherited walnut atlas."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
D=Path(__file__).resolve().parent;AX=np.array([1.,-.76])/np.hypot(1.,.76);UP=np.array([-AX[1],AX[0]])
def chart(a):
    xz=a[..., [0,2]]-[.412,4.158];return np.stack((xz@AX,xz@UP),axis=-1)
def raster(t,w,h):
    low=np.maximum(np.floor(t.min(0)).astype(int),[0,0]);high=np.minimum(np.ceil(t.max(0)).astype(int),[w-1,h-1])
    if (high<low).any():return None
    yy,xx=np.mgrid[low[1]:high[1]+1,low[0]:high[0]+1];q=np.stack((xx+.5,yy+.5),-1)-t[0]
    a=t[1]-t[0];b=t[2]-t[0];det=a[0]*b[1]-a[1]*b[0]
    if abs(det)<1e-8:return None
    u=(q[...,0]*b[1]-q[...,1]*b[0])/det;v=(q[...,1]*a[0]-q[...,0]*a[1])/det
    on=(u>=-.0001)&(v>=-.0001)&((u+v)<=1.0001)
    if not on.any():return None
    return yy[on],xx[on],np.stack((1-u[on]-v[on],u[on],v[on]),-1)
def resample(a,x,y):
    x=np.clip(x,0,a.shape[1]-1.01);y=np.clip(y,0,a.shape[0]-1.01)
    ix=x.astype(int);iy=y.astype(int);u=(x-ix)[...,None];v=(y-iy)[...,None]
    return (1-u)*(1-v)*a[iy,ix]+u*(1-v)*a[iy,ix+1]+(1-u)*v*a[iy+1,ix]+u*v*a[iy+1,ix+1]
def main():
    src=np.array(Image.open(D/'parent-pigment.png').convert('RGB'))
    W=src.shape[1];H=src.shape[0];allp=np.load(D/'atlas-parts.npz')
    co=allp['continuous_horse_head_and_neck_pts'];tex=allp['continuous_horse_head_and_neck_UV']
    xy=chart(co);low=np.array([-.44,-.51]);grid=.0022;w,h=388,220
    screen=(xy-low)/grid
    hit=(co[:,:,1].max(1)<-.15)&(screen[:,:,0].max(1)>=0)&(screen[:,:,0].min(1)<w)&(screen[:,:,1].max(1)>=0)&(screen[:,:,1].min(1)<h)
    surf=np.zeros((h,w,3));depth=np.zeros((h,w))
    for t,tt,tri in zip(screen[hit],tex[hit],co[hit]):
        r=raster(t,w,h)
        if r is None:continue
        y,x,b=r;z=b@(-tri[:,1]);vis=z>depth[y,x]
        y,x,b,z=y[vis],x[vis],b[vis],z[vis]
        uv=b@tt;surf[y,x]=resample(src,uv[:,0]*W-.5,(1-uv[:,1])*H-.5);depth[y,x]=z
    source=Image.fromarray(np.uint8(np.clip(surf,0,255)))
    wide=np.asarray(source.filter(ImageFilter.GaussianBlur(9)),float)
    medium=np.asarray(source.filter(ImageFilter.GaussianBlur(2.25)),float)
    grain=np.clip((surf-medium)/np.maximum(wide,24),-.54,.54)+.58*np.clip((medium-wide)/np.maximum(wide,24),-.45,.45)
    np.savez_compressed(D/'fine-grain-field.npz',grain=(grain@np.array([.62,.32,.06])).astype(np.float32),low=low,step=grid)
    # The two eyes occupy dedicated islands. Restrict all changes to their
    # actual surface and two existing bleed texels so the surrounding atlas
    # remains byte-identical.
    box=(int(.568*W),int((1-.282)*H),int(.639*W),int((1-.228)*H));x0,y0,x1,y1=box
    ww=x1-x0;hh=y1-y0;field=np.zeros((hh,ww,2));side=np.zeros((hh,ww));valid=np.zeros((hh,ww),bool)
    for label,sign in [('near_eye',-1),('far_eye',1)]:
        coord=chart(allp[label+'_pts']);uv=allp[label+'_UV']*[W,-H]+[-x0,H-y0]
        for t,c in zip(uv,coord):
            r=raster(t,ww,hh)
            if r is None:continue
            y,x,b=r;field[y,x]=b@c;side[y,x]=sign;valid[y,x]=True
    eye=valid.copy();before=src[y0:y1,x0:x1].astype(float)
    for _ in range(2):
        exp=valid.copy()
        for dy,dx in [(0,1),(1,0),(0,-1),(-1,0)]:
            use=np.roll(valid,(dy,dx),(0,1))&~exp&(before.max(2)>10)
            field[use]=np.roll(field,(dy,dx),(0,1))[use];side[use]=np.roll(side,(dy,dx),(0,1))[use]
            exp|=use
        valid=exp
    u,v=field[:,:,0],field[:,:,1]
    # Read real high-frequency wood from the cheek below the eye, at the
    # same physical scale, and retain the darker overall stain of the eye.
    sx=(.92*u-.046-low[0]+.012*side)/grid;sy=(v-.302-low[1])/grid
    g=resample(grain,sx,sy)
    nose=1/(1+np.exp(-(u-.080)/.041))
    fine=g@np.array([.62,.32,.06])
    alpha=.96+.48*nose
    dest=before*(1.105+.10*nose[...,None])+[3.5,2.0,1.0]
    dest+=(.60*before+[24,17,11])*alpha[...,None]*fine[...,None]
    dest+=.15*(before+10)*g
    out=src.copy();tile=out[y0:y1,x0:x1];tile[valid]=np.uint8(np.clip(np.round(dest[valid]),0,255))
    Image.fromarray(out).save(D/'pigment.png',compress_level=5)
    source.save(D/'cheek-grain-source.png')
    diff=np.any(out!=src,2)
    report={'input_sha256':hashlib.sha256((D/'parent-pigment.png').read_bytes()).hexdigest(),
            'output_sha256':hashlib.sha256((D/'pigment.png').read_bytes()).hexdigest(),'texture_size':[W,H],
            'mapped_eye_pixels':int(eye.sum()),'changed_pixels':int(diff.sum()),'outside_selected_islands_and_bleed':int(np.any(tile!=before,axis=2)[~valid].sum()),
            'median_eye_parent_rgb':np.median(before[eye],axis=0).tolist(),'median_eye_candidate_rgb':np.median(tile[eye],axis=0).tolist()}
    (D/'eye-pigment.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()

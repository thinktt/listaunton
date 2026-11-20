"""Unwrap the existing mane over measured sections and map it back to its actual islands."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
D=Path(__file__).resolve().parent
MANE='swept rounded mane';W,H=960,920;Z0,Z1=1.76,4.73

def raster(t,w,h):
    lo=np.maximum(np.floor(t.min(0)).astype(int),0);hi=np.minimum(np.ceil(t.max(0)).astype(int),[w-1,h-1])
    if (hi<lo).any():return
    a,b=t[1]-t[0],t[2]-t[0];det=a[0]*b[1]-a[1]*b[0]
    if abs(det)<1.e-9:return
    y,x=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];qx=x+.5-t[0,0];qy=y+.5-t[0,1]
    u=(qx*b[1]-qy*b[0])/det;v=(a[0]*qy-a[1]*qx)/det
    valid=(u>=-1.e-6)&(v>=-1.e-6)&(u+v<=1.000001)
    if valid.any():return y[valid],x[valid],np.stack([1-u[valid]-v[valid],u[valid],v[valid]],1)

def sample(a,x,y,wrap=False):
    x=np.mod(x,a.shape[1]) if wrap else np.clip(x,0,a.shape[1]-1.0001)
    y=np.clip(y,0,a.shape[0]-1.0001);i=x.astype(int);j=y.astype(int)
    k=(i+1)%a.shape[1];s=(x-i)[...,None];t=(y-j)[...,None]
    return (1-t)*((1-s)*a[j,i]+s*a[j,k])+t*((1-s)*a[j+1,i]+s*a[j+1,k])

def centers(points,tri):
    zs=np.linspace(Z0-.01,Z1+.01,170);xyz=points[tri]
    out=[]
    for z in zs:
        selected=xyz[(xyz[:,:,2].min(1)<=z)&(xyz[:,:,2].max(1)>=z)]
        e1=selected.reshape(-1,3);e2=np.roll(selected,-1,axis=1).reshape(-1,3)
        visible=(e1[:,2]>z)!=(e2[:,2]>z)
        a,b=e1[visible],e2[visible];ratio=(z-a[:,2])/(b[:,2]-a[:,2])
        cross=a[:,:2]+(b[:,:2]-a[:,:2])*ratio[:,None]
        if not len(cross):out.append([-.90,-.05]);continue
        out.append((cross.max(0)+cross.min(0))/2.)
    return zs,np.array(out)

def main():
    d=np.load(D/'surfaces.npz');p=d['xyz'];tri=d['tri'];uv=d[MANE];atlas=np.array(Image.open(D/'parent-pigment.png').convert('RGB'))
    h,w=atlas.shape[:2];zs,m=centers(p,tri);cx,cy=[np.interp(p[:,2],zs,m[:,j]) for j in [0,1]]
    # Positive and negative angles follow the two actual flanks. The chart
    # has no seam on the round back; it joins in the buried anterior margin.
    t=np.arctan2(p[:,1]-cy,cx-p[:,0]);rad=np.hypot(p[:,1]-cy,p[:,0]-cx)
    chart=np.column_stack([(t/(2*np.pi)+.5)*W,(Z1-p[:,2])/(Z1-Z0)*H])
    q=chart[tri].copy()
    split=np.ptp(q[:,:,0],axis=1)>W/2
    q[split,:,0]+=np.where(q[split,:,0]<W/2,W,0)
    field=np.zeros((H,W,3));depth=np.zeros((H,W));xy=uv*[w,-h]+[0,h]
    for i in np.where((q[:,:,1].min(1)<H)&(q[:,:,1].max(1)>0))[0]:
        for xx in [0,-W] if split[i] else [0]:
            r=raster(q[i]+[xx,0],W,H)
            if r is None:continue
            y,x,b=r;dst=b@rad[tri[i]];keep=dst>depth[y,x]
            y,x,b,dst=y[keep],x[keep],b[keep],dst[keep];coords=b@xy[i]
            depth[y,x]=dst;field[y,x]=sample(atlas,coords[:,0]-.5,coords[:,1]-.5)
    # Resolve all texture-space samples on the active length of this part.
    address=np.full((h,w,2),np.nan,np.float32);hits=np.zeros((h,w),np.uint8)
    local=(q[:,:,1].min(1)<H)&(q[:,:,1].max(1)>0)
    for i in np.where(local)[0]:
        r=raster(xy[i],w,h)
        if r is None:continue
        y,x,b=r;co=b@q[i];good=(co[:,1]>0)&(co[:,1]<H)
        y,x,co=y[good],x[good],co[good]
        address[y,x]=co;hits[y,x]+=1
    protected=Image.new('L',(w,h));pen=ImageDraw.Draw(protected)
    for key in d.files:
        if key in [MANE,'xyz','tri']:continue
        for face in d[key]*[w,-h]+[0,h]:
            pen.polygon(list(map(tuple,face)),fill=255)
    other=np.asarray(protected.filter(ImageFilter.MaxFilter(5)))>0
    available=np.isfinite(address[:,:,0])&~other
    y,x=np.nonzero(available);xy_chart=address[y,x]
    np.savez_compressed(D/'surface-field.npz',rgb=field.astype(np.float32),depth=depth.astype(np.float32),
        atlas_y=y.astype(np.uint16),atlas_x=x.astype(np.uint16),chart=xy_chart,protected=np.packbits(other.ravel()))
    Image.fromarray(np.uint8(np.clip(field,0,255))).save(D/'inherited-surface.png')
    print('Coverage',np.mean(depth>0),'atlas samples',len(x),'overlap',int((hits[available]>1).sum()),'protected',int((other&np.isfinite(address[:,:,0])).sum()))
if __name__=='__main__':main()

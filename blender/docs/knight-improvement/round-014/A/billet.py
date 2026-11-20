"""Bake a continuous three-dimensional, ring-porous walnut billet into existing mane UVs."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from join import join_chart_edges
D=Path(__file__).resolve().parent
def ease(a,b,x):
    q=np.clip((x-a)/(b-a),0,1)
    return q*q*(3-2*q)
def raster(t,n):
    lo=np.maximum(np.floor(t.min(0)).astype(int),0);hi=np.minimum(np.ceil(t.max(0)).astype(int),n-1)
    yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
    a,b=t[1]-t[0],t[2]-t[0];det=a[0]*b[1]-a[1]*b[0]
    if abs(det)<1e-8:return
    dx,dy=xx+.5-t[0,0],yy+.5-t[0,1]
    u=(dx*b[1]-dy*b[0])/det;v=(a[0]*dy-a[1]*dx)/det
    keep=(u>=0)&(v>=0)&(u+v<=1)
    if keep.any():return yy[keep],xx[keep],np.stack([1-u[keep]-v[keep],u[keep],v[keep]],1)
def prepare():
    bundle=np.load(D/'native-uv.npz');N=Image.open(D/'parent-pigment.png').width
    im=Image.new('L',(N,N));draw=ImageDraw.Draw(im)
    pix=lambda uv:uv*[N,-N]+[0,N]
    for tri in pix(bundle['reserved']):draw.polygon([tuple(v) for v in tri],fill=255)
    reserved=np.asarray(im.filter(ImageFilter.MaxFilter(5)))>0
    coord=np.zeros((N,N,3),np.float32);occupied=np.zeros((N,N),bool)
    collision=0
    for t,q in zip(pix(bundle['uv']),bundle['xyz']):
        sample=raster(t,N)
        if sample is None:continue
        y,x,bc=sample;v=bc@q
        collision+=np.count_nonzero(occupied[y,x]&(np.linalg.norm(coord[y,x]-v,axis=1)>.012))
        coord[y,x]=v;occupied[y,x]=True
    native_count=occupied.sum()
    # Copy native coordinates only three texels into empty map gutters to support bilinear/mip filtering.
    for _ in range(3):
        grown=occupied.copy()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            new=np.roll(occupied,(dy,dx),(0,1)) & ~grown
            coord[new]=np.roll(coord,(dy,dx),(0,1))[new];grown|=new
        occupied=grown
    restricted=occupied&reserved;allowed=occupied&~reserved;ys,xs=np.where(allowed)
    np.savez_compressed(D/'mane-samples.npz',y=ys.astype(np.uint16),x=xs.astype(np.uint16),xyz=coord[allowed])
    return {'mane_native_texels':int(native_count),'native_overlapping_distinct_points':int(collision),
            'padding_radius_texels':3,'all_mane_texels_including_padding':int(occupied.sum()),
            'reserved_texels_excluded':int(restricted.sum()),'writable_mane_texels':int(allowed.sum())}
# A deterministic nonperiodic hash, quorum of eight corners interpolated in 3D.
def hash3(i,j,k,seed):
    u=(i.astype(np.uint32)*np.uint32(0x8da6b343)) ^ (j.astype(np.uint32)*np.uint32(0xd8163841)) ^ (k.astype(np.uint32)*np.uint32(0xcb1ab31f)) ^ np.uint32(seed*31991)
    u=(u^(u>>16))*np.uint32(0x7feb352d);u=(u^(u>>15))*np.uint32(0x846ca68b)
    return ((u^(u>>16)).astype(np.float64)/4294967296.0)*2-1
def noise(x,y,z,seed):
    i,j,k=[np.floor(a).astype(np.int32) for a in (x,y,z)]
    fx,fy,fz=[ease(0,1,a-b) for a,b in zip((x,y,z),(i,j,k))]
    result=0.
    for dz in (0,1):
        for dy in (0,1):
            for dx in (0,1):
                result+=hash3(i+dx,j+dy,k+dz,seed)*(fx if dx else 1-fx)*(fy if dy else 1-fy)*(fz if dz else 1-fz)
    return result
def wood(q,brightness):
    x,y,z=q.T.astype(np.float64)
    # Fibers run along the sawn length, with an irregular grain slope and a pith outside the carving.
    l=x+.075*z
    yy=y+5.20+.042*x+.020*np.sin(z*1.15+x*.77)
    zz=z+1.18-.075*x+.032*np.sin(x*1.7+y*.54)
    r=np.hypot(yy,zz);t=(np.arctan2(zz,yy)-.72)*7.
    wander=.018*noise(l*1.6,t*2,r*1.8,11)+.006*noise(l*4,t*4,r*4,12)
    r+=wander;t+=.009*np.sin(l*5+r*2)
    # Unequal growth increments, a muted latewood boundary, then pore chains with finite length.
    ring=r/.082+.23*np.sin(r*9.73)+.30*noise(l*1.8,t*2.2,r*3.5,41)
    boundary=np.exp(-((np.minimum(ring%1,1-ring%1))/.158)**2)
    small=noise(l*12,t*58,r*85,31);med=noise(l*5.8,t*23,r*34,32)
    fine=noise(l*26,t*136,r*178,33)
    rays=noise(l*7,t*96,r*11,34)
    vessels=ease(.11,.72,.49*small+.36*med+.15*fine)
    broad=noise(l*1.7,t*4.3,r*5.6,35)
    cross=noise(l*3.9,t*10.3,r*15.8,36)
    mottling=noise(l*12.7,t*38,r*54,38)
    barrel=noise(l*20,t*82,r*104,39)
    base=brightness+.116*broad+.107*cross+.158*med+.144*small+.11*fine+.035*rays
    base+=.210*mottling+.172*barrel
    # Longitudinal variation toward darker heartwood in this region of the billet.
    base+=.016-.135*ease(-1.37,-.86,x)
    base-=.049*(boundary-.27)+.34*(vessels-.095)
    return np.stack([96.0*base+3.1*broad+2*cross,50.5*base+.8*broad,23.1*base-.65*broad],axis=1)
def bake(brightness):
    file=D/'chart.json'
    if not (D/'mane-samples.npz').exists():file.write_text(json.dumps(prepare(),indent=2)+'\n')
    trace=np.load(D/'mane-samples.npz');y,x,xyz=[trace[k] for k in ('y','x','xyz')]
    src=np.array(Image.open(D/'parent-pigment.png').convert('RGB'));out=src.copy()
    for first in range(0,len(x),150000):
        sl=slice(first,first+150000);q=xyz[sl];z=q[:,2]
        w=ease(1.82,2.37,z)*(1-ease(4.31,4.76,z));rows,cols=y[sl],x[sl]
        rgb=src[rows,cols];new=wood(q,brightness)
        out[rows,cols]=np.uint8(np.rint(np.clip(rgb+(new-rgb)*w[:,None],0,255)))
    geom=np.load(D/'native-uv.npz')
    joins=join_chart_edges(out,x,y,geom['uv'],geom['xyz'])
    changed=np.any(src!=out,2);Image.fromarray(out).save(D/'pigment.png',compress_level=5)
    manifest={'model_units':'Model-rest XYZ sampled continuously on the fixed mesh. Camera and lighting do not enter the field.',
              'height_blend':[1.82,2.37,4.31,4.76],'brightness':brightness,'changed_texels':int(changed.sum()),'chart_edge_filter':joins,
              'changed_texels_beyond_mane_chart_and_gutter':int(changed.sum()-changed[y,x].sum()),
              'protected_atlas_sha256':hashlib.sha256((D/'parent-pigment.png').read_bytes()).hexdigest(),
              'atlas_sha256':hashlib.sha256((D/'pigment.png').read_bytes()).hexdigest()}
    (D/'billet.json').write_text(json.dumps(manifest,indent=2)+'\n');print(manifest,flush=True)
if __name__=='__main__':bake(float(sys.argv[1]) if len(sys.argv)>1 else 1.02)

"""Restore the missing fine walnut modulation on the all-around turned base."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

SOURCE = None
REFERENCE = None

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ease(a, low, high):
    t = np.clip((a-low)/(high-low), 0, 1)
    return t*t*(3-2*t)

def gaussian(field, sigma):
    # Float convolution keeps the very small variations in dark walnut.
    margin = max(1, int(np.ceil(sigma*3)))
    offsets = np.arange(-margin, margin+1)
    kernel = np.exp(-.5*(offsets/sigma)**2)
    kernel /= kernel.sum()
    out = field
    for axis in [0, 1]:
        axis_first = np.moveaxis(out, axis, 0)
        pads = [(margin,margin)] + [(0,0)]*(axis_first.ndim-1)
        padded = np.pad(axis_first, pads, mode='reflect')
        smooth = np.zeros_like(axis_first)
        for i, k in enumerate(kernel):
            smooth += padded[i:i+len(axis_first)]*k
        out = np.moveaxis(smooth, 0, axis)
    return out

def sample(field, x, y):
    x = np.clip(x, 0, field.shape[1]-1.001)
    y = np.clip(y, 0, field.shape[0]-1.001)
    ix, iy = x.astype(int), y.astype(int)
    ax, ay = x-ix, y-iy
    return ((1-ay)*((1-ax)*field[iy,ix]+ax*field[iy,ix+1])+
            ay*((1-ax)*field[iy+1,ix]+ax*field[iy+1,ix+1]))

def band_detail(rgb, fine):
    # Nearly neutral varnish vanishes in red-minus-blue. A quiet luminance term
    # preserves low-saturation pores while chroma does most of the work.
    chroma = np.maximum(rgb[:,:,0] - rgb[:,:,2], 0)
    value = np.log(chroma + 14)*.82 + np.log(rgb @ np.array([.3,.58,.12],dtype='f') + 18)*.18
    clean = gaussian(value,.45)
    broad = gaussian(value,8.)
    field = clean - broad
    if fine:
        middle=gaussian(value,2.1)
        field=1.20*(gaussian(value,.32)-middle)+.61*(middle-broad)
    dy, dx = np.gradient(broad)
    weight = 1-ease(np.hypot(dy,dx),.018,.063)
    weight *= ease(chroma, 9, 37)
    return field, weight

def raster(verts, faces, width, height):
    points = verts[faces,:2]
    lo = np.maximum(np.ceil(points.min(1)).astype(int), [0,0])
    hi = np.minimum(np.floor(points.max(1)).astype(int), [width-1,height-1])
    dim = hi - lo + 1
    valid = (dim>0).all(1)
    bounds = np.ceil(np.log2(np.maximum(1, dim))).astype(int)
    groups = bounds[:,0] * 32 + bounds[:,1]
    for group in np.unique(groups[valid]):
        group_ids = np.flatnonzero(valid & (groups==group))
        spans = dim[group_ids].max(0)
        fy, fx = np.indices(spans[::-1])
        fx,fy = fx.ravel(),fy.ravel()
        chunk = max(1, min(2048, 130000 // len(fx)))
        for start in range(0,len(group_ids),chunk):
            ids = group_ids[start:start+chunk]
            xy = points[ids]; basis1 = xy[:,1]-xy[:,0]; basis2=xy[:,2]-xy[:,0]
            det = basis1[:,0]*basis2[:,1]-basis1[:,1]*basis2[:,0]
            safe = np.where(abs(det)>1e-10,det,1)
            x = lo[ids,0,None] + fx; y = lo[ids,1,None] + fy
            dx=x-xy[:,0,0,None];dy=y-xy[:,0,1,None]
            u=(dx*basis2[:,1,None]-dy*basis2[:,0,None])/safe[:,None]
            v=(dy*basis1[:,0,None]-dx*basis1[:,1,None])/safe[:,None]
            ii,jj=np.where((u>=0)&(v>=0)&(u+v<=1)&(abs(det[:,None])>1e-10)&
                           (x<=hi[ids,0,None])&(y<=hi[ids,1,None]))
            if len(ii):
                yield ids[ii], x[ii,jj], y[ii,jj], u[ii,jj], v[ii,jj]

def lerp_tri(data,faces,ids,u,v):
    block=data[faces[ids]]
    if block.ndim==3:
        u,v=u[:,None],v[:,None]
    return block[:,0]+u*(block[:,1]-block[:,0])+v*(block[:,2]-block[:,0])

def pigment_field(fine):
    meta=json.loads((SOURCE/'mesh.json').read_bytes())
    raw=(SOURCE/'mesh.bin').read_bytes()
    verts=np.frombuffer(raw,'<f4',count=meta['vertexCount']*8).reshape(-1,8)
    faces=np.frombuffer(raw,'<u4',offset=meta['indexByteOffset']).reshape(-1,3)
    camera=meta['referenceCamera'];w=camera['width'];h=camera['height']
    view=np.reshape(camera['worldToCamera'],(4,4));proj=np.reshape(camera['projectionMatrix'],(4,4))
    view_pos=verts[:,:3]@view[:3,:3].T+view[:3,3]
    ndc=view_pos@proj[:3,:3].T+proj[:3,3]
    sensor=np.column_stack(((1+ndc[:,0])*w/2-.5,(1-ndc[:,1])*h/2-.5,-view_pos[:,2]))
    depth=np.full((h,w),1.e6,dtype='f')
    for ids,x,y,u,v in raster(sensor,faces,w,h):
        np.minimum.at(depth,(y,x),lerp_tri(sensor[:,2],faces,ids,u,v))
    target=np.asarray(Image.open(REFERENCE).convert('RGB'),dtype='f')
    source=np.asarray(Image.open(SOURCE/'wood.png').convert('RGB'),dtype='f')
    desired,des_conf=band_detail(target,fine)
    present,cur_conf=band_detail(source,fine)
    # Wide shade and bright grooves are intentionally excluded from both fields.
    ref_delta=np.clip(desired-.80*present,-.38,.38)
    tile=desired[888:963,350:604]
    cap=np.percentile(abs(tile),98)
    tile=np.clip(tile-np.median(tile),-cap,cap)
    tile=np.concatenate([tile,tile[:,::-1]],axis=1)
    tile=np.concatenate([tile,tile[::-1,:]],axis=0)
    part=next(p for p in meta['parts'] if p['name'].endswith('turned pedestal'))
    pf=faces[part['indexOffset']//3:(part['indexOffset']+part['indexCount'])//3]
    xyz=verts[pf,:3].reshape(-1,3)
    cx,cy=(xyz.max(0)[:2]+xyz.min(0)[:2])*.5
    old=np.asarray(Image.open(SOURCE/'pigment.png').convert('RGB'))
    ht,wd=old.shape[:2];uv=verts[:,6:8]*[wd,-ht]+[-.5,ht-.5]
    facing=verts[:,3:6]@view[2,:3]
    gain=np.zeros((ht,wd),dtype='f');inside=np.zeros((ht,wd),bool)
    measured=np.zeros((ht,wd),dtype='f')
    material_conf=np.minimum(des_conf,cur_conf)
    for ids,x,y,u,v in raster(uv,pf,wd,ht):
        world=lerp_tri(verts[:,:3],pf,ids,u,v)
        angle=np.arctan2(world[:,1]-cy,world[:,0]-cx)
        z=world[:,2]
        # Complete integer revolutions and periodic warp give a continuous field
        # through the rear seam. All UV islands sample the same physical turning.
        s=3*tile.shape[1]*angle/(2*np.pi)+14*np.sin(2*angle+.8*z)+7*np.sin(5*angle+1.9*z)
        t=198*z+11*np.sin(2*angle+.9*z)+5*np.sin(4*angle-.7*z)
        all_around=(.81*sample(tile,s%tile.shape[1],t%tile.shape[0])+
                    .30*sample(tile,(s+97+3*np.cos(angle))%tile.shape[1],
                               (t+49+5*np.cos(3*angle))%tile.shape[0]))
        # Use only visible midtone material, far from a large illumination gradient
        # or another surface. The continuous field carries all hidden surfaces.
        px,py,pz=lerp_tri(sensor,pf,ids,u,v).T
        vis=1-ease(abs(sample(depth,px,py)-pz),.009,.032)
        vis*=ease(lerp_tri(facing,pf,ids,u,v),.12,.5)
        vis*=sample(material_conf,px,py)
        vis*=1-ease(z,1.20,1.44)
        grain=vis*sample(ref_delta,px,py)+(1-vis)*all_around*(.58 if fine else .72)
        gain[y,x]=np.clip(grain,-.34,.30)
        measured[y,x]=vis;inside[y,x]=True
    return gain,inside,measured

def main():
    import subprocess
    import tempfile
    import shutil
    global SOURCE,REFERENCE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path.cwd(),help='Checkout containing the 008 parent commit')
    parser.add_argument('--assets',type=Path,help='Alternatively use extracted assets/knight from 39a1219')
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--chest',type=Path,help='Optionally combine the independently reconstructed 044 chest atlas')
    args=parser.parse_args()
    here=Path(__file__).resolve().parent
    record=json.loads((here/'inputs.json').read_bytes())
    args.out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='knight-pedestal-') as temporary:
        SOURCE=Path(temporary)
        for local,committed in [('mesh.bin','mesh.bin'),('ref.png','ref.png'),('pigment.png','wood-atlas-mission-008.png')]:
            if args.assets:
                data=(args.assets/committed).read_bytes()
            else:
                data=subprocess.check_output(['git','-C',str(args.repo),'show','39a1219:assets/knight/'+committed])
            (SOURCE/local).write_bytes(data)
            assert sha(SOURCE/local)==record['inputs'][local],local
        for local,stored in [('wood.png','fixed-source.png'),('mesh.json','source-mesh.json')]:
            shutil.copyfile(here/stored,SOURCE/local)
            assert sha(SOURCE/local)==record['inputs'][local],local
        REFERENCE=SOURCE/'ref.png'
        field,inside,_=pigment_field(True)
        for _ in range(2):
            grown=inside.copy()
            for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                take=~grown & np.roll(inside,(dy,dx),(0,1))
                field[take]=np.roll(field,(dy,dx),(0,1))[take]
                grown|=take
            inside=grown
        parent=np.asarray(Image.open(SOURCE/'pigment.png').convert('RGB'))
        fine=parent.copy()
        factor=np.exp(np.clip(field[inside]*1.8,-.52,.40))
        fine[inside]=np.clip(np.rint((parent[inside]+np.float32(7.5))*factor[:,None]-7.5),0,255).astype('uint8')
        fine_file=args.out/'fine.png'
        Image.fromarray(fine).save(fine_file)
        assert hashlib.sha256(fine.tobytes()).hexdigest()==record['fine_rgb_sha256']
        on=np.any(fine!=parent,axis=2)
        combined=parent.copy() if args.chest is None else np.asarray(Image.open(args.chest).convert('RGB')).copy()
        if args.chest:
            assert sha(args.chest)==record['combined']['chest']
            assert not np.any(on & np.any(combined!=parent,axis=2))
        k=record['combined']['pedestal_display_blend']
        combined[on]=np.round((1-k)*parent[on]+k*fine[on]).astype('uint8')
        Image.fromarray(combined).save(args.out/'pigment.png')
        expected=record['combined_rgb_sha256'] if args.chest else record['pedestal_only_rgb_sha256']
        assert hashlib.sha256(combined.tobytes()).hexdigest()==expected
        print('Fine RGB, 68% display blend and output RGB verified.',sha(args.out/'pigment.png'))

if __name__=='__main__':
    main()

"""Sample actual horizontal cuts through the saved mane for matched carving comparisons."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
import numpy as np

p=argparse.ArgumentParser()
p.add_argument('scene',type=Path)
p.add_argument('out',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
bpy.ops.wm.open_mainfile(filepath=str(a.scene.resolve()),load_ui=False)
scene=bpy.context.scene
manes=[ob for ob in scene.objects if not ob.hide_render and ob.type=='MESH' and 'mane' in ob.name.lower()]
if len(manes)!=1:
    raise ValueError(f'Expected one visible mane, found {[ob.name for ob in manes]}')
ev=manes[0].evaluated_get(bpy.context.evaluated_depsgraph_get())
mesh=ev.to_mesh()
xyz=np.empty(len(mesh.vertices)*3,np.float32);mesh.vertices.foreach_get('co',xyz)
transform=np.asarray(ev.matrix_world,dtype=float)
xyz=xyz.reshape(-1,3)@transform[:3,:3].T+transform[:3,3]
mesh.calc_loop_triangles()
indices=np.empty(len(mesh.loop_triangles)*3,np.int32)
mesh.loop_triangles.foreach_get('vertices',indices)
tri=xyz[indices.reshape(-1,3)]
ev.to_mesh_clear()

def cross_section(z):
    faces=tri[(tri[:,:,2].min(1)<=z)&(tri[:,:,2].max(1)>z)]
    points=[]
    for i,j in [(0,1),(1,2),(2,0)]:
        l,r=faces[:,i],faces[:,j]
        meets=(l[:,2]<=z)!=(r[:,2]<=z)
        l,r=l[meets],r[meets]
        fraction=(z-l[:,2])/(r[:,2]-l[:,2])
        points.append(l[:,:2]+fraction[:,None]*(r[:,:2]-l[:,:2]))
    pts=np.unique(np.round(np.concatenate(points),6),axis=0)
    ctr=(pts.max(0)+pts.min(0))*.5
    angle=np.arctan2(pts[:,1]-ctr[1],pts[:,0]-ctr[0])
    pts=pts[angle.argsort()]
    closed=np.vstack((pts,pts[:1]))
    cumulative=np.r_[0,np.cumsum(np.linalg.norm(np.diff(closed,axis=0),axis=1))]
    ds=np.linspace(0,cumulative[-1],200,endpoint=False)
    sample=np.column_stack([np.interp(ds,cumulative,closed[:,j]) for j in (0,1)])
    back=sample-np.roll(sample,4,axis=0);next_=np.roll(sample,-4,axis=0)-sample
    cosine=(back*next_).sum(1)/(np.linalg.norm(back,axis=1)*np.linalg.norm(next_,axis=1))
    turns=np.rad2deg(np.arccos(np.clip(cosine,-1,1)))
    return {'plane_z':z,'closed_curve_xy':np.round(sample,5).tolist(),
            'fraction_with_under_two_degrees_turn':round(float((turns<2).mean()),3),
            'angle_fraction_in_sharpest_fifth':round(float(np.sort(turns)[-40:].sum()/turns.sum()),3)}
report={'model_sha256':hashlib.sha256(a.scene.read_bytes()).hexdigest(),'object':manes[0].name,
        'method':'Physical mesh intersection with horizontal planes. Resample each star-shaped closed outline at constant arc length. Estimate local turn using two adjacent chords spanning 2% of the perimeter each. Summary measurements describe the sections; the visual decision uses the actual clay and walnut surfaces.',
        'sections':[cross_section(z) for z in (2.55,3.05,3.65,4.10)]}
a.out.parent.mkdir(exist_ok=True,parents=True);a.out.write_text(json.dumps(report,indent=2)+'\n')
print([(s['plane_z'],s['fraction_with_under_two_degrees_turn'],s['angle_fraction_in_sharpest_fifth']) for s in report['sections']])

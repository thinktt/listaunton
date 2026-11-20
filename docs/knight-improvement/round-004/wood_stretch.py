"""Measure how a geometry edit stretches a fixed wood atlas on the lower mane."""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
import numpy as np
parser=argparse.ArgumentParser()
parser.add_argument('parent',type=Path)
parser.add_argument('candidate',type=Path)
parser.add_argument('output',type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def surface(path):
    bpy.ops.wm.open_mainfile(filepath=str(path.resolve()),load_ui=False)
    ob=bpy.data.objects['Knight | swept rounded mane'].evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=ob.to_mesh()
    try:
        xyz=np.empty(len(mesh.vertices)*3,np.float32)
        mesh.vertices.foreach_get('co',xyz)
        mat=np.asarray(ob.matrix_world,dtype=float)
        pos=xyz.reshape(-1,3)@mat[:3,:3].T+mat[:3,3]
        mesh.calc_loop_triangles()
        idx=np.empty(len(mesh.loop_triangles)*3,np.int32)
        mesh.loop_triangles.foreach_get('vertices',idx)
        uv=np.empty(len(mesh.uv_layers.active.data)*2,np.float32)
        mesh.uv_layers.active.data.foreach_get('uv',uv)
        loops=np.empty(len(mesh.loops),np.int32)
        mesh.loops.foreach_get('vertex_index',loops)
        faces=np.empty(len(mesh.polygons),np.int32)
        mesh.polygons.foreach_get('loop_total',faces)
        return pos,idx.reshape(-1,3),loops,faces,uv
    finally:
        ob.to_mesh_clear()
ap,i,loops,faces,uv=surface(args.parent)
bp,_,loopb,faceb,uvb=surface(args.candidate)
assert np.array_equal(loops,loopb) and np.array_equal(faces,faceb) and np.array_equal(uv,uvb)
# Blender can choose a different diagonal when it tessellates a deformed quad.
# Evaluate the same parametric points using the parent's triangulation.
a,b=ap[i],bp[i]
# Coordinates of the two triangle edges in a local orthonormal tangent basis.
def basis(t):
    e1=t[:,1]-t[:,0];e2=t[:,2]-t[:,0]
    first=np.linalg.norm(e1,axis=1)
    second=np.linalg.norm(np.cross(e1,e2),axis=1)/np.maximum(first,1e-15)
    cross=np.einsum('ij,ij->i',e1,e2)/np.maximum(first,1e-15)
    g=np.zeros((len(t),2,2));g[:,0,0]=first;g[:,0,1]=cross;g[:,1,1]=second
    return g,first*second*.5
A,area=basis(a);B,new_area=basis(b)
keep=(a.mean(1)[:,2] < 3.5)&(area>1e-9)&(new_area>1e-9)
values=np.linalg.svd(B[keep]@np.linalg.inv(A[keep]),compute_uv=False)
weights=area[keep]
def quantile(v,q):
    order=np.argsort(v);s=np.cumsum(weights[order])
    return round(float(v[order[np.searchsorted(s,q*s[-1])]]),4)
report={'parent':digest(args.parent),'candidate':digest(args.candidate),'same_face_topology_and_wood_uv':True,
        'method':'World-space deformation gradient on evaluated mane triangles with parent center z below 3.5. Quantiles weighted by original triangle area. A value of 1 means wood details retain their original size along that direction.',
        'triangles':int(keep.sum()),'area_ratio':round(float(new_area[keep].sum()/weights.sum()),4),
        'median_long_stretch':quantile(values[:,0],.5),'p95_long_stretch':quantile(values[:,0],.95),
        'median_short_stretch':quantile(values[:,1],.5),'p95_anisotropy':quantile(values[:,0]/values[:,1],.95)}
args.output.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

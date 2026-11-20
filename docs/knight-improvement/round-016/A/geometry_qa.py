"""Check that each edited component is a clean closed mesh with finite UVs and true intersection at the return."""
from pathlib import Path
import json,sys,hashlib
import bpy,bmesh,numpy as np
from mathutils.bvhtree import BVHTree
D=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(D))
from sculpt import load,carve,pose,world_vertices,rest_coords,sha
from self_intersection import test
def qamesh(o,g):
 m=o.data;m.calc_loop_triangles();pos=np.array([v.co[:] for v in m.vertices]);vtri=np.array([t.vertices[:] for t in m.loop_triangles])
 areas=np.linalg.norm(np.cross(pos[vtri[:,1]]-pos[vtri[:,0]],pos[vtri[:,2]]-pos[vtri[:,0]]),axis=1)
 uv=np.empty((len(m.loops),2),np.float32);m.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
 bm=bmesh.new();bm.from_mesh(m);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
 hits=test(o,g)
 if hits['pairs']:
  ranks=np.full(len(pos),-1,int);grid=np.load(D/'ring-chart.npz')['grid'];ranks[grid]=np.arange(len(grid))[:,None];vv=[v for hit in hits['pairs'] for t in hit['vertex_indices'] for v in t];print('fold stations',np.unique(ranks[vv],return_counts=True),flush=True)
 return {'triangles':len(vtri),'smallest_double_area':float(areas.min()),'degenerate_triangles':int((areas<1e-10).sum()),'nonmanifold_edges':int(bad),'self_intersections':hits['intersection_count'],'uv_sha256':hashlib.sha256(uv.tobytes()).hexdigest(),'uv_finite':bool(np.isfinite(uv).all()),'uv_bounds':[uv.min(0).tolist(),uv.max(0).tolist()]}
def main():
 name=sys.argv[-1] if sys.argv[-1] in ['parent','inspection','knight'] else 'inspection'
 s=load(name);g=bpy.context.evaluated_depsgraph_get();results={};parts=['swept rounded mane','continuous horse head and neck']
 for key in parts:results[key]=qamesh(s.objects['Knight | '+key],g)
 p=pose(s);trees={};xyzs={};indices={}
 for key in parts:
  o=s.objects['Knight | '+key];m=o.data;m.calc_loop_triangles();tri=np.array([t.vertices[:] for t in m.loop_triangles]);v=rest_coords(world_vertices(o),p);trees[key]=BVHTree.FromPolygons(v.tolist(),tri.tolist(),all_triangles=True);xyzs[key]=v;indices[key]=tri
 mane,head=parts;overlaps=trees[mane].overlap(trees[head]);front=[]
 for i,j in overlaps:
  x,y,z=xyzs[mane][indices[mane][i]].mean(0)
  if x>.06 and z>4.85:front.append([x,y,z])
 front=np.array(front)
 output={'scene_sha256':sha(D/(name+'.blend')),'parts':results,'front_native_intersection_pairs':len(front),'both_sides_of_joint':[int((front[:,1]<-.04).sum()),int((front[:,1]>.04).sum())]}
 (D/(name+'-qa.json')).write_text(json.dumps(output,indent=2)+'\n');print(output,flush=True)
if __name__=='__main__':main()

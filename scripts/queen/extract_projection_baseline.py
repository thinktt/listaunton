"""Read the accepted queen; preserve its editable controls and measure lower tessellation."""
from pathlib import Path
import bpy,bmesh,json,hashlib,math
import numpy as np
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[2];out=root/'assets/queen-projections';out.mkdir(parents=True,exist_ok=True)
source=root/'history/queen-before-54-finish/models/queen/queen-rebuilt.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene
ob=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render);points=np.asarray([tuple(v.co) for v in ob.data.vertices]);n=int(ob['ring_segments']);assert len(points)%n==0
np.savez_compressed(out/'baseline-controls.npz',points=points)
info={'sourceSha256':digest,'object':ob.name,'ringSegments':n,'bodyRingCount':int(ob['body_preserved_ring_count']),'finialFirstRing':int(ob['finial_first_ring']),'ringCount':len(points)//n,'floor':float(points[:,2].min()),'baseRadius':float(np.linalg.norm(points[:n*19,:2],axis=1).max()),'elevation':51.5,'scale':273.5,'cx':483.625,'y0':880.0,'sourceSubdivision':2,'candidateSubdivision':1,'crownTipCount':8}
def evaluated(level):
 for m in ob.modifiers:
  if m.type=='SUBSURF':m.levels=level;m.render_levels=level
 bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(graph);me=ev.to_mesh();me.calc_loop_triangles()
 vs=[v.co.copy() for v in me.vertices];fs=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();return vs,fs
dense,df=evaluated(2);low,lf=evaluated(1);tree=BVHTree.FromPolygons(low,lf,all_triangles=True)
distances=[tree.find_nearest(dense[i])[3] for i in range(0,len(dense),max(1,len(dense)//5000))]
study={'dense_triangles':len(df),'candidate_triangles':len(lf),'sample_count':len(distances),'surface_distance_max':max(distances),'surface_distance_p95':float(np.quantile(distances,.95)),'surface_distance_max_original_pixels':max(distances)*273.5/4.218205761316873,'method':'Dense subdivision-2 sampled vertices to nearest triangle of subdivision-1 surface; same editable controls.'}
assert study['surface_distance_max_original_pixels']<.5,study
info['reduced_mesh_check']=study
(out/'baseline-info.json').write_text(json.dumps(info,indent=2)+'\n');assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print(json.dumps(info,indent=2))

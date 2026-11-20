from pathlib import Path
import sys,json,bpy,numpy as np
sys.dont_write_bytecode=True
o=Path(__file__).resolve().parent;sys.path.insert(0,str(o.parents[2]/'scripts/knight'))
from mission_scene import visible_meshes
report={}
for tag,name in [('parent','parent.blend'),('candidate','knight.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(o/name),load_ui=False);s=bpy.context.scene;g=bpy.context.evaluated_depsgraph_get();parts={}
 for obj in visible_meshes(s):
  ev=obj.evaluated_get(g);me=ev.to_mesh();me.calc_loop_triangles();v=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get('co',v.ravel());tri=np.empty((len(me.loop_triangles),3),np.int32);me.loop_triangles.foreach_get('vertices',tri.ravel());p=v[tri];d=np.linalg.norm(np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]),axis=1)
  n=np.empty((len(me.corner_normals),3),np.float32);me.corner_normals.foreach_get('vector',n.ravel())
  parts[obj.name]={'triangles':len(tri),'double_area_below_1e-10':int((d<1e-10).sum()),'minimum_double_area':float(d.min()),'finite_corner_normals':bool(np.isfinite(n).all())}
  ev.to_mesh_clear()
 report[tag]=parts
(o/'evaluated-mesh.json').write_text(json.dumps(report,indent=2)+'\n');print([(k,parts['Knight | continuous horse head and neck']) for k,parts in report.items()],flush=True)

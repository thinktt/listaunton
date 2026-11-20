"""Audit the proposed local meshes and look at the actual two whole-head profiles."""
import sys,json,hashlib
from pathlib import Path
import bpy,numpy as np
sys.dont_write_bytecode=True;D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from self_intersection import test
from pictures import open_model,whole
def audit():
 s=open_model('inspection');g=bpy.context.evaluated_depsgraph_get();parts={}
 for name in ['continuous horse head and neck','near swept ear','far swept ear','near eye','far eye','coherent skull cheek and conical muzzle']:
  ob=s.objects['Knight | '+name];rec=test(ob,g);ev=ob.evaluated_get(g);m=ev.to_mesh();m.calc_loop_triangles()
  p=np.empty((len(m.vertices),3),np.float32);m.vertices.foreach_get('co',p.ravel());tri=np.empty((len(m.loop_triangles),3),np.int32);m.loop_triangles.foreach_get('vertices',tri.ravel())
  area=np.linalg.norm(np.cross(p[tri[:,1]]-p[tri[:,0]],p[tri[:,2]]-p[tri[:,0]]),axis=1)
  rec['min_double_area']=float(area.min());rec['degenerate']=int((area<1e-10).sum());ev.to_mesh_clear();parts[name]=rec
  print(name,rec['intersection_count'],rec['degenerate'],flush=True)
 (D/'sculpt-check.json').write_text(json.dumps({'source_sha256':hashlib.sha256((D/'inspection.blend').read_bytes()).hexdigest(),'parts':parts},indent=2)+'\n')
if __name__=='__main__':
 if sys.argv[-1]=='native':audit()
 else:whole('inspection',True)

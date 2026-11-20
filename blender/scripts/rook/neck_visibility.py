"""Conservatively protect reference-visible neck triangles before hidden wood repair."""
from pathlib import Path
import bpy,numpy as np,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];p=ROOT/'history/rook-mission-066/models/rook/rook-rebuilt.blend';assert hashlib.sha256(p.read_bytes()).hexdigest()=='4e1557a8dbfd4e93c6c837403ffaed7b7f08e1565f063f576eb6e5c338856cf7'
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False);s=bpy.context.scene;ob=next(o for o in s.objects if o.get('rook_editable_control'));ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();verts=[ob.matrix_world@v.co for v in me.vertices];tree=BVHTree.FromPolygons(verts,[t.vertices[:] for t in me.loop_triangles],all_triangles=True);view=(s.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized();W=3072;box=[int(.01*W),int((1-.78)*W),int(.75*W),int((1-.59)*W)];x0,y0,x1,y1=box;covered=np.zeros((y1-y0,x1-x0),bool);protected=covered.copy();uv=me.uv_layers['Pigment atlas'];count=[0,0]
for t in me.loop_triangles:
 a=np.array([[uv.data[i].uv.x*W,(1-uv.data[i].uv.y)*W] for i in t.loops]);lo=np.maximum(np.floor(a.min(0)).astype(int),[x0,y0]);hi=np.minimum(np.ceil(a.max(0)).astype(int),[x1,y1])
 if np.any(hi<=lo):continue
 abc=[verts[i] for i in t.vertices];visible=False
 for weights in [(1/3,1/3,1/3),(.8,.1,.1),(.1,.8,.1),(.1,.1,.8),(.48,.48,.04),(.48,.04,.48),(.04,.48,.48)]:
  pos=sum((v*w for v,w in zip(abc,weights)),Vector());hit=tree.ray_cast(pos+view*10,-view,11)
  if hit[0] is not None and (hit[0]-pos).length<.0001:visible=True;break
 xx,yy=np.meshgrid(np.arange(lo[0],hi[0])+.5,np.arange(lo[1],hi[1])+.5);ab=a[1]-a[0];ac=a[2]-a[0];den=ab[0]*ac[1]-ab[1]*ac[0]
 if abs(den)<1e-10:continue
 dx=xx-a[0,0];dy=yy-a[0,1];v=(dx*ac[1]-dy*ac[0])/den;w=(ab[0]*dy-ab[1]*dx)/den;inside=(v>=-1e-6)&(w>=-1e-6)&(v+w<=1.000001);sl=np.s_[lo[1]-y0:hi[1]-y0,lo[0]-x0:hi[0]-x0];covered[sl]|=inside
 if visible:protected[sl]|=inside
 count[int(visible)]+=1
out=ROOT/'build/rook-mission/067-neck-visibility';out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'visibility.npz',covered=covered,protected=protected,box=box);(out/'report.json').write_text(json.dumps({'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'neck_triangles_hidden_visible':count,'covered_texels':int(covered.sum()),'protected_texels':int(protected.sum()),'method':'Seven interior samples per evaluated triangle, BVH occlusion from fixed orthographic camera. Any visible sample protects entire UV triangle. Approximate conservative classification, verified afterward by fixed renders.'},indent=2)+'\n');print(count);ev.to_mesh_clear()

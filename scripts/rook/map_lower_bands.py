"""Rasterize actual evaluated upper-patch UV triangles into fixed-view coordinates."""
from pathlib import Path
import bpy,sys,json,hashlib,numpy as np
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'history/rook-mission-063/models/rook/rook-rebuilt.blend';assert hashlib.sha256(source.read_bytes()).hexdigest()=='a5008b93c10cd3e0f7cc8e23d1b7274c7a40529e0d0fdacf6c211fe8bf03cb78'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;ob=next(o for o in s.objects if o.get('rook_editable_control'));ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();me.calc_loop_triangles();uv=me.uv_layers['Pigment atlas'];W=3072
box=[int(.47*W),int((1-.457)*W),int(.66*W),int((1-.337)*W)];x0,y0,x1,y1=box;px=np.full((y1-y0,x1-x0),np.nan,np.float32);py=px.copy();hits=np.zeros(px.shape,np.uint8)
projected=[]
for v in me.vertices:
 p=world_to_camera_view(s,s.camera,ob.matrix_world@v.co);projected.append((p.x*1254-.5,(1-p.y)*1254-.5))
projected=np.array(projected)
for tri in me.loop_triangles:
 a=np.array([[uv.data[i].uv.x*W,(1-uv.data[i].uv.y)*W] for i in tri.loops]);lo=np.maximum(np.floor(a.min(0)).astype(int),[x0,y0]);hi=np.minimum(np.ceil(a.max(0)).astype(int),[x1,y1]);
 if np.any(hi<=lo):continue
 xx,yy=np.meshgrid(np.arange(lo[0],hi[0])+.5,np.arange(lo[1],hi[1])+.5);ab=a[1]-a[0];ac=a[2]-a[0];den=ab[0]*ac[1]-ab[1]*ac[0]
 if abs(den)<1e-10:continue
 dx=xx-a[0,0];dy=yy-a[0,1];v=(dx*ac[1]-dy*ac[0])/den;w=(ab[0]*dy-ab[1]*dx)/den;u=1-v-w;mask=(u>=-1e-6)&(v>=-1e-6)&(w>=-1e-6);p=projected[list(tri.vertices)];X=u*p[0,0]+v*p[1,0]+w*p[2,0];Y=u*p[0,1]+v*p[1,1]+w*p[2,1];sl=np.s_[lo[1]-y0:hi[1]-y0,lo[0]-x0:hi[0]-x0];px[sl][mask]=X[mask];py[sl][mask]=Y[mask];hits[sl][mask]+=1
out=ROOT/'build/rook-mission/064-lower-correspondence';out.mkdir(parents=True,exist_ok=True);np.savez_compressed(out/'mapping.npz',x=px,y=py,box=box,hits=hits);report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'atlas_box':box,'covered_texels':int(np.isfinite(px).sum()),'multiply_covered_texels':int((hits>1).sum()),'method':'Barycentric UV rasterization of evaluated closed body; orthographic saved-camera projection. Local front-facing patch only.'};(out/'mapping.json').write_text(json.dumps(report,indent=2)+'\n');ev.to_mesh_clear();print(report)


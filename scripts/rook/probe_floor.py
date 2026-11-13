"""Trace fixed-view floor-edge pixels to real atlas UVs and local normals."""
from pathlib import Path
import bpy,sys,json,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'history/rook-mission-037/models/rook/rook-rebuilt.blend'),load_ui=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;proj=cam.calc_matrix_camera(dg,x=1254,y=1254);view=(cam.matrix_world.to_3x3()@Vector((0,0,1))).normalized();rows=[]
for x in [450,483,520]:
 for y in range(328,362,2):
  clip=proj.inverted()@Vector((2*(x+.5)/1254-1,1-2*(y+.5)/1254,-1,1));origin=cam.matrix_world@(clip.xyz/clip.w);hit,p,n,fi,o,_=s.ray_cast(dg,origin,-view)
  if not hit:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();uv=m.uv_layers['Pigment atlas']
  for tri in m.loop_triangles:
   if tri.polygon_index!=fi:continue
   a,b,c=[o.matrix_world@m.vertices[i].co for i in tri.vertices];ab=b-a;ac=c-a;ap=p-a;aa=ab.dot(ab);bb=ab.dot(ac);cc=ac.dot(ac);dd=ap.dot(ab);ee=ap.dot(ac);den=aa*cc-bb*bb
   if abs(den)<1e-18:continue
   v=(cc*dd-bb*ee)/den;w=(aa*ee-bb*dd)/den;u=1-v-w
   if min(u,v,w)<-.001:continue
   coord=sum((uv.data[i].uv*t for i,t in zip(tri.loops,[u,v,w])),Vector((0,0)));normal=sum((m.corner_normals[i].vector*t for i,t in zip(tri.loops,[u,v,w])),Vector()).normalized();rows.append({'pixel':[x,y],'point':list(p),'uv':list(coord),'normal':list(normal),'object':o.name});break
  ev.to_mesh_clear()
body=next(o for o in s.objects if o.get('rook_editable_control'));co=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,128,3);r=np.linalg.norm(co[:,:,:2],axis=2).mean(1);z=co[:,:,2].mean(1);arc=np.r_[0,np.cumsum(np.hypot(np.diff(r),np.diff(z)))];vs=.01+.98*arc/arc[-1]
out=ROOT/'build/rook-mission/038-floor-probe';out.mkdir(parents=True,exist_ok=True);report={'samples':rows,'profile_rows':[{'index':i,'radius':float(r[i]),'z':float(z[i]),'v':float(vs[i])} for i in range(49,len(r))]};(out/'probe.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['profile_rows']))
for row in rows:
 if row['pixel'][0]==483:print(json.dumps(row))

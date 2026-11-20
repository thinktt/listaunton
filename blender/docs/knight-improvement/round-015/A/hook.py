"""Locate the contact between the temporal fold and the skull on the true near profile."""
import math,json,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D));from pictures import open_model
from sculpt import chart
from probe_carving import rest
for name in ['parent','inspection']:
 s=open_model(name);p=json.loads(s['knight_mission_pose']);a=math.radians(p['twist_degrees']);trans=Vector((-math.sin(a),math.cos(a),0));up=Vector((0,0,1))
 cam=s.camera;t=s.objects['Knight | near eye'].matrix_world.translation.copy();cam.location=t+7*(-trans+.28*up);cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.resolution_x=448;s.render.resolution_y=314;cam.data.ortho_scale=1.42;cam.data.shift_x=cam.data.shift_y=0;bpy.context.view_layer.update();q=cam.matrix_world.to_quaternion()
 data=[]
 for px,py in [(125,76),(134,82),(140,87),(146,91),(151,97),(157,104),(163,110),(168,113),(172,115),(177,114),(184,111),(193,109),(203,108),(216,110),(233,114),(252,126)]:
  origin=cam.location+q@Vector(((px+.5-224)*1.42/448,(157-py-.5)*1.42/448,0))
  hit,pt,no,idx,o,_=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,q@Vector((0,0,-1)))
  x=rest(pt,p);u,v=chart(np.array([x]));data.append([px,py,o.name,round(float(u[0]),3),round(float(v[0]),3),round(-x[1],3)])
 print(name,data)
 (D/(name+'-hook.json')).write_text(json.dumps(data,indent=2)+'\n')

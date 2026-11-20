"""Locate reflector directions from the actual smooth king surface at marked pixels."""
from pathlib import Path
import sys,json
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/king-mission/004-fine-reference-grain/king.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;g=bpy.context.evaluated_depsgraph_get();cam=s.camera
P=cam.calc_matrix_camera(g,x=1254,y=1254);W=cam.matrix_world;view=(W.to_3x3()@Vector((0,0,1))).normalized();rows=[]
for name,x,y in [('platter',580,303),('upper-collar',506,429),('middle-collar',538,497),('lower-collar',523,541),('socket',479,771),('base-upper',573,861),('base-lower',594,965),('foot',448,1030),('cross',570,85)]:
    loc=P.inverted()@Vector((2*x/1254-1,1-2*y/1254,-1,1));origin=W@(loc.xyz/loc.w)
    hit,point,normal,fi,obj,_=s.ray_cast(g,origin,-view)
    if not hit:rows.append({'name':name,'pixel':[x,y],'hit':False});continue
    ev=obj.evaluated_get(g);me=ev.to_mesh();me.calc_loop_triangles()
    for tri in me.loop_triangles:
        if tri.polygon_index!=fi:continue
        a,b,c=[obj.matrix_world@me.vertices[i].co for i in tri.vertices];v0=b-a;v1=c-a;v2=point-a
        d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
        if abs(den)<1e-18:continue
        v=(d11*d20-d01*d21)/den;w=(d00*d21-d01*d20)/den;u=1-v-w
        if min(u,v,w)<-.001:continue
        normal=sum((me.corner_normals[li].vector*weight for li,weight in zip(tri.loops,[u,v,w])),Vector())
        normal=(obj.matrix_world.to_3x3().inverted().transposed()@normal).normalized();break
    reflected=(2*normal.dot(view)*normal-view).normalized()
    rows.append({'name':name,'pixel':[x,y],'point':list(point),'normal':list(normal),'reflected':list(reflected),'position':list(point+6*reflected)})
    ev.to_mesh_clear()
out=ROOT/'build/king-mission/reflection-probes.json';out.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))

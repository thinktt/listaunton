"""Infer specular light rays at selected reference pixels on the current mesh.

This is diagnostic geometry, not a recovered claim about the source lighting.
"""
from pathlib import Path
import json
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'build/queen-mission/003b-collars-outline/queen.blend'),load_ui=False)
scene=bpy.context.scene;camera=scene.camera;graph=bpy.context.evaluated_depsgraph_get()
obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
verts=np.empty(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',verts);verts=verts.reshape(-1,3)
normals=np.empty(len(mesh.vertices)*3);mesh.vertices.foreach_get('normal',normals);normals=normals.reshape(-1,3)
tris=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('vertices',tris);tris=tris.reshape(-1,3)
tree=BVHTree.FromPolygons(verts.tolist(),tris.tolist(),all_triangles=True)
W=scene.render.resolution_x;H=scene.render.resolution_y
proj=camera.calc_matrix_camera(graph,x=W,y=H)
inv=(proj@camera.matrix_world.inverted()).inverted()
view=camera.matrix_world.to_3x3()@Vector((0,0,1));view.normalize()
targets={'finial-key':(486,181),'finial-side':(500,203),'bowl-back':(494,146),'upper-collar':(546,441),'middle-collar':(571,493),'lower-collar':(581,534),'socket':(427,746),'base':(565,884),'foot':(400,1030)}
results={}
for name,(x,y) in targets.items():
    near=inv@Vector((2*x/W-1,1-2*y/H,-1,1));near=near.xyz/near.w
    loc,face_n,idx,dist=tree.ray_cast(near,-view,100)
    if loc is None:continue
    tri=tris[idx];a,b,c=verts[tri]
    uv=np.linalg.lstsq(np.column_stack((b-a,c-a)),np.array(loc)-a,rcond=None)[0]
    n=Vector(normals[tri[0]]*(1-sum(uv))+normals[tri[1]]*uv[0]+normals[tri[2]]*uv[1]);n.normalize()
    light_dir=2*n.dot(view)*n-view
    results[name]={'pixel':[x,y],'point':list(loc),'normal':list(n),'light_direction':list(light_dir),'light_at_distance_6':list(loc+light_dir*6)}
out=ROOT/'build/queen-mission/reflection-rays.json';out.write_text(json.dumps(results,indent=2))
for name,r in results.items():print(name,'point',np.round(r['point'],2),'normal',np.round(r['normal'],2),'light@6',np.round(r['light_at_distance_6'],2))
ev.to_mesh_clear()

"""Infer specular light rays at selected reference pixels on the current mesh.

This is diagnostic geometry, not a recovered claim about the source lighting.
"""
from pathlib import Path
import argparse,json,sys
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',default='models/queen/queen-rebuilt.blend');p.add_argument('--output',default='build/queen-mission/reflection-rays.json');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(ROOT/args.source),load_ui=False)
scene=bpy.context.scene;camera=scene.camera
obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
for modifier in obj.modifiers:
    if modifier.type=='SUBSURF':modifier.levels=modifier.render_levels
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get()
ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
verts=np.empty(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',verts);verts=verts.reshape(-1,3)
normals=np.empty(len(mesh.vertices)*3);mesh.vertices.foreach_get('normal',normals);normals=normals.reshape(-1,3)
tris=np.empty(len(mesh.loop_triangles)*3,dtype=np.int32);mesh.loop_triangles.foreach_get('vertices',tris);tris=tris.reshape(-1,3)
tree=BVHTree.FromPolygons(verts.tolist(),tris.tolist(),all_triangles=True)
W=scene.render.resolution_x;H=scene.render.resolution_y
proj=camera.calc_matrix_camera(graph,x=W,y=H)
inv=(proj@camera.matrix_world.inverted()).inverted()
view=camera.matrix_world.to_3x3()@Vector((0,0,1));view.normalize()
targets={'finial-left':(479,186),'finial-top':(494,181),'finial-right':(500,205),
         'bowl-back':(505,148),'bowl-left':(428,168),'upper-collar-right':(543,439),
         'middle-collar-right':(580,477),'middle-collar-left':(426,501),
         'lower-collar-right':(566,528),'socket-left':(432,759),'socket-right':(553,764),
         'base-left':(316,647),'base-right':(578,901),'base-right-upper':(574,850),'base-right-lower':(583,955),
         'foot-left':(384,1020),'foot-right':(618,1012)}
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
out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(results,indent=2))
for name,r in results.items():print(name,'point',np.round(r['point'],2),'normal',np.round(r['normal'],2),'light@6',np.round(r['light_at_distance_6'],2))
ev.to_mesh_clear()

"""Locate reference features on the actual carving for shape and light trials."""
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import BUILD, json_file, visible_meshes
from mission_pose import bend_weight


def rest(point, pose):
    p=np.array(point)
    w=bend_weight(np.array([p[2]]))[0]
    theta=np.radians(w*pose["twist_degrees"])
    xy=p[:2]-w*np.array([pose["dx"],pose["dy"]])
    return [float(np.cos(theta)*xy[0]+np.sin(theta)*xy[1]),float(-np.sin(theta)*xy[0]+np.cos(theta)*xy[1]),float(p[2])]


def point_probe(scene):
    graph=bpy.context.evaluated_depsgraph_get()
    objects=visible_meshes(scene)
    trees={o.name:(o,BVHTree.FromObject(o,graph)) for o in objects}
    cam=scene.camera
    camera=np.array(cam.matrix_world)
    proj=np.asarray(cam.calc_matrix_camera(graph,x=1254,y=1254))
    view=cam.matrix_world.to_quaternion()@Vector((0,0,1))
    def probe(x,y):
        camera_point=np.array([((2*x/1254-1)-proj[0,3])/proj[0,0],((1-2*y/1254)-proj[1,3])/proj[1,1],0,1])
        start=Vector((camera@camera_point)[:3]);hits=[]
        for name,(o,tree) in trees.items():
            inv=o.matrix_world.inverted();loc,n,_,_=tree.ray_cast(inv@start,inv.to_3x3()@(-view),30)
            if loc is not None:
                pos=o.matrix_world@loc
                hits.append(((pos-start).length,name,pos,(o.matrix_world.to_3x3().inverted().transposed()@n).normalized()))
        return min(hits,key=lambda row:row[0]) if hits else None
    return probe


if __name__=="__main__":
    import json
    source=BUILD/"001-carving-pose/knight.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    pose=json.loads(s["knight_mission_pose"]);probe=point_probe(s)
    results={}
    for name,(x,y) in {"eye":(505,478),"eye-left":(481,470),"eye-right":(540,488),"brow":(505,461),
        "ear-start":(278,390),"ear-middle":(399,430),"mane-ridge":(370,341),"nose":(706,509),
        "cheek":(456,515),"neck-edge":(445,629),"neck-edge-bottom":(547,711),"neck-well":(508,613)}.items():
        hit=probe(x,y)
        if hit:
            _,obj,pt,n=hit
            results[name]={"pixel":[x,y],"object":obj,"world":list(pt),"pre_pose":rest(pt,pose),"normal":list(n)}
    for o in visible_meshes(s):
        if o.name.endswith(" eye"):results[o.name]={"center":list(o.location),"pre_pose":rest(o.location,pose)}
    json_file(BUILD/"landmarks-001.json", results)
    for key,v in results.items():
        print(key, v.get("object",""),np.round(v["pre_pose"],3).tolist(),flush=True)

"""Carve and seat paired almond-shaped eyes at the observed side-face landmarks."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from mission_pose import bend_weight,posed
from mission_scene import ROOT,BUILD,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes,world_vertices
from probe_carving import point_probe

SOURCE=ROOT/"history/knight/mission-001/knight-rebuilt.blend"
SOURCE_HASH="d10b2b09377981b915ac8fd418c7c654fdec6e6b6f9f631d8971276dcbcf67b7"


def unpose(points, pose):
    p=points.copy();w=bend_weight(p[:,2]);theta=np.radians(pose["twist_degrees"])*w
    x=p[:,0]-w*pose["dx"];y=p[:,1]-w*pose["dy"]
    p[:,0]=np.cos(theta)*x+np.sin(theta)*y
    p[:,1]=-np.sin(theta)*x+np.cos(theta)*y
    return p


def apply_world(obj, points, origin=None):
    m=np.asarray(obj.matrix_world)
    if origin is None:origin=m[:3,3].copy()
    coords=(points-origin)@np.linalg.inv(m[:3,:3]).T
    obj.data.vertices.foreach_set("co",np.asarray(coords,dtype=np.float32).ravel())
    obj.data.update();obj.location=Vector(origin)


def count_eye_pixels(scene):
    probe=point_probe(scene)
    hits=[]
    for y in range(443,513,2):
        for x in range(449,562,2):
            hit=probe(x,y)
            if hit and hit[1]=="Knight | near eye":hits.append([x,y])
    return {"grid_spacing_pixels":2,"visible_samples":len(hits),
            "bounds":[np.min(hits,axis=0).tolist(),np.max(hits,axis=0).tolist()] if hits else None}


def carve(source, variant, deep=.085, eye_height=.055, convex=False):
    assert sha(source)==SOURCE_HASH
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;pose=json.loads(scene["knight_mission_pose"])
    params=[pose["dx"],pose["dy"],pose["twist_degrees"]]
    before=count_eye_pixels(scene)
    center=np.array([.420,4.155])
    along=np.array([1.,-.76]);along/=np.linalg.norm(along)
    up=np.array([-along[1],along[0]])
    skin=bpy.data.objects["Knight | continuous horse head and neck"]
    construction=bpy.data.objects["Knight | coherent skull cheek and conical muzzle"]
    for obj in (skin,construction):
        rest=unpose(world_vertices(obj),pose)
        if obj==skin:uncarved_skin=rest.copy()
        diff=rest[:,[0,2]]-center;u=diff@along;v=diff@up
        width=.085*(1-.23*np.clip((u/.245)**2,0,1))
        radius=np.sqrt((u/.248)**2+(v/width)**2)
        floor=-deep*np.exp(-(radius/.85)**2)
        lip_gain,lip_width=(.022,.36) if convex else (.040,.24)
        lip=lip_gain*np.exp(-((radius-1.05)/lip_width)**2)*(.72+.28*np.tanh(v/.05))
        side=np.clip((np.abs(rest[:,1])-.10)/.18,0,1)
        rest[:,1]+=np.sign(rest[:,1])*side*(floor+lip)
        apply_world(obj,posed(rest,*params))
        if obj==skin:skin_rest=rest
    skin.data.calc_loop_triangles()
    tris=np.empty((len(skin.data.loop_triangles),3),np.int32)
    skin.data.loop_triangles.foreach_get("vertices",tris.ravel())
    tree=BVHTree.FromPolygons(skin_rest.tolist(),tris.tolist(),all_triangles=True)
    lens_surface=BVHTree.FromPolygons(uncarved_skin.tolist(),tris.tolist(),all_triangles=True) if convex else tree
    # Preserve the existing closed eye topology and UVs. Move the almond to
    # the new hollow and follow the actual curved floor around its perimeter.
    for side,name in [(-1,"near"),(1,"far")]:
        obj=bpy.data.objects["Knight | "+name+" eye"]
        rest=unpose(world_vertices(obj),pose)
        old_center=unpose(np.asarray(obj.matrix_world)[None,:3,3],pose)[0]
        relative=rest-old_center
        old_along=np.array([math.cos(.48),-math.sin(.48)])
        old_up=np.array([-old_along[1],old_along[0]])
        uu=(relative[:,[0,2]]@old_along)/.096
        vv=(relative[:,[0,2]]@old_up)/.047
        ww=relative[:,1]/.033
        half_length=.198 if convex else .185
        xz=center+(half_length*uu)[:,None]*along+(eye_height*vv*(1-.28*uu**2))[:,None]*up
        result=np.empty_like(rest)
        result[:,0]=xz[:,0];result[:,2]=xz[:,1]
        for i,(x,z) in enumerate(xz):
            loc=lens_surface.ray_cast(Vector((x,side*2,z)),Vector((0,-side,0)),5)[0]
            assert loc is not None
            result[i,1]=loc.y+ww[i]*(.069 if convex else .045)-side*(.041 if convex else .010)
        hit=tree.ray_cast(Vector((center[0],side*2,center[1])),Vector((0,-side,0)),5)[0]
        new_origin=posed(np.array([[center[0],hit.y-side*.010,center[1]]]),*params)[0]
        apply_world(obj,posed(result,*params),new_origin)
    bpy.context.view_layer.update()
    after=count_eye_pixels(scene)
    out=BUILD/variant;out.mkdir(parents=True,exist_ok=True)
    cfg={"baseline":source.relative_to(ROOT).as_posix(),"source_sha256":sha(source),"center_xz":center.tolist(),
         "socket_depth":deep,"eye_half_length":half_length,"eye_half_height":eye_height,"convex_lens":convex,"before":before,"after":after,
         "method":"Carve a bilateral almond hollow and raised eyelid in the continuous skull. Seat both closed eye forms against the remodeled surface. Preserve pedestal, camera, pigment coordinates, lighting and all other components."}
    scene["knight_mission_eye"]=json.dumps(cfg,sort_keys=True)
    configure_render(scene,64);save_model(scene,out/"knight.blend");render(scene,out/"wood.png")
    wood=skin.data.materials[0];clay=bpy.data.materials["Neutral satin clay"]
    for obj in visible_meshes(scene):obj.data.materials[0]=clay
    render(scene,out/"neutral.png")
    for obj in visible_meshes(scene):obj.data.materials[0]=wood
    use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg)
    print("KNIGHT_EYE_TRIAL",variant,before,after,flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--variant",default="009-carved-eye");p.add_argument("--depth",type=float,default=.085)
    p.add_argument("--eye-height",type=float,default=.055);p.add_argument("--convex",action="store_true")
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    carve(SOURCE,args.variant,args.depth,args.eye_height,args.convex)

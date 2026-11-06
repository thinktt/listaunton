"""Fit the broad upper surface of each swept ear while retaining its lower edge."""
import argparse
import json
from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).parent))
from export_mission import export
from mission_scene import ASSETS,BUILD,MODEL,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes,world_vertices
from mission_pose import posed
from project_mission_pigment import surface_tree
from refine_eye import apply_world,unpose

# Approximate boundaries read from the selected reference, checked against the
# original. The lower contour is already close to the accepted carving.
COLUMNS=[285,305,325,350,375,400,425,450,475,500,525]
UPPER=np.array([383,379,377,377,379,383,389,399,412,429,444])
LOWER=np.array([397,406,417,429,440,450,458,463,465,466,466])


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,default=MODEL)
    p.add_argument("--variant",default="022-broad-swept-ear")
    p.add_argument("--preserve-profile",action="store_true")
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/args.variant;out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.source),load_ui=False);scene=bpy.context.scene
    pose=json.loads(scene["knight_mission_pose"]);par=[pose["dx"],pose["dy"],pose["twist_degrees"]]
    ears=[bpy.data.objects["Knight | "+side+" swept ear"] for side in ("near","far")]
    rings=[unpose(world_vertices(ear),pose).reshape(7,64,3) for ear in ears]
    graph=bpy.context.evaluated_depsgraph_get();cam=scene.camera;camera=np.asarray(cam.matrix_world)
    projection=np.asarray(cam.calc_matrix_camera(graph,x=1254,y=1254))
    combined=projection@np.linalg.inv(camera)
    pix=(1-(world_vertices(ears[0])@combined[1,:3]+combined[1,3]))*627
    rows=pix.reshape(7,64)
    top=(rows.max(1)[:,None]-rows)/np.maximum(1e-6,np.ptp(rows,axis=1)[:,None])
    profile=np.array([.004,.061,.169,.262,.241,.119,.0])[:,None]*top**1.2
    front=np.array([0,0,0,.28,1,.82,0])[:,None]
    def set_ear(depth,rise,front_rise=0):
        for side,ear,rest in zip((-1,1),ears,rings):
            result=rest.copy()
            result[:,:,1]-=side*depth*profile
            result[:,:,2]+=(rise+front_rise*front)*profile
            apply_world(ear,posed(result.reshape(-1,3),*par))
        bpy.context.view_layer.update()
    others=surface_tree([o for o in visible_meshes(scene) if o not in ears])
    direction=cam.matrix_world.to_quaternion()@Vector((0,0,-1))
    ray_groups=[]
    for x in COLUMNS:
        rays=[]
        for y in range(367,473):
            cx=((2*(x+.5)/1254-1)-projection[0,3])/projection[0,0]
            cy=((1-2*(y+.5)/1254)-projection[1,3])/projection[1,1]
            origin=Vector((camera@np.array([cx,cy,0,1]))[:3])
            block=others.ray_cast(origin,direction,25)[3]
            rays.append((y,origin,block if block is not None else 25))
        ray_groups.append(rays)
    baseline=bpy.data.images.load(str(ASSETS/"render.png"),check_existing=False)
    rgba=np.empty(1254*1254*4,np.float32);baseline.pixels.foreach_get(rgba)
    bounds=np.argmax(rgba.reshape(1254,1254,4)[::-1,:,3]>.5,axis=0)
    bpy.data.images.remove(baseline)
    def protrusion():
        maximum=0.
        for ear in ears:
            ev=ear.evaluated_get(graph);mesh=ev.to_mesh()
            local=np.empty((len(mesh.vertices),3),np.float32);mesh.vertices.foreach_get("co",local.ravel())
            matrix=np.asarray(ear.matrix_world)
            pc=(local@matrix[:3,:3].T+matrix[:3,3])@combined[:2,:3].T+combined[:2,3]
            x=np.clip(np.rint((1+pc[:,0])*627-.5).astype(int),0,1253)
            y=(1-pc[:,1])*627-.5
            maximum=max(maximum,float(np.max(bounds[x]-y)))
            ev.to_mesh_clear()
        return maximum
    def examine(choice):
        depth,rise,*extra=choice;extra=extra[0] if extra else 0
        set_ear(depth,rise,extra)
        ear=ears[0];inv=ear.matrix_world.inverted();local_dir=inv.to_3x3()@direction
        tree=BVHTree.FromObject(ear,graph)
        low=[];high=[]
        for rays in ray_groups:
            ys=[]
            for y,origin,limit in rays:
                point=tree.ray_cast(inv@origin,local_dir,25)[0]
                if point is not None and (ear.matrix_world@point-origin).length<=limit+.0003:ys.append(y)
            low.append(min(ys) if ys else 472);high.append(max(ys) if ys else 367)
        # Penalize lifting the side silhouette more than the fit requires.
        loss=float(np.abs(np.array(low)-UPPER).mean()+.7*np.abs(np.array(high)-LOWER).mean()+1.0*abs(rise))
        spill=protrusion()
        if args.preserve_profile:
            loss+=12*max(0,spill-.65)+2.5*abs(rise)+abs(extra)
        return {"depth":round(depth,4),"rise":round(rise,4),"front_rise":round(extra,4),"upper":low,"lower":high,"rise_above_baseline_pixels":spill,"loss":loss}
    candidates=[(0,0),(.85,.25),(.65,.55),(.40,.85),(.10,1.05),(-.22,1.20),(.72,.70),(.64,.98)]
    if args.preserve_profile:
        candidates=[(0,0,0),(.85,.16,0),(.80,.20,.21),(.65,.25,.43),(.72,.27,.32),(.94,.10,.36),(.60,.30,.32),(.72,.12,.55)]
    trials=[examine(x) for x in candidates];best=min(trials,key=lambda t:t["loss"])
    center=np.array([best["depth"],best["rise"],best["front_rise"]])
    for delta in [[.12,0,0],[-.12,0,0],[0,.09,0],[0,-.09,0],[0,0,.14],[0,0,-.14]]:
        choice=center+delta
        if -.5<=choice[0]<=1.2 and choice[1]>=0 and (not args.preserve_profile or choice[1]<=.31):
            trials.append(examine(choice))
    best=min(trials,key=lambda t:t["loss"]);set_ear(best["depth"],best["rise"],best["front_rise"])
    cfg={"source_sha256":sha(args.source),"columns":COLUMNS,"observed_upper":UPPER.tolist(),"observed_lower":LOWER.tolist(),
         "profile_world_units":[.004,.061,.169,.262,.241,.119,.0],"trials":trials,"selected":best,"samples":144,
         "method":"Measure registered ray-visible ear boundaries behind the mane. Redistribute the existing paired surfaces toward the upper inside edge. Keep both lower lips, the eye, muzzle and accepted pigment coordinates."}
    configure_render(scene,144);scene["knight_broader_ear"]=json.dumps(cfg)
    save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,144)
    texture=ASSETS/json.loads((ASSETS/"mission-checkpoint.json").read_text())["texture_file"]
    export(scene,texture,output=out,source=out/"knight.blend")
    render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg);print("KNIGHT_SWEPT_EAR",trials[0],best,flush=True)


if __name__=="__main__":main()

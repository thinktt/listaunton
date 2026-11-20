"""Replace the broad brow panel with one compact, measured wood reflection."""
from pathlib import Path
import argparse
import json
import math
import shutil
import sys
import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from fit_eye_reflection import display_transform,smooth_normal
from fit_surface_polish import read_reference
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera
from probe_carving import point_probe


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--variant",required=True);arg=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/arg.variant;out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(arg.source),load_ui=False);scene=bpy.context.scene
    probe=point_probe(scene);camdir=scene.camera.matrix_world.to_quaternion()@Vector((0,0,1))
    old=bpy.data.objects["Walnut | ear patch"];original_power=old.data.energy
    receivers=old.light_linking.receiver_collection;assert receivers
    settings=[(358,393,.75,.12),(367,394,.80,.15),(373,397,.92,.19),(368,400,.70,.14)]
    lamps=[];details=[]
    for i,(x,y,distance,size) in enumerate(settings):
        hit=probe(x+.5,y+.5);assert hit and hit[1].endswith("near swept ear")
        _,name,point,normal=hit
        n=smooth_normal(bpy.data.objects[name],point,normal)
        vector=(2*max(.001,camdir.dot(n))*n-camdir).normalized()
        data=bpy.data.lights.new(f"Brow reflection {i+1}","AREA");data.shape="DISK";data.size=size
        data.spread=math.radians(46);data.color=(1,.935,.875);data.energy=0
        ob=bpy.data.objects.new(data.name,data);scene.collection.objects.link(ob)
        ob.location=point+distance*vector;ob.rotation_euler=(point-ob.location).to_track_quat("-Z","Y").to_euler()
        ob.visible_diffuse=False;ob.visible_glossy=True;ob.light_linking.receiver_collection=receivers
        lamps.append(ob);details.append({"target":[x,y],"world":list(ob.location),"normal":list(n),"diameter":size})
    configure_render(scene,384);scene.cycles.use_denoising=False;scene.cycles.use_light_tree=False
    x0,y0,x1,y1=268,355,555,478;w=1254
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.05)/w;scene.render.border_max_x=(x1+.05)/w
    scene.render.border_min_y=(w-y1+.05)/w;scene.render.border_max_y=(w-y0+.05)/w
    source=read_pass(scene,out/"current.exr")[:,:,:3]
    old.data.energy=0;base=read_pass(scene,out/"no-brow-key.exr")[:,:,:3]
    transform=display_transform(scene)
    target=read_reference()[y0:y1,x0:x1,:3];yy,xx=np.indices(target.shape[:2]);xx+=x0;yy+=y0
    weight=1+8*np.exp(-((xx-368)/21)**2-((yy-394)/12)**2)
    weight*=1+.85*np.clip((target[:,:,1]-.34)/.48,0,1)
    def loss(linear):
        color=np.ascontiguousarray(linear,dtype=np.float32);transform.applyRGB(color)
        delta=color-target
        return float(np.average((.6*delta**2+np.sqrt(delta**2+.055**2)-.055).mean(2),weights=weight))
    # Apply the transform to copies so the measured linear bases remain usable.
    previous=loss(source.copy());base_loss=loss(base.copy())
    winner=(previous,None,original_power)
    for i,ob in enumerate(lamps):
        ob.data.energy=5
        response=np.maximum(read_pass(scene,out/(f"spot-{i}.exr"))[:,:,:3]-base,0)
        ob.data.energy=0
        def score(watts):return loss(base+response*(watts/5))
        powers=[0,.08,.16,.32,.64,1.25,2.5,5,10,20]
        keep=min(powers,key=score)
        for step in (1,.25,.0625,.015625):
            options=[max(0,keep-step),keep,keep+step];keep=min(options,key=score)
        error=score(keep);details[i].update({"watts":keep,"loss":error})
        if error<winner[0]:winner=(error,i,keep)
    if winner[1] is None:
        old.data.energy=original_power
    else:
        bpy.data.objects.remove(old,do_unlink=True)
    for i,ob in enumerate(lamps):
        if i==winner[1]:ob.data.energy=float(winner[2])
        else:bpy.data.objects.remove(ob,do_unlink=True)
    scene.render.use_border=False;scene.render.use_crop_to_border=False
    configure_render(scene,144);scene.cycles.use_light_tree=True
    cfg={"source_sha256":sha(arg.source),"samples":144,"measure_samples":384,"previous_loss":previous,
         "no_key_loss":base_loss,"chosen":winner[1],"chosen_watts":winner[2],"loss":winner[0],"trials":details,
         "method":"Compare the prior broad lamp against four compact real lamp placements. Retain at most one replacement and assess the reopened fixed and side renders."}
    scene["knight_brow_key_fit"]=json.dumps(cfg);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,144);render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    if (arg.source.parent/"pigment.png").is_file():shutil.copyfile(arg.source.parent/"pigment.png",out/"pigment.png")
    json_file(out/"parameters.json",cfg);print("KNIGHT_BROW_KEY",previous,winner,flush=True)


if __name__=="__main__":main()

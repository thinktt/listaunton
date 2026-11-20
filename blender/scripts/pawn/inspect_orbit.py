"""Inspect the actual full-round pawn and the hidden wood under neutral studio fill."""
import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import BUILD,ROOT,area,control,fixed_camera,render,save_json,setup,sha


def inspect(source,out):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene
    fixed_camera(scene);setup(scene,64);control(scene)
    out.mkdir(parents=True,exist_ok=True)
    cam=scene.camera
    cam.data.shift_x=cam.data.shift_y=0
    cam.data.ortho_scale=3.5
    scene.render.resolution_x=scene.render.resolution_y=420
    target=Vector((0,0,1.34))
    elevation=math.radians(12)
    records={}
    for lighting in ("studio","inspection"):
        if lighting=="inspection":
            for lamp in list(scene.objects):
                if lamp.type=="LIGHT":
                    bpy.data.objects.remove(lamp,do_unlink=True)
            scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.28
            key=area(scene,"Orbit inspection softbox",(0,-4,5),target,250,3.2,color=(1,.97,.94))
        for degree in (0,90,180,270):
            angle=math.radians(degree)
            direction=Vector((math.sin(angle)*math.cos(elevation),-math.cos(angle)*math.cos(elevation),math.sin(elevation)))
            cam.location=target+10*direction
            cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
            if lighting=="inspection":
                key.location=(3.1*math.sin(angle-.55),-3.1*math.cos(angle-.55),5.2)
                key.rotation_euler=(target-key.location).to_track_quat("-Z","Y").to_euler()
            path=out/(lighting+"-"+str(degree)+".png")
            render(scene,path)
            records[path.name]=sha(path)
    save_json(out/"orbit-check.json",{"source_sha256":sha(source),"elevation_degrees":12,"azimuth_degrees":[0,90,180,270],"inspection_light":"Neutral fill and a single broad key rotating with the inspection camera.","views":records})


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("directory")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    inspect(ROOT/a.source,BUILD/a.directory)

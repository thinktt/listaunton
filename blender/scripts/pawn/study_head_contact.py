"""Locate the actual head occlusion edge and identify illumination immediately around it."""
import argparse
import sys
from pathlib import Path

import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from fit_lighting import response
from mission_render import ROOT,BUILD,Surface,control,fixed_camera,save_json,setup,sha

W=np.array([.2126,.7152,.0722])


def edge(scene,body):
    surface=Surface(scene,body)
    result=[]
    for x in range(410,557):
        nominal=469+np.sqrt(117**2-(x-483)**2)
        lo=nominal-12;hi=nominal+14
        for _ in range(13):
            mid=(lo+hi)/2
            hit,_=surface.hit(x,mid)
            # The front limb of this ball occludes a shallow collar below Z 1.98.
            if hit.z>1.995:
                lo=mid
            else:
                hi=mid
        if not nominal-11.9<hi<nominal+13.9:
            raise ValueError((x,lo,hi))
        result.append([x,(lo+hi)/2])
    return result


def run(variants,out):
    out.mkdir(parents=True,exist_ok=True)
    edges={}
    for trial in variants:
        source=BUILD/trial/"pawn.blend"
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
        scene=bpy.context.scene
        body=control(scene)
        fixed_camera(scene)
        edges[trial]=edge(scene,body)
    coords=np.array(edges[variants[-1]])
    yy,xx=np.mgrid[:1254,:1254]
    distance=yy-np.interp(xx,coords[:,0],coords[:,1])
    masks={
        "left head edge":(xx>=434)&(xx<=462)&(distance>=-5)&(distance<-1),
        "left contact":(xx>=434)&(xx<=462)&(distance>=0)&(distance<5),
        "front contact":(xx>=469)&(xx<=501)&(distance>=0)&(distance<5),
        "right contact":(xx>=508)&(xx<=533)&(distance>=0)&(distance<5),
        "outer collar":(xx>=431)&(xx<=469)&(distance>=16)&(distance<27),
    }
    setup(scene,96)
    scene.render.use_border=True
    scene.render.border_min_x=390/1254;scene.render.border_max_x=575/1254
    scene.render.border_min_y=1-638/1254;scene.render.border_max_y=1-505/1254
    scene.render.use_crop_to_border=False
    scene.render.image_settings.file_format="OPEN_EXR"
    scene.render.image_settings.color_depth="32"
    lamps=[o for o in scene.objects if o.type=="LIGHT"]
    energy={o.name:o.data.energy for o in lamps}
    world=scene.world.node_tree.nodes["Background"].inputs["Strength"]
    world_strength=world.default_value
    for o in lamps:o.data.energy=0
    groups={}
    for lamp in lamps:
        name=lamp.name
        if lamp.visible_diffuse:group=name
        elif name.startswith(("Bowl ","Lip ")):group="collar reflections"
        elif "head" in name.lower() or "polish core" in name:group="head reflections"
        elif name.startswith("Foot "):group="foot reflections"
        elif name.startswith("Socket "):group="socket reflections"
        else:group="flare reflections"
        groups.setdefault(group,[]).append(lamp)
    values={}
    for group,members in [("world",[])]+list(groups.items()):
        world.default_value=world_strength if group=="world" else 0
        for lamp in members:lamp.data.energy=energy[lamp.name]
        linear=response(scene,out)
        assert linear.shape[:2]==(1254,1254)
        light=linear[:,:,:3]@W
        values[group]={name:round(float(light[m].mean()),7) for name,m in masks.items()}
        for lamp in members:lamp.data.energy=0
    save_json(out/"contact-measurement.json",{"source_sha256":sha(source),"edge_xy":edges,"mean_scene_linear_contribution":values,"pixels":{k:int(v.sum()) for k,v in masks.items()}})


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("output");p.add_argument("variants",nargs="+")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(a.variants,BUILD/a.output)

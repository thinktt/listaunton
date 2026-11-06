"""Fit diffuse studio fill to the actual shadow cast by the seated pawn ball."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
import PyOpenColorIO as ocio
sys.path.insert(0,str(Path(__file__).parent))
from capture_pigment import reference_srgb
from fit_lighting import nonnegative_fit,response
from mission_render import ROOT,BUILD,area,save_json
from polish_trial import open_source,save_trial


def add_panel(scene,spec):
    light=area(scene,spec["name"],spec["position"],spec["target"],spec["energy"],spec["size"],glossy=False)
    light.data.spread=math.radians(spec.get("spread",180))
    return light


def install(scene,panels):
    for lamp in list(scene.objects):
        if lamp.type=="LIGHT" and lamp.visible_diffuse and not lamp.visible_glossy:
            bpy.data.objects.remove(lamp,do_unlink=True)
    return [add_panel(scene,row) for row in panels]


def run(cfg):
    scene,body=open_source(cfg)
    if cfg.get("profiles"):
        from shape_trial import edit
        edit(body,cfg["profiles"])
    if "fitted_panels" in cfg:
        install(scene,cfg["fitted_panels"])
        save_trial(scene,cfg)
        return
    out=BUILD/cfg["variant"]
    out.mkdir(parents=True,exist_ok=True)
    all_specs=cfg["panels"]
    panels=install(scene,all_specs)
    for lamp in panels:lamp.data.energy=0
    fixed_lights=[o for o in scene.objects if o.type=="LIGHT" and o not in panels]
    old=[o.data.energy for o in fixed_lights]
    world=scene.world.node_tree.nodes["Background"].inputs["Strength"]
    world_power=world.default_value
    scene.render.image_settings.file_format="OPEN_EXR"
    scene.render.image_settings.color_depth="32"
    scene.cycles.samples=cfg.get("response_samples",80)
    base=response(scene,out)
    target=reference_srgb()
    y,x=np.mgrid[:1254,:1254]
    points=np.asarray(cfg["edge"])
    dy=y-np.interp(x,points[:,0],points[:,1])
    join=(x>=414)&(x<=551)&(dy>=-7)&(dy<=13)
    mask=(base[:,:,3]>.995)&((target.max(2)>.025)|join)&(join|((x%3==0)&(y%3==0)))
    # The edge coordinates come from ray hits on the actual trial mesh.
    weights=np.ones(mask.shape,np.float64)
    weights[join]=1.7
    weights[join&(dy>=-1.2)&(dy<5.1)&(target.mean(2)<.16)]=cfg["shadow_weight"]
    if cfg.get("narrow_shadow"):
        weights[join&(dy>5)&(dy<12)]=12
        weights[join&(dy>=-.5)&(dy<3.2)&(target.mean(2)<.10)]=cfg["shadow_weight"]*1.8
    weight=weights[mask]
    base=base[:,:,:3][mask]
    target=target[mask].astype(np.float64)
    for lamp in fixed_lights:lamp.data.energy=0
    world.default_value=0
    basis=[]
    scale=[]
    for lamp,spec in zip(panels,all_specs):
        lamp.data.energy=spec["energy"]
        pixels=response(scene,out)[:,:,:3][mask]
        peak=max(float(np.quantile(pixels.max(1),.97)),.001)
        basis.append(pixels/peak)
        scale.append(peak)
        lamp.data.energy=0
        print("PAWN_DIFFUSE_PANEL",lamp.name,flush=True)
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display=scene.display_settings.display_device,view=scene.view_settings.view_transform)
    processor=config.getProcessor(transform).getDefaultCPUProcessor()
    power,loss=nonnegative_fit(base,np.stack(basis,axis=-1),target,weight,processor,np.array(scale))
    fitted=[]
    for lamp,spec,factor,denom in zip(panels,all_specs,power,scale):
        energy=float(spec["energy"]*factor/denom)
        if energy<.04:
            bpy.data.objects.remove(lamp,do_unlink=True)
        else:
            lamp.data.energy=energy
            fitted.append(dict(spec,energy=energy))
    for lamp,energy in zip(fixed_lights,old):lamp.data.energy=energy
    world.default_value=world_power
    explicit=dict(cfg)
    explicit.pop("panels");explicit.pop("edge")
    explicit["fitted_panels"]=fitted
    save_json(out/"fit.json",{"method":"Actual one-light Cycles diffuse responses, nonnegative powers through the AgX display transform, stronger weight on the dark edge beneath the ball. Gloss reflectors preserved.","foreground_samples":len(target),"loss":loss,"panels":fitted})
    save_json(out/"reproduction.json",explicit)
    save_trial(scene,explicit)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(a.config.read_text()))

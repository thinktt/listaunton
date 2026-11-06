"""Fit compact real emitters to the distribution of light inside each head glint."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
import PyOpenColorIO as ocio
sys.path.insert(0,str(Path(__file__).parent))
from capture_pigment import reference_srgb
from fit_lighting import shape, make_light, response
from mission_render import ROOT, BUILD, Surface, save_json
from polish_trial import open_source, save_trial


def adjust(scene, cfg):
    for name, scale in cfg["broad_energy_scale"].items():
        scene.objects[name].data.energy *= scale


def run(cfg):
    scene, body = open_source(cfg)
    if cfg.get("varnish_config"):
        from apply_finish import apply
        apply(scene,body,json.loads((ROOT/cfg["varnish_config"]).read_text()))
    adjust(scene,cfg)
    if "fitted_lights" in cfg:
        for row in cfg["fitted_lights"]:
            make_light(scene,row)
        save_trial(scene,cfg)
        return
    out = BUILD/cfg["variant"]
    out.mkdir(parents=True,exist_ok=True)
    surface=Surface(scene,body)
    rows=[shape(surface,spec) for spec in cfg["cores"]]
    scene.render.image_settings.file_format="OPEN_EXR"
    scene.render.image_settings.color_depth="32"
    scene.cycles.samples=cfg.get("response_samples",96)
    base=response(scene,out)[:,:,:3]
    lights=[ob for ob in scene.objects if ob.type=="LIGHT"]
    old=[ob.data.energy for ob in lights]
    for ob in lights:
        ob.data.energy=0
    world=scene.world.node_tree.nodes["Background"].inputs["Strength"]
    world_power=world.default_value
    world.default_value=0
    target=reference_srgb()
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display=scene.display_settings.display_device,view=scene.view_settings.view_transform)
    processor=config.getProcessor(transform).getDefaultCPUProcessor()
    reports=[]
    for spec,row in zip(cfg["cores"],rows):
        lamp=make_light(scene,row)
        isolated=response(scene,out)[:,:,:3]/row["energy"]
        x,y=spec["pixel"]
        rx,ry=spec["region_half_size"]
        roi=np.s_[y-ry:y+ry,x-rx:x+rx]
        region=base[roi].copy()
        delta=isolated[roi]
        q=[.5,.9,.99]
        weights=np.array([.24,.53,.23])
        desired=np.quantile(target[roi]@weights,q)
        def levels(energy):
            rgb=np.ascontiguousarray(region+delta*energy,dtype=np.float32)
            processor.applyRGB(rgb)
            return np.quantile(rgb@weights,q)
        def loss(energy):
            return float(np.dot([.22,.33,.45],(levels(energy)-desired)**2))
        # One-dimensional bounded minimization. Each reflector has its own
        # small target region and the previous regions retain their powers.
        lo,hi=0.,cfg.get("max_watts",18.)
        for _ in range(24):
            left=lo+(hi-lo)/3;right=hi-(hi-lo)/3
            if loss(left)<loss(right):
                hi=right
            else:
                lo=left
        energy=(hi+lo)/2
        reports.append({"name":row["name"],"percentiles":q,"reference":desired.tolist(),"without":levels(0).tolist(),"predicted":levels(energy).tolist(),"watts":energy})
        row["energy"]=energy
        base+=isolated*energy
        lamp.data.energy=0
        print("PAWN_GLINT_CORE",row["name"],energy,flush=True)
    for ob,energy in zip(lights,old):
        ob.data.energy=energy
    world.default_value=world_power
    for row in rows:
        scene.objects[row["name"]].data.energy=row["energy"]
    explicit=dict(cfg)
    explicit.pop("cores")
    explicit["fitted_lights"]=rows
    save_json(out/"fit.json",{"method":"Real one-light Cycles responses. Match the median, 90th and 99th percentiles of displayed glint brightness in local registered rectangles. Evaluate the actual full render independently.","regions":reports})
    save_json(out/"reproduction.json",explicit)
    save_trial(scene,explicit)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("config",type=Path)
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(args.config.read_text()))

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
            if row["energy"]>.00001:
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
        if float(delta.max())<1e-7:
            row["energy"]=0.
            lamp.data.energy=0.
            reports.append({"name":row["name"],"watts":0.,"reason":"No measured response in its target region."})
            continue
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
        # Compact sources can saturate the display across most of the watt
        # range. Bracket the useful response in log watts before refining;
        # two equally clipped probes cannot rule out a dimmer solution.
        ceiling=cfg.get("max_watts",18.)
        grid=np.r_[0.,np.geomspace(1e-6,ceiling,44)]
        costs=[loss(energy) for energy in grid]
        index=int(np.argmin(costs))
        energy=float(grid[index]);best=costs[index]
        lo=float(grid[max(index-1,0)]);hi=float(grid[min(index+1,len(grid)-1)])
        for _ in range(24):
            left=lo+(hi-lo)/3;right=hi-(hi-lo)/3
            a,b=loss(left),loss(right)
            if a<best:energy,best=left,a
            if b<best:energy,best=right,b
            if a<=b:
                hi=right
            else:
                lo=left
        assert best<=costs[0]
        reports.append({"name":row["name"],"percentiles":q,"reference":desired.tolist(),"without":levels(0).tolist(),"predicted":levels(energy).tolist(),"loss_without":costs[0],"loss_with":best,"watts":energy})
        row["energy"]=energy
        base+=isolated*energy
        lamp.data.energy=0
        print("PAWN_GLINT_CORE",row["name"],energy,flush=True)
    for ob,energy in zip(lights,old):
        ob.data.energy=energy
    world.default_value=world_power
    for row in rows:
        lamp=scene.objects[row["name"]]
        if row["energy"]>.00001:
            lamp.data.energy=row["energy"]
        else:
            bpy.data.objects.remove(lamp,do_unlink=True)
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

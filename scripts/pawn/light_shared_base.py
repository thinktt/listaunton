"""Measure the lights on the transferred turning and fit their real Cycles powers."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
import PyOpenColorIO as ocio

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from capture_pigment import reference_srgb
from fit_lighting import make_light, nonnegative_fit, response, shape
from mission_render import ASSETS, ROOT, Surface, control, fixed_camera, render, save_json, setup, sha


def lighting_group(obj):
    name = obj.name.lower()
    if obj.visible_diffuse:
        if name.startswith("front shadow"):
            return "front diffuse"
        return "surround diffuse"
    if "head" in name or "polish core" in name:
        return "head reflections"
    if "foot" in name or "groove" in name:
        return "foot reflections"
    if "collar" in name or "stem" in name:
        return "stem and collar reflections"
    if "socket" in name:
        return "socket reflections"
    return "flare reflections"


def fit(scene, body, directory, settings):
    lamps = [o for o in scene.objects if o.type == "LIGHT"]
    groups = {}
    for lamp in lamps:
        groups.setdefault(lighting_group(lamp), []).append(lamp)
    align = json.loads((ASSETS/"original-alignment.json").read_text())
    scale = align["scale"]*300/1254
    offset = np.array([align["x"],align["y"]])*3
    surface = Surface(scene, body)
    cards = []
    for spec in settings["cards"]:
        loc = (np.asarray(spec["native_xy"])-offset)/scale
        row = shape(surface, dict(name=spec["name"], pixel=loc.tolist(),
                    half_axes=(np.asarray(spec["native_half_axes"])/scale).tolist(),
                    angle=spec["angle"], color=spec["color"], spread=spec.get("spread",30)))
        lamp = make_light(scene,row)
        lamp.data.energy = spec["probe_watts"]
        groups[lamp.name] = [lamp]
        cards.append(row)
    energy = {lamp.name:float(lamp.data.energy) for group in groups.values() for lamp in group}
    for group in groups.values():
        for lamp in group:
            lamp.data.energy = 0
    adaptive = scene.cycles.use_adaptive_sampling
    setup(scene,48)
    scene.cycles.use_denoising = False
    scene.cycles.use_adaptive_sampling = False
    scene.render.resolution_percentage = 50
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    world = scene.world.node_tree.nodes["Background"].inputs["Strength"]
    world_power = world.default_value
    raw = response(scene,directory)
    source = reference_srgb().reshape(627,2,627,2,3).mean((1,3))
    original = np.load(directory.parent/"registered-original.npy").reshape(627,2,627,2,3).mean((1,3))
    y,x = np.indices(source.shape[:2])
    target_mix = np.where(y*2<590,settings["original_head_weight"],settings["original_weight"])[:,:,None]
    target = original*target_mix+source*(1-target_mix)
    valid = (raw[:,:,3]>.995)&(original.max(2)>.045)&(source.max(2)>.045)&(y%2==0)&(x%2==0)
    base = raw[:,:,:3][valid]
    world.default_value = 0
    columns=[]
    for key,group in groups.items():
        for lamp in group:
            lamp.data.energy = energy[lamp.name]
        columns.append(response(scene,directory)[:,:,:3][valid])
        for lamp in group:
            lamp.data.energy = 0
    weights = 1.+1.5*np.clip((target[valid].mean(1)-.3)/.42,0,1)
    config = ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    transform = ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR, display=scene.display_settings.display_device,
                                          view=scene.view_settings.view_transform)
    processor = config.getProcessor(transform).getDefaultCPUProcessor()
    initial = np.array([0. if group in {r["name"] for r in cards} else 1. for group in groups])
    factors, losses = nonnegative_fit(base,np.stack(columns,axis=-1),target[valid],weights,processor,initial)
    factors = np.clip(factors,0,settings["max_gain"])
    world.default_value = world_power
    for group,factor in zip(groups.values(),factors):
        for lamp in group:
            lamp.data.energy = energy[lamp.name]*factor
    scene.cycles.use_adaptive_sampling = adaptive
    final_powers = {lamp.name:float(lamp.data.energy) for group in groups.values() for lamp in group}
    for row in cards:
        row["energy"] = final_powers[row["name"]]
    return dict(groups=dict(zip(groups,map(float,factors))), lamps=final_powers, cards=cards,
                fit_loss=losses, foreground_pixels=int(valid.sum()))


def run(settings, replay=None):
    base = ROOT/settings["base"]
    out = ROOT/settings["output"]
    out.mkdir(parents=True,exist_ok=True)
    assert sha(base/"pawn.blend")==json.loads((base/"geometry.json").read_text())["model_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(base/"pawn.blend"),load_ui=False)
    scene = bpy.context.scene
    body = control(scene)
    fixed_camera(scene)
    if replay:
        record = json.loads(replay.read_text())
        for row in record["cards"]:
            make_light(scene,row)
        for lamp,power in record["lamps"].items():
            scene.objects[lamp].data.energy=power
    else:
        record=fit(scene,body,out,settings)
    record["settings"]=settings
    save_json(out/"lights.json",record)
    setup(scene,settings["samples"])
    fixed_camera(scene)
    scene["pawn_accepted_trial"]=out.name
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"pawn.blend"),compress=True)
    render(scene,out/"fixed.png")
    side=bpy.data.scenes[scene["pawn_side_scene"]]
    assert control(side) is body
    bpy.context.window.scene=side
    setup(side,settings["samples"])
    render(side,out/"side.png")
    geom=json.loads((base/"geometry.json").read_text())
    geom.update(model_sha256=sha(out/"pawn.blend"),fixed_sha256=sha(out/"fixed.png"),side_sha256=sha(out/"side.png"))
    save_json(out/"geometry.json",geom)
    print("PAWN_SHARED_TURNING_LIGHT",out.name,record["groups"],flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("settings",type=Path)
    parser.add_argument("--replay",type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(args.settings.read_text()),args.replay)

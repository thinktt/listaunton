"""Build and render one isolated pawn trial. Run in Blender with -- CONFIG."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT, BUILD, Surface, area, control, fixed_camera, render, save_json, setup, sha, side_camera

def head_profile(body, cfg):
    """Lift the widest section, retaining the actual apex, foot and joined seat."""
    coordinates = np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)
    head = coordinates[42:]
    radii = np.linalg.norm(head[:,:,:2],axis=2).mean(axis=1)
    equator = int(np.argmax(radii))
    z = head[:,0,2]
    center, top, seat = z[equator], z[-1], z[0]
    # Continuous height redistribution. The lower spherical flank meets the
    # existing seat at exactly its original height and contact radius.
    weight = np.where(z < center, (z-seat)/(center-seat), (top-z)/(top-center))
    head[:,:,2] += (cfg["equator_lift"]*weight)[:,None]
    body.data.vertices.foreach_set("co",coordinates.reshape(-1))
    body.data.update()

def wood_material(cfg):
    material = bpy.data.materials.new("Pawn | polished dark walnut")
    material.use_nodes = True
    nodes,links = material.node_tree.nodes,material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = cfg.get("roughness",.26)
    bsdf.inputs["Coat Weight"].default_value = cfg.get("coat",.23)
    bsdf.inputs["Coat Roughness"].default_value = cfg.get("coat_roughness",.14)
    texcoord = nodes.new("ShaderNodeTexCoord")
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "MULTIPLY"
    scale.inputs[1].default_value = (6,6,60)
    links.new(texcoord.outputs["Object"],scale.inputs[0])
    grain = nodes.new("ShaderNodeTexNoise")
    grain.name = "Continuous turned grain"
    grain.inputs["Scale"].default_value = 1
    grain.inputs["Detail"].default_value = 4.5
    grain.inputs["Distortion"].default_value = .3
    links.new(scale.outputs[0],grain.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .17
    ramp.color_ramp.elements[0].color = (.022,.006,.0016,1)
    ramp.color_ramp.elements[1].position = .82
    ramp.color_ramp.elements[1].color = (.19,.059,.016,1)
    links.new(grain.outputs["Fac"],ramp.inputs[0])
    links.new(ramp.outputs["Color"],bsdf.inputs["Base Color"])
    pores = nodes.new("ShaderNodeTexNoise")
    pores.inputs["Scale"].default_value = 175
    pores.inputs["Detail"].default_value = 2
    links.new(texcoord.outputs["Object"],pores.inputs["Vector"])
    bump = nodes.new("ShaderNodeBump")
    bump.name = "Fine varnish relief"
    bump.inputs["Strength"].default_value = .16
    bump.inputs["Distance"].default_value = .002
    links.new(pores.outputs["Fac"],bump.inputs["Height"])
    links.new(bump.outputs["Normal"],bsdf.inputs["Normal"])
    links.new(bump.outputs["Normal"],bsdf.inputs["Coat Normal"])
    material.diffuse_color = (.10,.032,.009,1)
    return material

def reseat_sphere_and_foot(body, cfg):
    """Keep the spherical head and its contact width; flatten the foot's sole."""
    co = np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)
    profile = json.loads((ROOT/"scripts/pawn/profile.json").read_text())
    align = json.loads((ROOT/"assets/pawn/original-alignment.json").read_text())
    units = 1254 / (300*align["scale"]*profile["scale"])
    vertical = units / math.cos(math.radians(54))
    floor = float(co[0,0,2])
    old_floor_y = profile["profile"][0][1]
    lift = (old_floor_y-cfg["foot_profile"][0][1])*vertical
    for i,(radius,axis_y) in enumerate(cfg["foot_profile"]):
        current_radius = np.linalg.norm(co[i,:,:2],axis=1)
        co[i,:,:2] *= (radius*units/current_radius)[:,None]
        co[i,:,2] = floor + (old_floor_y-axis_y)*vertical
    if cfg.get("preserve_seat"):
        head = co[42:]
        equator = np.argmax(np.linalg.norm(head[:,0,:2],axis=1))
        z = head[:,0,2]
        lift_weight = np.clip((z-z[0])/(z[equator]-z[0]),0,1)
        head[:,:,2] += lift*lift_weight[:,None]
    else:
        co[40,:,2] += .20*lift
        co[41,:,2] += .62*lift
        co[42:,:,2] += lift
    body.data.vertices.foreach_set("co",co.reshape(-1))
    body.data.update()

def studio(scene, body, cfg):
    for obj in list(scene.objects):
        if obj.type == "LIGHT":
            bpy.data.objects.remove(obj,do_unlink=True)
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1,1,1,1)
    bg.inputs["Strength"].default_value = cfg.get("world",.09)
    for item in cfg["diffuse"]:
        area(scene,item["name"],item["position"],[0,0,1.35],item["energy"],item["size"],glossy=False)
    surface = Surface(scene,body)
    for item in cfg["reflectors"]:
        hit,normal = surface.hit(*item["pixel"])
        direction = (-surface.back).reflect(normal)
        pos = hit + direction*item.get("distance",4.5)
        area(scene,item["name"],pos,hit,item["energy"],item["size"],diffuse=False,
             color=item.get("color",[1,.85,.72]),size_y=item.get("size_y"))

def prepare(cfg):
    source = ROOT / cfg["source"]
    assert sha(source) == cfg["source_sha256"], "Trial source changed"
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene = bpy.context.scene
    fixed_camera(scene)
    body = control(scene)
    setup(scene,cfg.get("samples",64))
    clay = body.data.materials[0]
    if "head" in cfg:
        head_profile(body,cfg["head"])
    if "round_head" in cfg:
        reseat_sphere_and_foot(body,cfg["round_head"])
    if "wood" in cfg:
        body.data.materials[0] = wood_material(cfg["wood"])
    if "studio" in cfg:
        studio(scene,body,cfg["studio"])
    return scene,body,clay

def run(cfg):
    scene,body,clay=prepare(cfg)
    directory = BUILD / cfg["variant"]
    directory.mkdir(parents=True, exist_ok=True)
    scene["pawn_mission_variant"] = cfg["variant"]
    scene["pawn_mission_config"] = json.dumps(cfg,sort_keys=True)
    scene.render.filepath = str(directory/"fixed.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(directory/"pawn.blend"))
    render(scene,directory/"fixed.png")
    current = body.data.materials[0]
    if "wood" in cfg:
        body.data.materials[0] = clay
        render(scene,directory/"clay.png")
        body.data.materials[0] = current
    side_camera(scene)
    render(scene,directory/"side.png")
    save_json(directory/"manifest.json",dict(config=cfg,source_sha256=sha(ROOT/cfg["source"]),model_sha256=sha(directory/"pawn.blend"),render_sha256=sha(directory/"fixed.png")))
    print("PAWN_TRIAL_DONE",cfg["variant"],flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config",type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(args.config.read_text(encoding="utf-8-sig")))

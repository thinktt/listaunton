"""Attach a packed diffuse atlas to the editable pawn, then render fixed and side views."""
import argparse
import json
import sys
from pathlib import Path

import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT, BUILD, control, fixed_camera, render, save_json, setup, sha, side_camera
from capture_pigment import UV_NAME,add_lathe_uv

def run(cfg):
    source=ROOT/cfg["source"]; texture=ROOT/cfg["texture"]
    assert sha(source)==cfg["source_sha256"] and sha(texture)==cfg["texture_sha256"]
    if "geometry_config" in cfg:
        from mission_trial import prepare
        geometry=json.loads((ROOT/cfg["geometry_config"]).read_text())
        assert geometry["source_sha256"]==cfg["source_sha256"]
        scene,body,_=prepare(geometry)
    else:
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
        scene=bpy.context.scene;body=control(scene)
    if "rig_config" in cfg:
        from fit_lighting import clear_reflectors, make_light
        from shape_trial import edit
        rig=json.loads((ROOT/cfg["rig_config"]).read_text())
        assert rig["source_sha256"]==cfg["source_sha256"]
        edit(body,rig["profiles"])
        if "world_strength" in rig:
            scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=rig["world_strength"]
        if "fitted_panels" in rig:
            from fit_diffuse import install
            install(scene,rig["fitted_panels"])
        clear_reflectors(scene,rig.get("keep_reflectors",()))
        for row in rig["fitted_lights"]:
            if row["energy"]>.00001:
                make_light(scene,row)
    fixed_camera(scene);setup(scene,cfg.get("samples",96));add_lathe_uv(body)
    material=body.data.materials[0]
    nodes,links=material.node_tree.nodes,material.node_tree.links
    bs=nodes.get("Principled BSDF")
    image=bpy.data.images.load(str(texture),check_existing=False)
    image.colorspace_settings.name="sRGB"
    image.pack()
    previous=nodes.get("Pawn walnut pigment")
    if previous:
        # Existing grain-relief nodes may still use this source. Color and
        # relief can then be compared independently with the same light rig.
        previous.name="Earlier pigment | "+previous.image.name
    pigment=nodes.new("ShaderNodeTexImage");pigment.name="Pawn walnut pigment";pigment.image=image
    uv=nodes.new("ShaderNodeUVMap");uv.uv_map=UV_NAME
    links.new(uv.outputs["UV"],pigment.inputs["Vector"])
    links.new(pigment.outputs["Color"],bs.inputs["Base Color"])
    if nodes.get("Matte walnut"):
        links.new(pigment.outputs["Color"],nodes["Matte walnut"].inputs["Color"])
    if previous and not any(output.is_linked for output in previous.outputs):
        old_image=previous.image
        old_uv=previous.inputs["Vector"].links[0].from_node if previous.inputs["Vector"].is_linked else None
        nodes.remove(previous)
        if old_uv and old_uv.type=="UVMAP" and not any(output.is_linked for output in old_uv.outputs):
            nodes.remove(old_uv)
        if old_image.users==0:
            bpy.data.images.remove(old_image)
    if cfg.get("recess_config"):
        from recess_finish import add_finish
        add_finish(material,json.loads((ROOT/cfg["recess_config"]).read_text()))
    directory=BUILD/cfg["variant"];directory.mkdir(parents=True,exist_ok=True)
    scene["pawn_texture_path"]=cfg["texture"]
    scene["pawn_texture_sha256"]=cfg["texture_sha256"]
    scene["pawn_mission_variant"]=cfg["variant"]
    scene["reconstruction"]="Reconstruction from original Lichess pawn and selected black candidate 2. Assumed 54-degree camera. Usable packed walnut pigment with live Cycles reflections."
    scene.render.filepath=str(directory/"fixed.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(directory/"pawn.blend"))
    render(scene,directory/"fixed.png")
    side_camera(scene);render(scene,directory/"side.png")
    save_json(directory/"manifest.json",{"config":cfg,"model_sha256":sha(directory/"pawn.blend"),"render_sha256":sha(directory/"fixed.png"),"source_sha256":sha(source),"texture_sha256":sha(texture)})
    print("PAWN_ATLAS_TRIAL_DONE",cfg["variant"],flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(args.config.read_text(encoding="utf-8-sig")))

"""Attach bounded grain relief to the wood/varnish and render a controlled trial."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT, BUILD, setup, fixed_camera, control, render, side_camera, sha, save_json

def finish(scene,body,cfg):
    mat=body.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links
    bs=n.get("Principled BSDF")
    pigment=n["Pawn walnut pigment"]
    gray=n.new("ShaderNodeRGBToBW");l.new(pigment.outputs["Color"],gray.inputs[0])
    soft=n.new("ShaderNodeMath");soft.operation="POWER";soft.inputs[1].default_value=.4
    l.new(gray.outputs[0],soft.inputs[0])
    bump=n.new("ShaderNodeBump");bump.name="Walnut grain relief"
    bump.inputs["Distance"].default_value=cfg["distance"];bump.inputs["Strength"].default_value=cfg["strength"]
    l.new(soft.outputs[0],bump.inputs["Height"])
    previous=bs.inputs["Normal"].links[0].from_socket
    l.new(previous,bump.inputs["Normal"])
    l.new(bump.outputs["Normal"],bs.inputs["Normal"]);l.new(bump.outputs["Normal"],bs.inputs["Coat Normal"])
    bs.inputs["Roughness"].default_value=cfg["roughness"]
    bs.inputs["Coat Roughness"].default_value=cfg["coat_roughness"]

def save_trial(scene,cfg):
    directory=BUILD/cfg["variant"];directory.mkdir(parents=True,exist_ok=True)
    scene["pawn_mission_variant"]=cfg["variant"];scene["pawn_trial_config"]=json.dumps(cfg,sort_keys=True)
    setup(scene,cfg.get("samples",96));scene.render.filepath=str(directory/"fixed.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(directory/"pawn.blend"))
    render(scene,directory/"fixed.png");side_camera(scene);render(scene,directory/"side.png")
    save_json(directory/"manifest.json",{"config":cfg,"model_sha256":sha(directory/"pawn.blend"),"render_sha256":sha(directory/"fixed.png")})
    print("PAWN_TRIAL_COMPLETE",cfg["variant"],flush=True)

def open_source(cfg):
    source=ROOT/cfg["source"];assert sha(source)==cfg["source_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;fixed_camera(scene);setup(scene,cfg.get("samples",96))
    return scene,control(scene)

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("config",type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:]);cfg=json.loads(args.config.read_text())
    scene,body=open_source(cfg);finish(scene,body,cfg["finish"]);save_trial(scene,cfg)

"""Apply listed meridian changes to the current editable pawn; preserve camera and UVs."""
import argparse,json,math,sys
from pathlib import Path
import bpy
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT, BUILD, fixed_camera, render, side_camera, save_json, sha
from polish_trial import open_source

def edit(body,profiles):
    co=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,96,3)
    guide=json.loads((ROOT/"scripts/pawn/profile.json").read_text())
    align=json.loads((ROOT/"assets/pawn/original-alignment.json").read_text())
    scale=1254/(300*align["scale"]*guide["scale"])
    for key,(radius,axis) in profiles.items():
        i=int(key);r=np.linalg.norm(co[i,:,:2],axis=1)
        co[i,:,:2]*=(radius*scale/r)[:,None]
        co[i,:,2]=(guide["y0"]-axis)*scale/math.cos(math.radians(54))
    body.data.vertices.foreach_set("co",co.reshape(-1));body.data.update()

def run(cfg):
    scene,body=open_source(cfg)
    edit(body,cfg["profiles"]);fixed_camera(scene)
    out=BUILD/cfg["variant"];out.mkdir(parents=True,exist_ok=True)
    scene["pawn_mission_variant"]=cfg["variant"];scene["pawn_trial_config"]=json.dumps(cfg,sort_keys=True)
    scene.render.filepath=str(out/"fixed.png")
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"pawn.blend"));render(scene,out/"fixed.png")
    wood=body.data.materials[0]
    clay=bpy.data.materials.new("Pawn curvature study");clay.use_nodes=True
    bs=clay.node_tree.nodes.get("Principled BSDF");bs.inputs["Base Color"].default_value=(.28,.30,.34,1);bs.inputs["Roughness"].default_value=.30
    body.data.materials[0]=clay;render(scene,out/"clay.png")
    side_camera(scene);render(scene,out/"clay-side.png")
    body.data.materials[0]=wood;render(scene,out/"side.png")
    save_json(out/"manifest.json",{"config":cfg,"model_sha256":sha(out/"pawn.blend"),"render_sha256":sha(out/"fixed.png")})
    print("PAWN_CURVATURE_TRIAL_DONE",cfg["variant"],flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(json.loads(a.config.read_text()))

"""Rebuild the finer collar finish from the preserved tenth pawn checkpoint."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,sha
from polish_trial import open_source,save_trial
from apply_finish import apply as finish
from micro_normals import apply as slopes
from mix_varnish import validate

def run(cfg):
    scene,body=open_source(cfg)
    finish(scene,body,cfg["finish"])
    slopes(scene,body,cfg["slopes"])
    path=ROOT/cfg["texture"]
    assert sha(path)==cfg["texture_sha256"]
    image=bpy.data.images.load(str(path),check_existing=False)
    image.colorspace_settings.name="sRGB";image.pack()
    body.data.materials[0].node_tree.nodes["Pawn walnut pigment"].image=image
    scene["pawn_texture_path"]=cfg["texture"];scene["pawn_texture_sha256"]=cfg["texture_sha256"]
    scene.cycles.use_light_tree=cfg["light_tree"];scene.cycles.seed=cfg["seed"]
    scene["pawn_sampling"]=json.dumps({"samples":cfg["samples"],"light_tree":cfg["light_tree"],"seed":cfg["seed"]},sort_keys=True)
    validate(scene,body);save_trial(scene,cfg)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(json.loads(a.config.read_text(encoding="utf-8")))

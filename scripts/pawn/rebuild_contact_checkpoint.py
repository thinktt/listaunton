"""Rebuild the contact finish from the preserved ninth pawn and explicit inputs."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,sha
from polish_trial import open_source,save_trial
from fit_lighting import clear_reflectors,make_light
from micro_normals import apply as apply_slopes
from mix_varnish import install as matte,validate
from shift_contact_lights import shift

def run(cfg):
    scene,body=open_source(cfg)
    names={row["name"] for row in cfg["reflectors"]}
    keep=[o.name for o in scene.objects if o.type=="LIGHT" and o.name not in names]
    clear_reflectors(scene,keep)
    for row in cfg["reflectors"]:make_light(scene,row)
    apply_slopes(scene,body,cfg["slopes"])
    matte(scene,body,cfg["matte_band"])
    shift(scene,cfg["shadow_lights"])
    path=ROOT/cfg["texture"]
    assert sha(path)==cfg["texture_sha256"]
    image=bpy.data.images.load(str(path),check_existing=False)
    image.colorspace_settings.name="sRGB";image.pack()
    body.data.materials[0].node_tree.nodes["Pawn walnut pigment"].image=image
    scene["pawn_texture_path"]=cfg["texture"]
    scene["pawn_texture_sha256"]=cfg["texture_sha256"]
    validate(scene,body)
    save_trial(scene,cfg)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(a.config.read_text()))

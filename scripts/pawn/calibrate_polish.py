"""Measure roughness and polish-strength changes on the same packed pawn material."""
import argparse
import json
import sys
from pathlib import Path

import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import BUILD,render,save_json,sha
from polish_trial import open_source


def scale_input(nodes,links,socket):
    prev=socket.links[0].from_socket if socket.is_linked else None
    mult=nodes.new("ShaderNodeMath")
    mult.operation="MULTIPLY"
    if prev:
        links.new(prev,mult.inputs[0])
    else:
        mult.inputs[0].default_value=socket.default_value
    mult.inputs[1].default_value=1
    links.new(mult.outputs[0],socket)
    return mult.inputs[1]


def run(cfg):
    scene,body=open_source(cfg)
    tree=body.data.materials[0].node_tree
    shader=tree.nodes["Principled BSDF"]
    controls={name:scale_input(tree.nodes,tree.links,shader.inputs[name]) for name in ("Roughness","Coat Roughness","Specular IOR Level","Coat Weight")}
    out=BUILD/cfg["measurement"]
    out.mkdir(parents=True,exist_ok=True)
    first_seed=scene.cycles.seed
    poses={}
    for i,rough in enumerate(cfg["rough_scales"]):
        for j,gloss in enumerate(cfg["polish_scales"]):
            controls["Roughness"].default_value=controls["Coat Roughness"].default_value=rough
            controls["Specular IOR Level"].default_value=controls["Coat Weight"].default_value=gloss
            name="flat" if rough==1 and gloss==1 else f"response-{i}-{j}"
            path=out/(name+".png")
            render(scene,path)
            poses[name]={"rough":rough,"polish":gloss,"sha256":sha(path)}
    for control in controls.values():control.default_value=1
    scene.cycles.seed=first_seed+31
    independent=out/"flat-independent.png"
    render(scene,independent)
    save_json(out/"measurement.json",{"config":cfg,"poses":poses,"independent_sha256":sha(independent),"method":"Actual fixed-view Cycles responses for nine combinations of roughness and reflectance on wood and coat. A second seed measures where noise competes with the material signal."})


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(json.loads(a.config.read_text()))

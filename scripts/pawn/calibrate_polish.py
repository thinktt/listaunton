"""Measure roughness and polish-strength changes on the same packed pawn material."""
import argparse
import json
import sys
from pathlib import Path

import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import BUILD,render,save_json,sha
from polish_trial import open_source


def scale_input(nodes,links,socket,band=None):
    prev=socket.links[0].from_socket if socket.is_linked else None
    mult=nodes.new("ShaderNodeMath")
    mult.operation="MULTIPLY"
    if prev:
        links.new(prev,mult.inputs[0])
    else:
        mult.inputs[0].default_value=socket.default_value
    mult.inputs[1].default_value=1
    links.new(mult.outputs[0],socket)
    if band is not None:
        offset=nodes.new("ShaderNodeMath");offset.operation="SUBTRACT"
        offset.inputs[0].default_value=offset.inputs[1].default_value=1
        factor=nodes.new("ShaderNodeMath");factor.operation="MULTIPLY_ADD"
        links.new(band,factor.inputs[0]);links.new(offset.outputs[0],factor.inputs[1]);factor.inputs[2].default_value=1
        links.new(factor.outputs[0],mult.inputs[1])
        return offset.inputs[0]
    return mult.inputs[1]


def run(cfg):
    scene,body=open_source(cfg)
    tree=body.data.materials[0].node_tree
    shader=tree.nodes["Principled BSDF"]
    band=None
    if cfg.get("uv_focus"):
        a,b,c,d=cfg["uv_focus"]
        uv=tree.nodes.new("ShaderNodeUVMap");uv.uv_map="Pawn pigment"
        split=tree.nodes.new("ShaderNodeSeparateXYZ");tree.links.new(uv.outputs["UV"],split.inputs["Vector"])
        ramps=[]
        for lo,hi,start,end in ((a,b,0,1),(c,d,1,0)):
            ramp=tree.nodes.new("ShaderNodeMapRange");ramp.interpolation_type="SMOOTHSTEP"
            for key,value in (("From Min",lo),("From Max",hi),("To Min",start),("To Max",end)):ramp.inputs[key].default_value=value
            tree.links.new(split.outputs["Y"],ramp.inputs["Value"]);ramps.append(ramp)
        product=tree.nodes.new("ShaderNodeMath");product.operation="MULTIPLY"
        tree.links.new(ramps[0].outputs[0],product.inputs[0]);tree.links.new(ramps[1].outputs[0],product.inputs[1]);band=product.outputs[0]
    controls={name:scale_input(tree.nodes,tree.links,shader.inputs[name],band) for name in ("Roughness","Coat Roughness","Specular IOR Level","Coat Weight")}
    if cfg.get("crop"):
        x0,y0,x1,y1=cfg["crop"]
        scene.render.use_border=True;scene.render.use_crop_to_border=False
        scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
        scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
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

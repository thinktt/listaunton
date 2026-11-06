"""Measure or attach bounded tangent slopes on top of the pawn's existing grain."""
import argparse
import json
import sys
from pathlib import Path

import bpy
sys.path.insert(0,str(Path(__file__).parent))
from capture_pigment import UV_NAME
from mission_render import ROOT, BUILD, render, save_json, sha
from polish_trial import open_source, save_trial


def slope_nodes(body):
    material=body.data.materials[0]
    nodes,links=material.node_tree.nodes,material.node_tree.links
    shader=nodes["Principled BSDF"]
    old_normal=shader.inputs["Normal"].links[0].from_socket
    tilt=nodes.new("ShaderNodeNormalMap")
    tilt.uv_map=UV_NAME
    tilt.name="Measured fine varnish slopes"
    flat=nodes.new("ShaderNodeNormalMap")
    flat.uv_map=UV_NAME
    flat.inputs["Color"].default_value=(.5,.5,1,1)
    difference=nodes.new("ShaderNodeVectorMath")
    difference.operation="SUBTRACT"
    links.new(tilt.outputs["Normal"],difference.inputs[0])
    links.new(flat.outputs["Normal"],difference.inputs[1])
    combine=nodes.new("ShaderNodeVectorMath")
    combine.operation="ADD"
    links.new(old_normal,combine.inputs[0])
    links.new(difference.outputs[0],combine.inputs[1])
    unit=nodes.new("ShaderNodeVectorMath")
    unit.operation="NORMALIZE"
    links.new(combine.outputs[0],unit.inputs[0])
    links.new(unit.outputs[0],shader.inputs["Normal"])
    links.new(unit.outputs[0],shader.inputs["Coat Normal"])
    return material,tilt


def measure(cfg):
    scene,body=open_source(cfg)
    _,tilt=slope_nodes(body)
    out=BUILD/cfg["measurement"]
    out.mkdir(parents=True,exist_ok=True)
    step=cfg["step"]
    results={}
    for name,dx,dy in (("flat",0,0),("u-plus",step,0),("u-minus",-step,0),("v-plus",0,step),("v-minus",0,-step)):
        tilt.inputs["Color"].default_value=(.5+.5*dx,.5+.5*dy,1,1)
        path=out/(name+".png")
        render(scene,path)
        results[name]=sha(path)
    save_json(out/"measurement.json",{"config":cfg,"pass_sha256":results,"method":"Five actual Cycles renders with slopes in the real wood UV tangent frame. Hold all lights, pigment, roughness, existing grain, geometry and camera."})


def apply(scene,body,cfg):
    path=ROOT/cfg["texture"]
    assert sha(path)==cfg["texture_sha256"]
    material,tilt=slope_nodes(body)
    nodes,links=material.node_tree.nodes,material.node_tree.links
    image=bpy.data.images.load(str(path),check_existing=False)
    image.colorspace_settings.name="Non-Color"
    image.pack()
    tex=nodes.new("ShaderNodeTexImage")
    tex.name="Pawn fine slope atlas"
    tex.image=image
    uv=nodes["Pawn walnut pigment"].inputs["Vector"].links[0].from_socket
    links.new(uv,tex.inputs["Vector"])
    # Byte 128 is flat. Stretch the small physical range across all 8 bits.
    scale=cfg["max_slope"]*255/254
    decode=nodes.new("ShaderNodeVectorMath")
    decode.operation="MULTIPLY_ADD"
    decode.inputs[1].default_value=(scale,scale,0)
    center=.5-128/255*scale
    decode.inputs[2].default_value=(center,center,1)
    links.new(tex.outputs["Color"],decode.inputs[0])
    links.new(decode.outputs[0],tilt.inputs["Color"])
    scene["pawn_slope_path"]=cfg["texture"]
    scene["pawn_slope_sha256"]=cfg["texture_sha256"]
    scene["pawn_slope_limit"]=cfg["max_slope"]


def run(cfg):
    scene,body=open_source(cfg)
    apply(scene,body,cfg)
    save_trial(scene,cfg)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("measure","apply"))
    p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    cfg=json.loads(a.config.read_text())
    (measure if a.action=="measure" else run)(cfg)

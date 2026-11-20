"""Measure or attach bounded tangent slopes on top of the pawn's existing grain."""
import argparse
import json
import math
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
    if cfg.get("crop"):
        x0,y0,x1,y1=cfg["crop"]
        scene.render.use_border=True;scene.render.use_crop_to_border=False
        scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
        scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
    step=cfg["step"]
    poses=[("flat",0.,0.)]
    if cfg.get("rings"):
        for ring,radius in enumerate(cfg["rings"]):
            for i in range(cfg["directions"]):
                theta=2*math.pi*i/cfg["directions"]
                poses.append((f"ring-{ring}-{i}",radius*math.cos(theta),radius*math.sin(theta)))
    else:
        poses.extend((("u-plus",step,0),("u-minus",-step,0),("v-plus",0,step),("v-minus",0,-step)))
    results={}
    for name,dx,dy in poses:
        tilt.inputs["Color"].default_value=(.5+.5*dx,.5+.5*dy,1,1)
        path=out/(name+".png")
        render(scene,path)
        results[name]=sha(path)
    save_json(out/"measurement.json",{"config":cfg,"pass_sha256":results,"poses":{name:[dx,dy] for name,dx,dy in poses},"method":"Actual Cycles renders with slopes in the wood UV tangent frame. Hold all lights, pigment, roughness, existing grain, geometry and camera."})


def apply(scene,body,cfg):
    path=ROOT/cfg["texture"]
    assert sha(path)==cfg["texture_sha256"]
    material=body.data.materials[0]
    nodes,links=material.node_tree.nodes,material.node_tree.links
    image=bpy.data.images.load(str(path),check_existing=False)
    image.colorspace_settings.name="Non-Color"
    image.pack()
    tex=nodes.get("Pawn fine slope atlas")
    if tex:
        decode=tex.outputs["Color"].links[0].to_node
        assert decode.type=="VECT_MATH" and decode.operation=="MULTIPLY_ADD"
        old=tex.image;tex.image=image
        if old.users==0:
            bpy.data.images.remove(old)
    else:
        _,tilt=slope_nodes(body)
        tex=nodes.new("ShaderNodeTexImage")
        tex.name="Pawn fine slope atlas"
        tex.image=image
        uv=nodes["Pawn walnut pigment"].inputs["Vector"].links[0].from_socket
        links.new(uv,tex.inputs["Vector"])
        decode=nodes.new("ShaderNodeVectorMath")
        decode.operation="MULTIPLY_ADD"
        links.new(tex.outputs["Color"],decode.inputs[0])
        links.new(decode.outputs[0],tilt.inputs["Color"])
    # Byte 128 is flat. Stretch the small physical range across all 8 bits.
    scale=cfg["max_slope"]*255/254
    decode.inputs[1].default_value=(scale,scale,0)
    center=.5-128/255*scale
    decode.inputs[2].default_value=(center,center,1)
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

"""Attach a measured roughness atlas to the live Principled wood and coat."""
import argparse
import json
import sys
from pathlib import Path
import bpy
sys.path.insert(0, str(Path(__file__).parent))
from mission_render import ROOT, sha
from polish_trial import open_source, save_trial


def replace_polish(scene,body,cfg):
    material=body.data.materials[0]
    nodes,links=material.node_tree.nodes,material.node_tree.links
    shader=nodes["Principled BSDF"]
    node=nodes["Pawn varnish roughness"]
    path=ROOT/cfg["texture"]
    assert sha(path)==cfg["texture_sha256"]
    texture=bpy.data.images.load(str(path),check_existing=False)
    texture.colorspace_settings.name="Non-Color";texture.pack()
    old=node.image;node.image=texture
    if old.users==0:
        bpy.data.images.remove(old)
    separate=nodes.get("Pawn finish channels")
    if not separate:
        separate=nodes.new("ShaderNodeSeparateColor");separate.name="Pawn finish channels"
        links.new(node.outputs["Color"],separate.inputs["Color"])
    old_min=scene["pawn_roughness_range"][0]
    for name in ("Roughness","Coat Roughness"):
        remap=shader.inputs[name].links[0].from_node
        assert remap.type=="MAP_RANGE"
        base=remap.inputs["To Min"].default_value/old_min
        remap.inputs["To Min"].default_value=base*cfg["range"][0]
        remap.inputs["To Max"].default_value=base*cfg["range"][1]
        links.new(separate.outputs["Red"],remap.inputs["Value"])
    coverage=nodes.get("Pawn polish strength")
    if not coverage:
        coverage=nodes.new("ShaderNodeMapRange");coverage.name="Pawn polish strength"
        for name in ("Specular IOR Level","Coat Weight"):
            socket=shader.inputs[name]
            mult=nodes.new("ShaderNodeMath");mult.operation="MULTIPLY"
            mult.label="Oil coverage on "+name
            if socket.is_linked:
                links.new(socket.links[0].from_socket,mult.inputs[0])
            else:
                mult.inputs[0].default_value=socket.default_value
            links.new(coverage.outputs["Result"],mult.inputs[1])
            links.new(mult.outputs[0],socket)
    coverage.inputs["To Min"].default_value=cfg["polish_range"][0]
    coverage.inputs["To Max"].default_value=cfg["polish_range"][1]
    links.new(separate.outputs["Green"],coverage.inputs["Value"])
    scene["pawn_roughness_path"]=cfg["texture"]
    scene["pawn_roughness_sha256"]=cfg["texture_sha256"]
    scene["pawn_roughness_range"]=cfg["range"]
    scene["pawn_polish_range"]=cfg["polish_range"]


def apply(scene, body, cfg):
    if "polish_range" in cfg:
        replace_polish(scene,body,cfg)
        return
    material = body.data.materials[0]
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    shader = nodes["Principled BSDF"]
    pigment = nodes["Pawn walnut pigment"]
    path = ROOT / cfg["texture"]
    assert sha(path) == cfg["texture_sha256"]
    texture = bpy.data.images.load(str(path), check_existing=False)
    texture.colorspace_settings.name = "Non-Color"
    texture.pack()
    texture.filepath = "//../../" + cfg["texture"]
    node = nodes.new("ShaderNodeTexImage")
    node.name = "Pawn varnish roughness"
    node.image = texture
    links.new(pigment.inputs["Vector"].links[0].from_socket, node.inputs["Vector"])
    base_values = {}
    for name in ("Roughness", "Coat Roughness"):
        socket = shader.inputs[name]
        assert not socket.is_linked
        base = socket.default_value
        base_values[name] = base
        remap = nodes.new("ShaderNodeMapRange")
        remap.label = name + " over the walnut grain"
        remap.inputs["To Min"].default_value = base * cfg["range"][0]
        remap.inputs["To Max"].default_value = base * cfg["range"][1]
        links.new(node.outputs["Color"], remap.inputs["Value"])
        links.new(remap.outputs["Result"], socket)
    scene["pawn_roughness_path"] = cfg["texture"]
    scene["pawn_roughness_sha256"] = cfg["texture_sha256"]
    scene["pawn_roughness_range"] = cfg["range"]
    scene["pawn_roughness_base"] = base_values["Roughness"]


def run(cfg):
    scene, body = open_source(cfg)
    apply(scene, body, cfg)
    save_trial(scene, cfg)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(args.config.read_text()))

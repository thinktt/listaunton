"""Use actual local pigment variations as shallow wood relief under the varnish."""
from mission_scene import visible_meshes


def add_grain_relief(scene, height):
    material=visible_meshes(scene)[0].data.materials[0]
    nodes,links=material.node_tree.nodes,material.node_tree.links
    bs=nodes["Principled BSDF"]
    pigment=bs.inputs["Base Color"].links[0].from_socket
    previous=bs.inputs["Normal"].links[0].from_socket
    luminance=nodes.new("ShaderNodeRGBToBW")
    luminance.label="Local pigment luminance"
    links.new(pigment,luminance.inputs["Color"])
    floor=nodes.new("ShaderNodeMath");floor.operation="ADD"
    floor.inputs[1].default_value=.018
    links.new(luminance.outputs[0],floor.inputs[0])
    value=nodes.new("ShaderNodeMath");value.operation="LOGARITHM"
    value.inputs[1].default_value=2.7182818
    links.new(floor.outputs[0],value.inputs[0])
    bump=nodes.new("ShaderNodeBump")
    bump.name="Open walnut grain under the varnish"
    bump.inputs["Strength"].default_value=1
    bump.inputs["Distance"].default_value=height
    links.new(previous,bump.inputs["Normal"])
    links.new(value.outputs[0],bump.inputs["Height"])
    for name in ("Normal","Coat Normal"):links.new(bump.outputs[0],bs.inputs[name])
    return bump

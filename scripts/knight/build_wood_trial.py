"""Build a fully three-dimensional walnut finish and an initial studio rig."""
import json
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from mission_scene import (ASSETS, BUILD, configure_render, render, save_model,
                           sha, visible_meshes, world_vertices, use_side_camera, json_file)


def walnut():
    mat = bpy.data.materials.new("Knight | polished walnut")
    mat.use_nodes = True
    n, links = mat.node_tree.nodes, mat.node_tree.links
    bs = n.get("Principled BSDF")
    bs.inputs["IOR"].default_value = 1.47
    bs.inputs["Specular IOR Level"].default_value = .34
    bs.inputs["Coat Weight"].default_value = .26
    bs.inputs["Coat Roughness"].default_value = .095
    coord = n.new("ShaderNodeAttribute")
    coord.attribute_name = "Carved wood coordinates"
    coord.label = "Coordinates fixed to the carving"

    def noise(label, stretch, detail, distortion):
        scale = n.new("ShaderNodeVectorMath")
        scale.operation = "MULTIPLY"
        scale.inputs[1].default_value = stretch
        links.new(coord.outputs["Vector"], scale.inputs[0])
        tex = n.new("ShaderNodeTexNoise")
        tex.label = label
        tex.inputs["Scale"].default_value = 1
        tex.inputs["Detail"].default_value = detail
        tex.inputs["Roughness"].default_value = .65
        tex.inputs["Distortion"].default_value = distortion
        links.new(scale.outputs[0], tex.inputs["Vector"])
        return tex.outputs["Fac"]

    def mix(first, second, factor):
        node = n.new("ShaderNodeMixRGB")
        node.inputs[0].default_value = factor
        links.new(first, node.inputs[1])
        links.new(second, node.inputs[2])
        return node.outputs[0]

    fibers = noise("Fine wavy grain", (4.6, 5.5, 50), 4.0, .55)
    broad = noise("Walnut color variation", (2.5, 3.0, 4.5), 3.0, .65)
    pores = noise("Fine open pores", (155, 92, 172), 2.0, .4)
    wave = n.new("ShaderNodeTexWave")
    wave.label = "Cut growth rings"
    wave.wave_type = "RINGS"
    wave.rings_direction = "Y"
    wave.inputs["Scale"].default_value = 1.8
    wave.inputs["Distortion"].default_value = 5.2
    wave.inputs["Detail"].default_value = 2.5
    wave.inputs["Detail Scale"].default_value = 1.8
    offset = n.new("ShaderNodeVectorMath")
    offset.operation = "ADD"
    offset.inputs[1].default_value = (3.6, .4, -6.4)
    links.new(coord.outputs["Vector"], offset.inputs[0])
    links.new(offset.outputs[0],wave.inputs["Vector"])
    grain = mix(mix(fibers, broad, .20), wave.outputs["Fac"], .13)
    ramp = n.new("ShaderNodeValToRGB")
    ramp.name = "Walnut pigment"
    for element, pos, rgb in [(ramp.color_ramp.elements[0],.24,(.023,.0052,.0016)),
                               (ramp.color_ramp.elements[1],.77,(.205,.067,.017))]:
        element.position = pos
        element.color = (*rgb,1)
    links.new(grain, ramp.inputs[0])
    links.new(ramp.outputs[0], bs.inputs["Base Color"])
    rough = n.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = .22
    rough.inputs["To Max"].default_value = .34
    links.new(fibers, rough.inputs["Value"])
    links.new(rough.outputs[0], bs.inputs["Roughness"])
    bump = n.new("ShaderNodeBump")
    bump.name = "Carving micro relief"
    bump.inputs["Strength"].default_value = .19
    bump.inputs["Distance"].default_value = .004
    links.new(mix(grain, pores, .55), bump.inputs["Height"])
    links.new(bump.outputs[0], bs.inputs["Normal"])
    links.new(bump.outputs[0], bs.inputs["Coat Normal"])
    return mat


def light(scene, name, position, target, power, size, size_y, color):
    data = bpy.data.lights.new(name, "AREA")
    data.shape = "RECTANGLE"
    data.size, data.size_y, data.energy, data.color = size, size_y, power, color
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = position
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z","Y").to_euler()


def main():
    source = BUILD/"001-carving-pose/knight.blend"
    out = BUILD/"002-walnut-studio"
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    mat = walnut()
    for obj in visible_meshes(scene):
        coordinates = obj.data.attributes.new("Carved wood coordinates", "FLOAT_VECTOR", "POINT")
        coordinates.data.foreach_set("vector", np.asarray(world_vertices(obj),dtype=np.float32).ravel())
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    for obj in list(scene.objects):
        if obj.type == "LIGHT": bpy.data.objects.remove(obj, do_unlink=True)
    light(scene, "Knight key | upper left", (-3,-5,10), (0,0,3), 760, 2.2, 4.0, (1,.91,.81))
    light(scene, "Knight fill | cheek", (5,-3,6.8), (.1,0,3.3), 380, 1.3, 3.0, (1,.89,.78))
    light(scene, "Knight edge | poll", (1.1,2.8,10.5), (-.2,0,3.4), 510, 1.0, 3.2, (1,.94,.86))
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1,1,1,1)
    bg.inputs["Strength"].default_value = .075
    configure_render(scene, 64)
    scene["knight_mission_material"] = "Polished walnut, three-dimensional grain and pore relief"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    save_model(scene, out/"knight.blend")
    render(scene, out/"wood.png")
    use_side_camera(scene)
    render(scene, out/"wood-side.png")
    json_file(out/"parameters.json", {"source":source.relative_to(BUILD.parent.parent).as_posix(),
              "source_sha256":sha(source), "saved_model_sha256":sha(out/"knight.blend"),
              "samples":64,"display":"AgX, look None","finish":"3D walnut; fine fibres, rings, pore bump, varnish",
              "camera_and_geometry":"From 001; unchanged"})
    print("KNIGHT_WALNUT_RENDERED", flush=True)


if __name__ == "__main__":
    main()

"""Bake only walnut pigment into one surface atlas for Blender and WebGL."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import (BUILD, configure_render, render, save_model, sha, json_file,
                           visible_meshes, use_side_camera)

LAYER="Knight wood atlas"


def unwrap(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
        uv=obj.data.uv_layers.get(LAYER) or obj.data.uv_layers.new(name=LAYER)
        obj.data.uv_layers.active=uv
        uv.active_render=True
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=np.radians(65),island_margin=.003,
                             area_weight=.2,correct_aspect=True,scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",default="005-softened-pigment")
    parser.add_argument("--variant",default="006-pigment-atlas")
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    source=BUILD/args.source/"knight.blend"
    out=BUILD/args.variant;out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;objects=visible_meshes(scene)
    configure_render(scene,64)
    render(scene,out/"source-reopened.png")
    unwrap(objects)
    mat=objects[0].data.materials[0]
    assert all(o.data.materials[0]==mat for o in objects)
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bs=nodes["Principled BSDF"]
    output=next(n for n in nodes if n.type=="OUTPUT_MATERIAL" and n.is_active_output)
    color=bs.inputs["Base Color"].links[0].from_socket
    emission=nodes.new("ShaderNodeEmission")
    links.new(color,emission.inputs["Color"]);links.new(emission.outputs[0],output.inputs["Surface"])
    atlas=bpy.data.images.new("Knight walnut pigment atlas",width=3072,height=3072,alpha=False)
    atlas.colorspace_settings.name="sRGB"
    target=nodes.new("ShaderNodeTexImage");target.image=atlas;target.name="Knight delivered albedo"
    for node in nodes:node.select=False
    target.select=True;nodes.active=target
    scene.cycles.samples=1
    bpy.ops.object.bake(type="EMIT",use_clear=True,margin=6,uv_layer=LAYER)
    atlas.file_format="PNG";atlas.filepath_raw=str(out/"pigment.png");atlas.save();atlas.pack()
    links.new(bs.outputs[0],output.inputs["Surface"]);nodes.remove(emission)
    uv=nodes.new("ShaderNodeUVMap");uv.uv_map=LAYER
    links.new(uv.outputs["UV"],target.inputs["Vector"]);links.new(target.outputs["Color"],bs.inputs["Base Color"])
    scene["knight_pigment_atlas"]=LAYER
    configure_render(scene,64)
    save_model(scene,out/"knight.blend")
    # Render the saved package, including the packed byte texture and real BSDF.
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False)
    scene=bpy.context.scene;configure_render(scene,64)
    atlas=bpy.data.images["Knight walnut pigment atlas"]
    assert atlas.packed_file and atlas.size[0]==3072 and atlas.colorspace_settings.name=="sRGB"
    render(scene,out/"wood.png")
    use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",{"source":str(source.relative_to(BUILD.parent.parent)).replace(chr(92),"/"),
              "source_sha256":sha(source),"saved_sha256":sha(out/"knight.blend"),"texture_sha256":sha(out/"pigment.png"),
              "size":[3072,3072],"uv_layer":LAYER,"bake_type":"pigment only; temporary emission, restored Principled BSDF",
              "reopened_packed_texture":True,"render_samples":64})
    print("KNIGHT_ATLAS_REOPENED",flush=True)


if __name__=="__main__":
    main()

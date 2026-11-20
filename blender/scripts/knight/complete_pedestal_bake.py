"""Finish and verify the pedestal UV islands in the shared knight pigment atlas."""
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera,visible_meshes
from bake_mission_atlas import LAYER


def check_coverage(scene, image):
    width,height=image.size
    rgb=np.empty((height,width,4),np.float32)
    image.pixels.foreach_get(rgb.ravel())
    graph=bpy.context.evaluated_depsgraph_get()
    report={}
    for obj in visible_meshes(scene):
        ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
        uv=np.empty((len(mesh.loops),2),np.float32); mesh.uv_layers[LAYER].data.foreach_get("uv",uv.ravel())
        indices=np.empty((len(mesh.loop_triangles),3),np.int32);mesh.loop_triangles.foreach_get("loops",indices.ravel())
        pts=uv[indices].mean(1)
        coords=np.clip((pts*[width,height]).astype(int),[0,0],[width-1,height-1])
        values=rgb[coords[:,1],coords[:,0],:3]
        missing=float(np.mean(values.max(1)<.001))
        report[obj.name]={"sampled_triangle_centers":len(pts),"uncolored_fraction":missing}
        ev.to_mesh_clear()
        assert missing<.01,(obj.name,missing)
    return report


def main():
    source=BUILD/"006-pigment-atlas/knight.blend";out=BUILD/"007-complete-atlas";out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;configure_render(scene,64)
    pedestal=bpy.data.objects["Knight | turned pedestal"]
    mat=pedestal.data.materials[0];nodes,links=mat.node_tree.nodes,mat.node_tree.links
    color=nodes["Registered pigment with continuous hidden walnut"].outputs[0]
    target=nodes["Knight delivered albedo"];atlas=target.image
    bs=nodes["Principled BSDF"];output=next(n for n in nodes if n.type=="OUTPUT_MATERIAL" and n.is_active_output)
    emission=nodes.new("ShaderNodeEmission")
    links.new(color,emission.inputs["Color"]);links.new(emission.outputs[0],output.inputs["Surface"])
    for node in nodes:node.select=False
    target.select=True;nodes.active=target
    bpy.ops.object.select_all(action="DESELECT")
    pedestal.select_set(True);bpy.context.view_layer.objects.active=pedestal
    pedestal.data.uv_layers.active=pedestal.data.uv_layers[LAYER]
    scene.cycles.samples=1;scene.render.use_persistent_data=False
    bpy.ops.object.bake(type="EMIT",use_clear=False,margin=6,uv_layer=LAYER)
    atlas.file_format="PNG";atlas.filepath_raw=str(out/"pigment.png");atlas.save();atlas.pack()
    links.new(bs.outputs[0],output.inputs["Surface"]);nodes.remove(emission)
    coverage=check_coverage(scene,atlas)
    configure_render(scene,64);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False)
    scene=bpy.context.scene;configure_render(scene,64)
    render(scene,out/"wood.png")
    use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",{"source_sha256":sha(source),"saved_sha256":sha(out/"knight.blend"),
              "texture_sha256":sha(out/"pigment.png"),"coverage":coverage,"samples":64,
              "method":"Isolated pedestal pigment bake into the pre-existing non-overlapping atlas. All seven parts checked before rendering the reopened real BSDF."})
    print("KNIGHT_ALL_ATLAS_COMPONENTS_RENDERED",flush=True)


if __name__=="__main__":
    main()

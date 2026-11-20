"""Attach inferred, bounded diffuse pigment to visible areas of a true 3D BSDF."""
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import (BUILD, configure_render, json_file, render, save_model, sha,
                           use_side_camera, visible_meshes, world_vertices)


def surface_tree(objects):
    graph=bpy.context.evaluated_depsgraph_get()
    verts=[];faces=[];offset=0
    for obj in objects:
        ev=obj.evaluated_get(graph)
        mesh=ev.to_mesh();mesh.calc_loop_triangles()
        co=np.empty((len(mesh.vertices),3),np.float32)
        mesh.vertices.foreach_get("co",co.ravel())
        transform=np.asarray(obj.matrix_world)
        verts.append(co@transform[:3,:3].T+transform[:3,3])
        tri=np.empty((len(mesh.loop_triangles),3),np.int32)
        mesh.loop_triangles.foreach_get("vertices",tri.ravel())
        faces.append(tri+offset);offset+=len(co)
        ev.to_mesh_clear()
    return BVHTree.FromPolygons(np.concatenate(verts).tolist(),np.concatenate(faces).tolist(),all_triangles=True)


def projection(scene, objects):
    tree=surface_tree(objects)
    graph=bpy.context.evaluated_depsgraph_get()
    camera=scene.camera
    view=camera.matrix_world.to_quaternion()@Vector((0,0,1))
    matrix=np.asarray(camera.calc_matrix_camera(graph,x=1254,y=1254)@camera.matrix_world.inverted())
    stats={}
    for obj in objects:
        co=world_vertices(obj)
        uv_points=.5*(co@matrix[:2,:3].T+matrix[:2,3]+1)
        indices=np.empty(len(obj.data.loops),np.int32)
        obj.data.loops.foreach_get("vertex_index",indices)
        uv=obj.data.uv_layers.get("Knight pigment projection") or obj.data.uv_layers.new(name="Knight pigment projection")
        uv.data.foreach_set("uv",uv_points[indices].astype(np.float32).ravel())
        normals=np.empty(co.shape,np.float32)
        obj.data.vertices.foreach_get("normal",normals.ravel())
        normals=normals@np.linalg.inv(np.asarray(obj.matrix_world)[:3,:3])
        facing=np.clip((normals@np.array(view)-.025)/.30,0,1)
        weight=np.zeros(len(co),np.float32)
        for i in np.flatnonzero(facing>0):
            point=Vector(co[i])
            hit=tree.ray_cast(point+view*15,-view,30)
            if hit[0] is not None:
                error=abs(hit[3]-15)
                weight[i]=facing[i]*np.clip((.07-error)/.04,0,1)
        attr=obj.data.attributes.get("Knight visible pigment") or obj.data.attributes.new("Knight visible pigment","FLOAT","POINT")
        attr.data.foreach_set("value",weight)
        stats[obj.name]=float(weight.mean())
    return stats


def packed_map(name, rgb, out, color_space):
    h,w=rgb.shape[:2]
    image=bpy.data.images.new(name,width=w,height=h,alpha=False,float_buffer=True)
    image.colorspace_settings.name=color_space
    pixels=np.dstack((rgb,np.ones((h,w),np.float32))).astype(np.float32)
    image.pixels.foreach_set(pixels[::-1].copy().ravel())
    image.file_format="OPEN_EXR";image.filepath_raw=str(out/(name+".exr"))
    image.save();image.pack()
    return image


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", default="004-measured-pigment")
    parser.add_argument("--estimate", default="material-observations")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    data=BUILD/"material-observations"
    source=BUILD/"003-continuous-grain/knight.blend"
    estimate=BUILD/args.estimate
    out=BUILD/args.variant;out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;objects=visible_meshes(scene)
    stats=projection(scene,objects)
    mat=objects[0].data.materials[0]
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bs=nodes["Principled BSDF"];old=bs.inputs["Base Color"].links[0].from_socket
    uv=nodes.new("ShaderNodeUVMap");uv.uv_map="Knight pigment projection"
    pigment=nodes.new("ShaderNodeTexImage")
    pigment.image=packed_map("Knight inferred walnut",np.load(estimate/"estimated-pigment.npy"),out,"Linear Rec.709")
    confidence=nodes.new("ShaderNodeTexImage")
    field=np.load(estimate/"transfer-confidence.npy")
    confidence.image=packed_map("Knight inference coverage",np.repeat(field[:,:,None],3,2),out,"Non-Color")
    for tex in (pigment,confidence):
        tex.extension="EXTEND";links.new(uv.outputs["UV"],tex.inputs["Vector"])
    coverage=nodes.new("ShaderNodeAttribute");coverage.attribute_name="Knight visible pigment"
    weight=nodes.new("ShaderNodeMath");weight.operation="MULTIPLY"
    links.new(coverage.outputs["Fac"],weight.inputs[0]);links.new(confidence.outputs["Color"],weight.inputs[1])
    mix=nodes.new("ShaderNodeMixRGB");mix.name="Registered pigment with continuous hidden walnut"
    links.new(weight.outputs[0],mix.inputs[0]);links.new(old,mix.inputs[1]);links.new(pigment.outputs["Color"],mix.inputs[2])
    links.new(mix.outputs[0],bs.inputs["Base Color"])
    configure_render(scene,64)
    scene["knight_material_note"]="Inferred diffuse walnut, masked by real surface visibility; preserved live Principled varnish, bump and scene lights."
    save_model(scene,out/"knight.blend")
    render(scene,out/"wood.png")
    use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",{"source_sha256":sha(source),"coverage_by_component":stats,
              "inference":str((estimate/"inference.json").relative_to(BUILD.parent.parent)).replace(chr(92),"/"),
              "fixed_camera_and_geometry":True,"samples":64})
    print("KNIGHT_PIGMENT_PROJECTED",flush=True)


if __name__=="__main__":
    main()

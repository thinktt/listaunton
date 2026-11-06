"""Measure diffuse response and map evaluated 3D surfaces to their pigment UVs."""
import argparse
from pathlib import Path
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from mission_scene import BUILD,configure_render,json_file,sha,visible_meshes

TEST_GAIN=.42


def atlas_surfaces(scene,out):
    graph=bpy.context.evaluated_depsgraph_get()
    camera=np.asarray(scene.camera.matrix_world.inverted())
    projection=np.asarray(scene.camera.calc_matrix_camera(graph,x=1254,y=1254))
    records=[]
    view=np.array(scene.camera.matrix_world)[:3,2]
    for i,obj in enumerate(visible_meshes(scene)):
        ev=obj.evaluated_get(graph);mesh=ev.to_mesh();mesh.calc_loop_triangles()
        co=np.empty((len(mesh.vertices),3),np.float32)
        corners=np.empty((len(mesh.loops),3),np.float32)
        loop_vertex=np.empty(len(mesh.loops),np.int32)
        tris=np.empty((len(mesh.loop_triangles),3),np.int32)
        uv=np.empty((len(mesh.loops),2),np.float32)
        mesh.vertices.foreach_get("co",co.ravel())
        mesh.corner_normals.foreach_get("vector",corners.ravel())
        mesh.loops.foreach_get("vertex_index",loop_vertex)
        mesh.loop_triangles.foreach_get("loops",tris.ravel())
        mesh.uv_layers["Knight wood atlas"].data.foreach_get("uv",uv.ravel())
        world=np.asarray(obj.matrix_world)
        co=co@world[:3,:3].T+world[:3,3]
        camera_co=co@camera[:3,:3].T+camera[:3,3]
        ndc=camera_co@projection[:3,:3].T+projection[:3,3]
        # Pixel centers use integer coordinates in the sampling code.
        screen=np.column_stack(((1+ndc[:,0])*627-.5,(1-ndc[:,1])*627-.5,-camera_co[:,2]))
        face=corners@np.linalg.inv(world[:3,:3])
        face=face@view/np.maximum(np.linalg.norm(face,axis=1),1e-8)
        name=f"surface-{i}.npz"
        np.savez_compressed(out/name,uv=uv,screen=screen[loop_vertex].astype(np.float32),
                            facing=face.astype(np.float32),triangles=tris)
        records.append({"file":name,"object":obj.name,"triangles":len(tris)})
        ev.to_mesh_clear()
    return records


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True);opt=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=opt.out.resolve();out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(opt.source),load_ui=False);scene=bpy.context.scene
    material=visible_meshes(scene)[0].data.materials[0];tree=material.node_tree
    bs=tree.nodes["Principled BSDF"];color=bs.inputs["Base Color"].links[0].from_socket
    assert color.node.type=="TEX_IMAGE" and color.node.image.packed_file
    import hashlib
    texture_sha=hashlib.sha256(color.node.image.packed_file.data).hexdigest()
    configure_render(scene,128)
    full=read_pass(scene,out/"studio.exr")
    change=tree.nodes.new("ShaderNodeVectorMath");change.operation="SCALE";change.inputs["Scale"].default_value=TEST_GAIN
    tree.links.new(color,change.inputs[0])
    layers=[n for n in tree.nodes if n.type=="BSDF_PRINCIPLED" and n.inputs["Base Color"].is_linked and n.inputs["Base Color"].links[0].from_socket==color]
    assert len(layers)==2
    for node in layers:tree.links.new(change.outputs["Vector"],node.inputs["Base Color"])
    dim=read_pass(scene,out/"dim.exr")
    output=next(n for n in tree.nodes if n.type=="OUTPUT_MATERIAL" and n.is_active_output)
    emissive=tree.nodes.new("ShaderNodeEmission");camera=tree.nodes.new("ShaderNodeCameraData")
    tree.links.new(camera.outputs["View Z Depth"],emissive.inputs["Color"])
    tree.links.new(emissive.outputs[0],output.inputs["Surface"])
    scene.cycles.samples=4;scene.cycles.use_denoising=False
    depth=read_pass(scene,out/"depth.exr")[:,:,0]
    np.savez_compressed(out/"light-response.npz",full=full,dim=dim,depth=depth)
    objects=atlas_surfaces(scene,out)
    json_file(out/"measurement.json",{"source_sha256":sha(opt.source),"texture_sha256":texture_sha,
              "samples":128,"dim_gain":TEST_GAIN,"objects":objects,"camera":"fixed 54 degrees, same registration",
              "method":"Measured full and reduced actual Principled base color with unchanged material normals, finish, lights and camera. Measured camera Z for visible-surface rejection."})
    print("KNIGHT_SURFACE_RESPONSE",texture_sha,flush=True)


if __name__=="__main__":main()

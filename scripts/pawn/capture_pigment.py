"""Measure the real pawn BSDF and lathe coordinates. Pass the source trial directory."""
import argparse
import sys
from pathlib import Path

import bpy
import numpy as np
import PyOpenColorIO as ocio

sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ASSETS, BUILD, control, fixed_camera, save_json, setup, sha

UV_NAME = "Pawn pigment"

def reference_srgb():
    image=bpy.data.images.load(str(ASSETS/"reference.png"),check_existing=False)
    try:
        image.colorspace_settings.name="Non-Color"
        decoded=np.empty(image.size[0]*image.size[1]*4,dtype=np.float32)
        image.pixels.foreach_get(decoded)
        return decoded.reshape(image.size[1],image.size[0],4)[::-1,:,:3].copy()
    finally:bpy.data.images.remove(image)

def add_lathe_uv(obj):
    mesh = obj.data
    if mesh.uv_layers.get(UV_NAME):
        return
    co = np.array([v.co[:] for v in mesh.vertices]).reshape(-1,96,3)
    rz = np.column_stack((np.linalg.norm(co[:,:,:2],axis=2).mean(1),co[:,:,2].mean(1)))
    meridian = np.r_[0,np.cumsum(np.linalg.norm(np.diff(rz,axis=0),axis=1))]
    meridian /= meridian[-1]
    layer = mesh.uv_layers.new(name=UV_NAME)
    for face in mesh.polygons:
        ids=[mesh.loops[i].vertex_index for i in face.loop_indices]
        us=[(index % 96 / 96 - .25) % 1 for index in ids]
        seam=max(us)-min(us)>.5
        for loop,index,u in zip(face.loop_indices,ids,us):
            layer.data[loop].uv=(u+(1 if seam and u<.5 else 0), meridian[index//96])
    mesh.uv_layers.active=layer
    layer.active_render=True

def meridian_samples(obj):
    bpy.context.view_layer.update()
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=ev.to_mesh()
    try:
        layer=mesh.uv_layers[UV_NAME];samples={}
        for loop in mesh.loops:
            vertex=mesh.vertices[loop.vertex_index]
            x,y,z=vertex.co
            if x<=0 or abs(y)>1e-6:continue
            u,v=layer.data[loop.index].uv
            if abs(u-.75)>.0001:continue
            samples[round(v,8)]=(v,x,z,vertex.normal.x,vertex.normal.z)
        result=np.array(sorted(samples.values()),dtype=np.float32)
        # The flat underside fans into the lathe; its central UVs have no
        # unique longitude. Complete that hidden disk and the tiny top pole.
        assert len(result)>130 and result[0,0]<.18 and result[0,4]<-.99
        assert result[-1,0]>.994 and result[-1,4]>.99
        height=[v.co.z for v in mesh.vertices]
        return np.vstack(([0,0,min(height),0,-1],result,[1,0,max(height),0,1]))
    finally:ev.to_mesh_clear()

def capture(source,directory):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;body=control(scene)
    fixed_camera(scene);setup(scene,96);add_lathe_uv(body)
    directory.mkdir(parents=True,exist_ok=True)
    np.save(directory/"meridian.npy",meridian_samples(body))
    scene.render.image_settings.file_format="OPEN_EXR"
    scene.render.image_settings.color_depth="32"
    scene.render.filepath=str(directory/"pass.exr")
    def read_pass(name):
        bpy.ops.render.render(write_still=True)
        im=bpy.data.images.load(scene.render.filepath,check_existing=False)
        arr=np.empty(im.size[0]*im.size[1]*4,dtype=np.float32)
        im.pixels.foreach_get(arr)
        np.save(directory/(name+".npy"),arr.reshape(im.size[1],im.size[0],4)[::-1])
        bpy.data.images.remove(im)
    mat=body.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links
    bsdf=nodes.get("Principled BSDF")
    for link in list(bsdf.inputs["Base Color"].links):links.remove(link)
    bsdf.inputs["Base Color"].default_value=(0,0,0,1)
    read_pass("black")
    bsdf.inputs["Base Color"].default_value=(.1,.1,.1,1)
    read_pass("gray")
    output=next(node for node in nodes if node.type=="OUTPUT_MATERIAL")
    emitter=nodes.new("ShaderNodeEmission");cam=nodes.new("ShaderNodeCameraData")
    links.new(cam.outputs["View Z Depth"],emitter.inputs["Color"])
    links.new(emitter.outputs[0],output.inputs["Surface"])
    scene.cycles.samples=12;scene.cycles.use_denoising=False
    read_pass("depth")
    # Read display-encoded bytes once. OCIO inverts this scene's view transform.
    pixels=reference_srgb()
    np.save(directory/"reference-srgb.npy",pixels)
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    view=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display=scene.display_settings.display_device,view=scene.view_settings.view_transform)
    view.setDirection(ocio.TRANSFORM_DIR_INVERSE)
    config.getProcessor(view).getDefaultCPUProcessor().applyRGB(pixels)
    np.save(directory/"target-linear.npy",pixels)
    save_json(directory/"measurement.json",{"source_sha256":sha(source),"reference_sha256":sha(ASSETS/"reference.png"),"camera_above_board_degrees":54,"gray_linear_value":.1,"samples":96,"depth_samples":12,"method":"Scene-linear black and neutral 0.1 BSDF passes preserve actual reflections, geometry and lights. The separate depth pass measures visibility for UV projection. Diagnostics never enter the public beauty images."})

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source");p.add_argument("output")
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    capture(BUILD/args.source/"pawn.blend",BUILD/args.output)

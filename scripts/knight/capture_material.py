"""Measure reflected light and diffuse response for the knight's actual BSDF."""
from pathlib import Path
import sys

import bpy
import numpy as np
import PyOpenColorIO as ocio

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import BUILD, configure_render, json_file, render, save_model, sha, visible_meshes
from build_wood_trial import light

def read_pass(scene, path):
    scene.render.image_settings.file_format = "OPEN_EXR"
    scene.render.image_settings.color_depth = "32"
    render(scene, path)
    im = bpy.data.images.load(str(path), check_existing=False)
    w,h = im.size
    pixels = np.empty(w*h*4,dtype=np.float32)
    im.pixels.foreach_get(pixels)
    bpy.data.images.remove(im)
    return pixels.reshape(h,w,4)[::-1].copy()


def main():
    source = BUILD/"002-walnut-studio/knight.blend"
    out = BUILD/"material-observations"
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    configure_render(scene, 80)
    mat = visible_meshes(scene)[0].data.materials[0]
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bs = nodes["Principled BSDF"]
    # Blend actual small-scale wood variation into the continuous 3D carving.
    prior = bs.inputs["Base Color"].links[0].from_socket
    tile = nodes.new("ShaderNodeTexImage")
    tile.name = "Local walnut grain"
    tile.image = bpy.data.images.load(str(out/"continuous-grain.png"),check_existing=False)
    tile.image.pack()
    tile.projection = "BOX"
    tile.projection_blend = .25
    coords = next(n for n in nodes if n.type=="ATTRIBUTE" and n.attribute_name=="Carved wood coordinates")
    scale = nodes.new("ShaderNodeVectorMath"); scale.operation="MULTIPLY"
    scale.inputs[1].default_value = (.37,.57,1.28)
    links.new(coords.outputs["Vector"],scale.inputs[0])
    links.new(scale.outputs[0],tile.inputs["Vector"])
    mix = nodes.new("ShaderNodeMixRGB"); mix.name="Continuous walnut"
    mix.inputs[0].default_value=.86
    links.new(prior,mix.inputs[1]);links.new(tile.outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],bs.inputs["Base Color"])
    for obj in list(scene.objects):
        if obj.type=="LIGHT": bpy.data.objects.remove(obj,do_unlink=True)
    light(scene,"Walnut key", (3.3,-4.7,9.5),(.1,0,3.1),880,1.45,2.7,(1,.88,.73))
    light(scene,"Walnut soft fill",(-3.8,-1,7.5),(-.2,0,3.2),250,3.0,4.1,(1,.91,.81))
    light(scene,"Walnut upper strip",(-1,2,9.8),(-.2,0,3.8),480,.72,2.65,(1,.94,.85))
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.055
    trial=BUILD/"003-continuous-grain";trial.mkdir(exist_ok=True)
    save_model(scene,trial/"knight.blend")
    render(scene,trial/"wood.png")
    json_file(trial/"parameters.json",{"source_sha256":sha(source),"tile":sha(out/"continuous-grain.png"),
              "direction":"Right-side key, softer left fill and upper strip; subdued continuous volumetric grain."})
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    view=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR, display=scene.display_settings.display_device,view=scene.view_settings.view_transform)
    assert scene.view_settings.look=="None" and scene.view_settings.gamma==1 and scene.view_settings.exposure==0
    view.setDirection(ocio.TRANSFORM_DIR_INVERSE)
    target=np.load(out/"reference-display.npy")[:,:,:3].copy()
    config.getProcessor(view).getDefaultCPUProcessor().applyRGB(target)
    np.save(out/"reference-linear.npy",target)
    links.remove(bs.inputs["Base Color"].links[0])
    for name,value in [("black",0.),("gray",.16)]:
        bs.inputs["Base Color"].default_value=(value,value,value,1)
        np.save(out/(name+".npy"),read_pass(scene,out/(name+".exr")))
    # Pure pigment is a diagnostic only.
    emission=nodes.new("ShaderNodeEmission")
    links.new(mix.outputs[0],emission.inputs["Color"])
    output=next(n for n in nodes if n.type=="OUTPUT_MATERIAL")
    links.new(emission.outputs[0],output.inputs["Surface"])
    scene.cycles.samples=8;scene.cycles.use_denoising=False
    np.save(out/"prior.npy",read_pass(scene,out/"prior.exr"))
    json_file(out/"response.json",{"source":"build/knight-mission/003-continuous-grain/knight.blend",
              "source_sha256":sha(trial/"knight.blend"),"gray_response_value":.16,"samples":80,
              "camera":"Fixed","view":"AgX","diagnostics_only":True})
    print("KNIGHT_RESPONSES_CAPTURED",flush=True)


if __name__=="__main__":
    main()

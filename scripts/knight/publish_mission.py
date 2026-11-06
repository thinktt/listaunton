"""Prepare the saved model, all render views and exact mesh for one reviewed trial."""
import argparse
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import ASSETS,BUILD,MODEL,ROOT,configure_render,json_file,render,sha,use_side_camera,visible_meshes
from export_mission import export
from complete_pedestal_bake import check_coverage


def angles(scene):
    cam=scene.camera
    scene.render.resolution_x=scene.render.resolution_y=640
    cam.data.shift_x=cam.data.shift_y=0
    cam.data.ortho_scale=6.4
    scene.cycles.samples=24
    target=Vector((0,0,2.65))
    for label,az,el in [("side",0,16),("profile",0,0),("front",90,25),("opposite",180,40),("threequarter",45,20)]:
        az,el=math.radians(az),math.radians(el)
        cam.location=target+Vector((12*math.sin(az)*math.cos(el),-12*math.cos(az)*math.cos(el),12*math.sin(el)))
        cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
        render(scene,ASSETS/("view-"+label+".png"))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("variant")
    parser.add_argument("--previous-hash",required=True)
    parser.add_argument("--atlas-name",required=True)
    parser.add_argument("--checkpoint",required=True)
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    assert Path(args.atlas_name).name==args.atlas_name
    trial=BUILD/args.variant
    metrics=json.loads((trial/"metrics.json").read_text())
    assert sha(MODEL)==args.previous_hash
    assert sha(trial/"knight.blend")==metrics["model_sha256"]
    assert sha(trial/"wood.png")==metrics["render_sha256"]
    for ref in ("original","selected"):
        assert metrics["scores"][ref]["iou"]>=metrics["scores"][ref]["previous_iou"]-.00005
    bpy.ops.wm.open_mainfile(filepath=str(trial/"knight.blend"),load_ui=False)
    scene=bpy.context.scene
    material=visible_meshes(scene)[0].data.materials[0]
    atlas=material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].links[0].from_node.image
    texture=ASSETS/args.atlas_name
    if (trial/"pigment.png").is_file():
        shutil.copyfile(trial/"pigment.png",texture)
    assert texture.is_file() and bytes(atlas.packed_file.data)==texture.read_bytes()
    atlas.filepath="//../../assets/knight/"+args.atlas_name
    scene["knight_mission_checkpoint"]=args.checkpoint
    scene["knight_mission_variant"]=args.variant
    scene["reconstruction"]="Editable Staunton knight. Fixed 54-degree reference camera; original black sprite and selected black candidate 2."
    scene.render.filepath="//../../assets/knight/render.png"
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(MODEL),compress=True,relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(MODEL),load_ui=False)
    scene=bpy.context.scene;objects=visible_meshes(scene)
    saved=objects[0].data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].links[0].from_node.image
    assert saved.packed_file and bytes(saved.packed_file.data)==texture.read_bytes()
    coverage=check_coverage(scene,saved)
    configure_render(scene,scene.cycles.samples)
    export(scene,texture)
    render(scene,ASSETS/"render.png")
    clay=bpy.data.materials.get("Neutral satin clay")
    assert clay is not None
    wood=objects[0].data.materials[0]
    for obj in objects:obj.data.materials[0]=clay
    render(scene,ASSETS/"neutral.png")
    use_side_camera(scene);render(scene,ASSETS/"guide-neutral.png")
    for obj in objects:obj.data.materials[0]=wood
    render(scene,ASSETS/"guide-render.png")
    registration={"guide":"assets/knight/concepts/side-01.png","profile":"assets/knight/guide-render.png",
                  "source_blend_sha256":sha(MODEL),"guide_sha256":sha(ASSETS/"concepts/side-01.png"),
                  "profile_sha256":sha(ASSETS/"guide-render.png"),"profile_size":[1254,1254],
                  "canvas":[1254,1254],"guide_top":0,"scale":1,"offset_x":0,"offset_y":0,
                  "physical_foot_center_x":float(scene.get("knight_foot_center_x",0.0)),
                  "method":"Actual registered 7-degree side-camera render. The camera follows the turned axis horizontally and preserves the shared 565px base width and projected foot at 1127px."}
    json_file(ASSETS/"side-registration.json",registration)
    for obj in objects:obj.data.materials[0]=clay
    angles(scene)
    json_file(ASSETS/"mission-checkpoint.json",{"checkpoint":args.checkpoint,"variant":args.variant,
              "prior_model_sha256":args.previous_hash,"source_sha256":sha(MODEL),"render_sha256":sha(ASSETS/"render.png"),
              "texture_sha256":sha(texture),"texture_file":texture.name,"packed_texture_exact":True,
              "surface_color_coverage":coverage,"camera_degrees":54,"side_degrees":7})
    print("KNIGHT_REVIEW_ASSETS_RENDERED",sha(MODEL),flush=True)


if __name__=="__main__":main()

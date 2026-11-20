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


def check_round(verdict, checkpoint, variant, model, assets, build):
    """Bind a three-way artistic judgment to the scenes and renders actually reviewed."""
    if verdict["checkpoint"] != checkpoint or variant != f"{checkpoint}-{verdict['winner']}":
        raise ValueError("The recorded winner belongs to a different trial")
    if verdict["winner"] not in ("A", "B") or not verdict["reason"].strip():
        raise ValueError("A three-way release needs a winner and a reason")
    def check_files(folder, expected):
        for path, digest in expected.items():
            if sha(folder / path) != digest:
                raise ValueError(f"Reviewed file changed: {folder / path}")
    parent = verdict["parent"]
    if sha(model) != parent["scene"]:
        raise ValueError("The reviewed parent is no longer current")
    check_files(assets, {"render.png": parent["fixed"], "guide-render.png": parent["side"]})
    for code in ("A", "B"):
        trial = build / f"{checkpoint}-{code}"
        row = verdict["candidates"][code]
        check_files(trial, {"parent.blend": parent["scene"], "knight.blend": row["scene"],
                            "wood.png": row["fixed"], "wood-side.png": row["side"],
                            "metrics.json": row["audit"]})
        audit = json.loads((trial / "metrics.json").read_text())
        if (audit["previous_render_sha256"], audit["model_sha256"], audit["render_sha256"]) != (
                parent["fixed"], row["scene"], row["fixed"]):
            raise ValueError(f"Stale registration for {code}")
        check_files(assets, audit["source_sha256"])
    weights = {"reference": .45, "side": .35, "form": .15, "finish": .05}
    totals = {}
    for name in ("Parent", "A", "B"):
        grades = verdict["scores"][name]
        if any(not 0 <= grades[key] <= 100 for key in weights):
            raise ValueError("Grade outside the mission scale")
        totals[name] = sum(grades[key] * weight for key, weight in weights.items())
    if totals[verdict["winner"]] < max(totals.values()):
        raise ValueError("The recorded winner did not win the weighted comparison")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("variant")
    parser.add_argument("--previous-hash",required=True)
    parser.add_argument("--atlas-name",required=True)
    parser.add_argument("--checkpoint",required=True)
    parser.add_argument("--round-verdict",type=Path,
                        help="Signed-off three-way comparison with both candidates' file digests and grades")
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    assert Path(args.atlas_name).name==args.atlas_name
    trial=BUILD/args.variant
    metrics=json.loads((trial/"metrics.json").read_text())
    assert sha(MODEL)==args.previous_hash
    assert sha(trial/"knight.blend")==metrics["model_sha256"]
    assert sha(trial/"wood.png")==metrics["render_sha256"]
    if args.round_verdict:
        check_round(json.loads(args.round_verdict.read_text()), args.checkpoint, args.variant, MODEL, ASSETS, BUILD)
    else:
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
    registration={"neutral":"assets/knight/guide-neutral.png","profile":"assets/knight/guide-render.png",
                  "source_blend_sha256":sha(MODEL),"neutral_sha256":sha(ASSETS/"guide-neutral.png"),
                  "profile_sha256":sha(ASSETS/"guide-render.png"),"profile_size":[1254,1254],
                  "canvas":[1254,1254],"scale":1,"offset_x":0,"offset_y":0,
                  "elevation":json.loads((ASSETS/"guide-camera.json").read_text())["elevation"],
                  "physical_foot_center_x":float(scene.get("knight_foot_center_x",0.0)),
                  "method":"Walnut and neutral clay rendered from the reopened scene using the same registered side camera."}
    json_file(ASSETS/"side-registration.json",registration)
    for obj in objects:obj.data.materials[0]=clay
    angles(scene)
    json_file(ASSETS/"mission-checkpoint.json",{"checkpoint":args.checkpoint,"variant":args.variant,
              "prior_model_sha256":args.previous_hash,"source_sha256":sha(MODEL),"render_sha256":sha(ASSETS/"render.png"),
              "texture_sha256":sha(texture),"texture_file":texture.name,"packed_texture_exact":True,
              "surface_color_coverage":coverage,"camera_degrees":54,"side_degrees":7})
    print("KNIGHT_REVIEW_ASSETS_RENDERED",sha(MODEL),flush=True)


if __name__=="__main__":main()

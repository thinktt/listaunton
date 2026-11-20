"""Compare the saved pawn and both donor meridians in common turning units."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from mission_render import ROOT, control, fixed_camera, save_json, sha
sys.path.insert(0,str(HERE.parent/"king"))
from match_queen_base import SEGMENTS, coordinates
from validate_queen_base import dimensions, profile_error, section


def donor(path, prefix, segments, landmark):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(path),link=False) as (source,loaded):
        names=[n for n in source.objects if n.startswith(prefix)]
        assert len(names)==1,names
        loaded.objects=names
    body,=loaded.objects
    bpy.context.scene.collection.objects.link(body)
    body.hide_viewport=False
    body.hide_set(False)
    assert body.get(landmark)
    return coordinates(body,segments)[:40,::segments//SEGMENTS].astype(np.float64),section(body)


def run(config, output):
    queen_path,king_path=(ROOT/config[key] for key in ("queen","king"))
    assert sha(queen_path)==config["queen_sha256"] and sha(king_path)==config["king_sha256"]
    queen,q_profile=donor(queen_path,"01 Queen - continuous body",192,"mission_editable_control")
    king,k_profile=donor(king_path,"King - continuous turned body",96,"king_editable_control")
    np.testing.assert_allclose(queen,king,atol=2e-6,rtol=0)
    old=ROOT/config["source"]
    assert sha(old)==config["source_sha256"]
    bpy.ops.wm.open_mainfile(filepath=str(old),load_ui=False)
    old_scene=bpy.context.scene
    fixed_camera(old_scene)
    old_body=control(old_scene)
    old_floor=coordinates(old_body,SEGMENTS)[0,0,2]
    old_profile=section(old_body)
    old_width=json.loads((ROOT/config["starting_dimensions"]).read_text())["diameter"]
    old_profile[:,1]-=old_floor
    old_profile/=old_width/config["donor_foot_diameter"]
    model=ROOT/"models/pawn/pawn-rebuilt.blend"
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
    scene=bpy.context.scene
    fixed_camera(scene)
    body=control(scene)
    controls=coordinates(body,SEGMENTS)
    recipe=json.loads(scene["pawn_shared_base"])
    scale=recipe["uniform_scale"]
    floor=recipe["floor"]
    assert abs(floor-old_floor)<1e-7
    base=controls[:40].astype(np.float64)
    base[:,:,2]-=floor
    base/=scale
    base[:,:,2]+=queen[0,0,2]
    np.testing.assert_allclose(base,queen,rtol=0,atol=2e-7)
    np.testing.assert_allclose(base,king,rtol=0,atol=2e-6)
    profile=section(body)
    profile[:,1]-=floor
    profile/=scale
    profile[:,1]+=queen[0,0,2]
    errors={k:profile_error(profile,p) for k,p in (("queen",q_profile),("king",k_profile))}
    old_errors={k:profile_error(old_profile,p) for k,p in (("queen",q_profile),("king",k_profile))}
    assert max(errors.values())<.005 and max(errors.values())<min(old_errors.values())/10,(errors,old_errors)
    side=bpy.data.scenes[scene["pawn_side_scene"]]
    assert control(side) is body
    bpy.context.window.scene=side
    bpy.context.view_layer.update()
    level=float(side.camera.matrix_world.to_3x3().col[2].normalized().z)
    assert abs(level)<1e-6
    report={"model_sha256":sha(model),"donor_sha256":{"king":sha(king_path),"queen":sha(queen_path)},
            "base_rings":39,"adjoining_stem_support":1,"ring_segments":SEGMENTS,
            "uniform_scale":scale,"floor":floor,"height":recipe["actual_height"],"diameter":recipe["actual_diameter"],
            "max_control_coordinate_delta_donor_units":{"queen":float(abs(base-queen).max()),"king":float(abs(base-king).max())},
            "evaluated_base_max_normal_distance_donor_units":errors,"previous_at_equal_diameter":old_errors,
            "compared_z_donor_units":[.006,1.225],"donor_native_foot_diameter":config["donor_foot_diameter"],
            "normalized_dimensions":{name:dimensions(p) for name,p in (("queen",q_profile),("king",k_profile),("pawn",profile))},
            "level_camera_sine":level,"same_control_mesh_at_54_and_0_degrees":True}
    save_json(output,report)
    print("PAWN_SHARED_BASE_CHECK",errors,old_errors,flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("config",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(args.config.read_text()),args.output)

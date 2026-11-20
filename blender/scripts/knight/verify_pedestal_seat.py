"""Verify the physical foot, lower-carving seat, protected head and side floor."""
from pathlib import Path
import argparse
import json
import sys
import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import json_file,sha,visible_meshes,world_vertices
from project_mission_pigment import surface_tree


def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);scene=bpy.context.scene
    objects=visible_meshes(scene);base=bpy.data.objects["Knight | turned pedestal"]
    skin=bpy.data.objects["Knight | continuous horse head and neck"]
    foot=surface_tree([base]);body=surface_tree([skin]);contact=len(foot.overlap(body))
    assert contact>0
    graph=bpy.context.evaluated_depsgraph_get();ev=base.evaluated_get(graph);me=ev.to_mesh()
    pts=np.empty((len(me.vertices),3),np.float32);me.vertices.foreach_get("co",pts.ravel())
    world=np.asarray(base.matrix_world);pts=pts@world[:3,:3].T+world[:3,3];ev.to_mesh_clear()
    return {"objects":{obj.name:world_vertices(obj) for obj in objects if obj!=base},
            "foot_bounds":[pts.min(0),pts.max(0)],"foot_origin":np.asarray(base.matrix_world)[:3,3].copy(),
            "intersections":contact,"camera":np.asarray(scene.camera.matrix_world).copy()}


def main():
    p=argparse.ArgumentParser();p.add_argument("previous",type=Path);p.add_argument("current",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    first=snapshot(a.previous);last=snapshot(a.current)
    assert np.array_equal(first["camera"],last["camera"])
    offset=last["foot_origin"]-first["foot_origin"]
    assert abs(offset[0])<.055 and max(abs(offset[1:]))<1e-7
    for a0,b0 in zip(first["foot_bounds"],last["foot_bounds"]):
        assert np.max(np.abs((b0-offset)-a0))<.000003
    check={}
    for name,old in first["objects"].items():
        new=last["objects"][name];assert new.shape==old.shape
        lower=old[:,2]<=1.76;upper=old[:,2]>=2.48
        lower_error=float(np.abs((new[lower]-offset)-old[lower]).max()) if lower.any() else 0
        upper_error=float(np.abs(new[upper]-old[upper]).max()) if upper.any() else 0
        assert max(lower_error,upper_error)<.000003
        check[name]={"seat_vertices":int(lower.sum()),"protected_upper_vertices":int(upper.sum()),
                     "seat_relative_error":lower_error,"upper_coordinate_error":upper_error}
    cfg={"previous_sha256":sha(a.previous),"source_sha256":sha(a.current),"axis_shift_world":offset.tolist(),
         "base_mesh_intersection_pairs_before":first["intersections"],"base_mesh_intersection_pairs_after":last["intersections"],
         "diameter_change":float((last["foot_bounds"][1]-last["foot_bounds"][0])[0]-(first["foot_bounds"][1]-first["foot_bounds"][0])[0]),
         "physical_bounds_relative_to_foot_preserved":True,"floor_and_camera_preserved":True,"parts":check}
    json_file(a.output,cfg);print("KNIGHT_SEAT_CHECK",cfg["diameter_change"],cfg["base_mesh_intersection_pairs_after"],flush=True)


if __name__=="__main__":main()

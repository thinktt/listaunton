"""Compare evaluated carvings and measure both native joints and the level shelf."""
from pathlib import Path
import argparse
from hashlib import sha256
import json
import sys

import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from combine_carvings import evaluated_digest

BASE = "Knight | turned pedestal"
NECK = "Knight | continuous horse head and neck"
MANE = "Knight | swept rounded mane"


def surface(obj):
    host = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = host.to_mesh()
    try:
        mesh.calc_loop_triangles()
        vertices = np.empty((len(mesh.vertices), 3), np.float32)
        indices = np.empty((len(mesh.loop_triangles), 3), np.int32)
        mesh.vertices.foreach_get("co", vertices.ravel())
        mesh.loop_triangles.foreach_get("vertices", indices.ravel())
        transform = np.asarray(host.matrix_world)
        world = vertices @ transform[:3, :3].T + transform[:3, 3]
        tree = BVHTree.FromPolygons(world.tolist(), indices.tolist(), all_triangles=True)
        return world, indices, tree
    finally:
        host.to_mesh_clear()


def section(points, faces, height, center):
    tri = points[faces]
    next_point = np.roll(tri, -1, axis=1)
    crosses = (tri[:, :, 2] < height) != (next_point[:, :, 2] < height)
    a, b = tri[crosses], next_point[crosses]
    w = (height - a[:, 2]) / (b[:, 2] - a[:, 2])
    lines = (a[:, :2] + w[:, None] * (b[:, :2] - a[:, :2]) - center).reshape(-1, 2, 2)
    radii = np.zeros(360)
    for degrees in range(360):
        angle = np.radians(degrees)
        direction = np.array([np.cos(angle), np.sin(angle)])
        offsets = lines @ np.array([-direction[1], direction[0]])
        intersects = (offsets[:, 0] <= 0) != (offsets[:, 1] <= 0)
        on_ray, distance = lines[intersects], offsets[intersects]
        weight = distance[:, 0] / (distance[:, 0] - distance[:, 1])
        endpoints = on_ray[:, 0] + weight[:, None] * (on_ray[:, 1] - on_ray[:, 0])
        radii[degrees] = (endpoints @ direction).max(initial=0)
    return radii


def distances(margins):
    return {"minimum": float(margins.min()), "mean": float(margins.mean()),
            "positive_samples": int((margins > 0).sum()),
            "front": float(margins[0]), "far": float(margins[90]),
            "back": float(margins[180]), "near": float(margins[270])}


def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    scene = bpy.context.scene
    parts = {obj.name: evaluated_digest(obj) for obj in scene.objects if obj.type == "MESH"}
    assert len(parts) == 9
    base, base_faces, base_tree = surface(scene.objects[BASE])
    center = (base[:, :2].max(axis=0) + base[:, :2].min(axis=0)) / 2
    top = float(base[:, 2].max())
    tolerance = .00001
    rim = section(base, base_faces, top - tolerance, center)
    contacts = {}
    footprints = {}
    for name in (NECK, MANE):
        points, faces, tree = surface(scene.objects[name])
        pairs = base_tree.overlap(tree)
        assert len(pairs) > 0 and points[:, 2].min() < top < points[:, 2].max()
        footprints[name] = section(points, faces, top, center)
        assert footprints[name].max() > 0
        contacts[name] = {"intersecting_triangle_pairs": len(pairs), "lowest_z": float(points[:, 2].min()),
                          "height_below_top": float(top - points[:, 2].min())}
    neck_margin = distances(rim - footprints[NECK])
    combined_margin = distances(rim - np.maximum(footprints[NECK], footprints[MANE]))
    return {"scene_sha256": sha256(path.read_bytes()).hexdigest(), "geometry": parts,
            "native_contacts": contacts, "top_z": top, "turning_center_xy": center.tolist(),
            "level_tolerance": tolerance, "average_level_radius": float(rim.mean()),
            "neck_margin": neck_margin, "combined_footprint_margin": combined_margin,
            "mane_extends_beyond_neck_in_degrees": int((footprints[MANE] > footprints[NECK]).sum())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("scenes", nargs="+", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    runs = {p.parent.name: inspect(p.resolve()) for p in args.scenes}
    values = list(runs.values())
    assert all(v["geometry"] == values[0]["geometry"] for v in values)
    assert all(v["neck_margin"]["positive_samples"] == 360 for v in values)
    assert all(v["combined_footprint_margin"]["positive_samples"] == 360 for v in values)
    report = {"blender": bpy.app.version_string, "all_nine_evaluated_meshes_identical": True,
              "sampled_azimuths": 360, "method": "World-space evaluated native triangles. Measure turning at top minus 0.00001 and footprint through the top. BVH triangle overlap verifies each joint separately.",
              "trials": runs}
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for k, row in runs.items():
        print(k, row["neck_margin"], row["combined_footprint_margin"], row["native_contacts"], flush=True)


if __name__ == "__main__":
    main()

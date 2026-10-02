"""Validate the continuous queen without modifying either Blender source file.

Run inside Blender in background mode only after the final model is saved.
The authorized crown flare/rim change is intentionally not compared for equality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "history" / "queen-hires"
OUTPUT = ROOT / "assets" / "queen"
TOLERANCE = 2e-6
BASELINE_BODY_SEGMENTS = 192
BASELINE_CROWN_SEGMENTS = 256
BASELINE_FINIAL_FIRST_RING = 20
SHARED_ANGLES = 64


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def coordinates(obj):
    values = np.empty(len(obj.data.vertices) * 3, dtype=np.float64)
    obj.data.vertices.foreach_get("co", values)
    values = values.reshape((-1, 3))
    matrix = np.asarray(obj.matrix_world, dtype=np.float64)
    return values @ matrix[:3, :3].T + matrix[:3, 3]


def component_count(mesh):
    """Count all control-vertex components, including isolated vertices."""
    parents = list(range(len(mesh.vertices)))
    sizes = [1] * len(parents)

    def root(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    for edge in mesh.edges:
        first, second = (root(index) for index in edge.vertices)
        if first != second:
            if sizes[first] < sizes[second]:
                first, second = second, first
            parents[second] = first
            sizes[first] += sizes[second]
    return len({root(index) for index in range(len(parents))})


def compare_points(current, baseline):
    require(current.shape == baseline.shape, "Comparison point-array sizes differ")
    require(len(current) > 0, "Comparison contains no points")
    delta = current - baseline
    max_distance = float(np.linalg.norm(delta, axis=1).max())
    max_component = float(np.abs(delta).max())
    return {
        "vertex_count": len(current),
        "coordinate_space": "world",
        "tolerance": TOLERANCE,
        "max_distance": max_distance,
        "max_component_difference": max_component,
        "passed": bool(np.isfinite(delta).all() and max_distance <= TOLERANCE),
    }


def inspect_scene(report):
    scene = bpy.context.scene
    objects = [obj for obj in scene.objects if obj.type == "MESH"]
    report["mesh_object_count"] = len(objects)
    require(len(objects) == 1, "Expected exactly one mesh in the current scene")
    queen = objects[0]
    require(not queen.hide_render, "The queen is hidden from renders")
    require(bool(scene.get("continuous_crown")), "Continuous-crown scene marker is absent")
    report["control_connected_components"] = component_count(queen.data)
    require(report["control_connected_components"] == 1,
            "The control mesh is not one connected surface")
    require(np.isfinite(coordinates(queen)).all(), "Non-finite control coordinates")

    # Evaluate at the saved render subdivision settings, in memory only.
    for modifier in queen.modifiers:
        modifier.show_viewport = modifier.show_render
        if modifier.type == "SUBSURF":
            modifier.levels = modifier.render_levels
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    graph.update()
    evaluated = queen.evaluated_get(graph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=graph)
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bm.transform(evaluated.matrix_world)
        record = {
            "name": queen.name,
            "editable_vertices": len(queen.data.vertices),
            "render_vertices": len(mesh.vertices),
            "render_faces": len(mesh.polygons),
            "non_manifold_edges": sum(not edge.is_manifold for edge in bm.edges),
            "loose_vertices": sum(not vertex.link_edges for vertex in bm.verts),
            "loose_edges": sum(not edge.link_faces for edge in bm.edges),
            "volume": float(bm.calc_volume(signed=True)),
            "subdivision_editable": any(mod.type == "SUBSURF" for mod in queen.modifiers),
        }
        report["meshes"] = [record]
        require(record["render_vertices"] > 0 and record["render_faces"] > 0,
                "The evaluated mesh is empty")
        require(record["non_manifold_edges"] == 0, "Evaluated mesh has non-manifold edges")
        require(record["loose_vertices"] == 0 and record["loose_edges"] == 0,
                "Evaluated mesh contains loose geometry")
        require(math.isfinite(record["volume"]) and record["volume"] > 0,
                "Evaluated mesh must have positive finite signed volume")
        require(record["subdivision_editable"], "Editable subdivision modifier is missing")
    finally:
        bm.free()
        evaluated.to_mesh_clear()

    camera = scene.camera
    require(camera is not None and camera.type == "CAMERA", "No active reference camera")
    backgrounds = [item.image for item in camera.data.background_images if item.image]
    references = [image for image in backgrounds if image.name.startswith("reference")]
    report["reference_packed"] = bool(references) and all(bool(image.packed_file) for image in references)
    report["camera_background"] = bool(camera.data.show_background_images and backgrounds)
    report["resolution"] = [scene.render.resolution_x, scene.render.resolution_y]
    report["resolution_percentage"] = scene.render.resolution_percentage
    report["pixel_aspect"] = [scene.render.pixel_aspect_x, scene.render.pixel_aspect_y]
    report["render_samples"] = scene.cycles.samples
    report["camera"] = {
        "name": camera.name,
        "type": camera.data.type,
        "ortho_scale": float(camera.data.ortho_scale),
        "shift_x": float(camera.data.shift_x),
        "shift_y": float(camera.data.shift_y),
        "matrix_world": [[float(value) for value in row] for row in camera.matrix_world],
    }
    require(report["reference_packed"], "Camera reference image is not packed")
    require(report["camera_background"], "Reference camera background is not enabled")
    require(camera.data.type == "ORTHO", "The matched reference camera is not orthographic")
    require(report["resolution"] == [1254, 1254] and report["resolution_percentage"] == 100,
            "Unexpected reference-render resolution")
    require(report["pixel_aspect"] == [1.0, 1.0], "Unexpected render pixel aspect")
    return queen


def compare_preserved_regions(queen, baseline_path, report):
    keys = ("ring_segments", "body_preserved_ring_count", "finial_first_ring",
            "finial_ring_count", "finial_source_first_ring")
    require(all(key in queen for key in keys), "Preserved-region metadata is incomplete")
    metadata = {key: int(queen[key]) for key in keys}
    report["ring_metadata"] = metadata
    segments = metadata["ring_segments"]
    body_count = metadata["body_preserved_ring_count"]
    finial_start = metadata["finial_first_ring"]
    finial_count = metadata["finial_ring_count"]
    require(segments == BASELINE_BODY_SEGMENTS, "Body angular sampling changed from 192")
    require(body_count > 0 and finial_count > 0 and finial_start > body_count,
            "Invalid ring metadata")
    require(metadata["finial_source_first_ring"] == BASELINE_FINIAL_FIRST_RING,
            "Finial source ring must be 20")
    require((finial_start + finial_count) * segments == len(queen.data.vertices),
            "Finial metadata does not cover the final complete control rings")

    with bpy.data.libraries.load(str(baseline_path), link=False) as (source, destination):
        names = [name for name in source.objects
                 if name.startswith("01 Body") or name.startswith("02 Crown")]
        require(len(names) == 2, "Baseline must contain exactly one 01 Body and one 02 Crown")
        destination.objects = names
    imported = [obj for obj in destination.objects if obj is not None]
    # Linking only in memory lets the dependency graph compute the imported
    # object's world matrix, including the old crown's saved Z translation.
    baseline_collection = bpy.data.collections.new("__validation_baseline__")
    bpy.context.scene.collection.children.link(baseline_collection)
    try:
        for obj in imported:
            baseline_collection.objects.link(obj)
        bpy.context.view_layer.update()
        bodies = [obj for obj in imported if obj.name.startswith("01 Body") and obj.type == "MESH"]
        crowns = [obj for obj in imported if obj.name.startswith("02 Crown") and obj.type == "MESH"]
        require(len(bodies) == len(crowns) == 1, "Could not identify the baseline meshes")
        body, crown = bodies[0], crowns[0]
        current_points = coordinates(queen)
        body_points = coordinates(body)
        crown_points = coordinates(crown)

        preserved_vertices = body_count * segments
        require(preserved_vertices <= len(body_points), "Preserved body range exceeds baseline")
        report["preserved_body_control_vertices"] = compare_points(
            current_points[:preserved_vertices], body_points[:preserved_vertices])
        require(report["preserved_body_control_vertices"]["passed"],
                "Preserved body vertices differ from the baseline")

        require(len(crown_points) % BASELINE_CROWN_SEGMENTS == 0,
                "Baseline crown does not contain complete 256-vertex rings")
        old_ring_count = len(crown_points) // BASELINE_CROWN_SEGMENTS
        require(old_ring_count - BASELINE_FINIAL_FIRST_RING == finial_count,
                "Finial ring count differs from the baseline")
        require(segments % SHARED_ANGLES == 0 and BASELINE_CROWN_SEGMENTS % SHARED_ANGLES == 0,
                "Angular sampling does not provide 64 exact shared angles")
        current_indices = []
        baseline_indices = []
        for ring in range(finial_count):
            for angle in range(SHARED_ANGLES):
                current_indices.append((finial_start + ring) * segments
                                       + angle * (segments // SHARED_ANGLES))
                baseline_indices.append((BASELINE_FINIAL_FIRST_RING + ring) * BASELINE_CROWN_SEGMENTS
                                        + angle * (BASELINE_CROWN_SEGMENTS // SHARED_ANGLES))
        finial = compare_points(current_points[current_indices], crown_points[baseline_indices])
        finial.update({"rings": finial_count, "shared_angles_per_ring": SHARED_ANGLES,
                       "baseline_segments": BASELINE_CROWN_SEGMENTS,
                       "current_segments": segments,
                       "baseline_first_ring": BASELINE_FINIAL_FIRST_RING})
        report["preserved_finial_control_vertices"] = finial
        require(finial["passed"], "Finial differs at the 64 shared world-space angles")
        report["authorized_changed_region"] = "Crown body transition, flare, rim and bowl; no full-crown equality check"
    finally:
        for obj in imported:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(baseline_collection)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blend", type=Path, default=ROOT / "models" / "queen" / "queen-rebuilt.blend")
    parser.add_argument("--baseline", type=Path, default=WORK / "before-seamless-crown" / "queen-rebuilt.blend")
    parser.add_argument("--report", type=Path, default=OUTPUT / "model-validation.json")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    current_path, baseline_path = args.blend.resolve(), args.baseline.resolve()
    report = {"validation": "Continuous queen and preserved control regions", "passed": False,
              "source_blend": str(current_path), "baseline_blend": str(baseline_path),
              "coordinate_tolerance": TOLERANCE}
    fingerprints = {}
    try:
        for label, path in (("source", current_path), ("baseline", baseline_path)):
            require(path.is_file(), f"Missing {label} Blender file: {path}")
            fingerprints[label] = (path, sha256(path), path.stat().st_mtime_ns)
            report[f"{label}_sha256"] = fingerprints[label][1]
        bpy.ops.wm.open_mainfile(filepath=str(current_path), load_ui=False)
        queen = inspect_scene(report)
        compare_preserved_regions(queen, baseline_path, report)
        report["passed"] = True
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}"
    finally:
        for label, (path, before_hash, before_mtime) in fingerprints.items():
            unchanged = path.is_file() and sha256(path) == before_hash and path.stat().st_mtime_ns == before_mtime
            report[f"{label}_file_unchanged"] = unchanged
            if not unchanged:
                report["passed"] = False
                report.setdefault("file_errors", []).append(f"{label} Blender file changed during validation")
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

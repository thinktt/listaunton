"""Reapply the two carvings independently to the pinned model in Blender memory."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
import bpy
import numpy as np


def digest(data):
    return hashlib.sha256(data).hexdigest()


def evaluated_part(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    result = hashlib.sha256()
    try:
        fields = [(mesh.vertices, "co", 3, "f"), (mesh.edges, "vertices", 2, "i"),
                  (mesh.loops, "vertex_index", 1, "i"), (mesh.corner_normals, "vector", 3, "f")]
        fields += [(uv.data, "uv", 2, "f") for uv in mesh.uv_layers]
        for collection, prop, columns, dtype in fields:
            values = np.empty(len(collection) * columns, dtype)
            collection.foreach_get(prop, values)
            result.update(values.tobytes())
    finally:
        evaluated.to_mesh_clear()
    result.update(np.asarray(obj.matrix_world, dtype="f").tobytes())
    return result.hexdigest()


def parts(scene):
    return {obj.name: evaluated_part(obj) for obj in scene.objects if obj.type == "MESH"}


def open_scene(path):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    return bpy.context.scene


def verify_bytes(path, expected):
    raw = path.read_bytes()
    if digest(raw) != expected:
        # Working copies of project scripts and configuration can use Windows line endings.
        if path.suffix not in (".py", ".json") or digest(raw.replace(b"\r\n", b"\n")) != expected:
            raise ValueError(f"Unexpected source bytes in {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Project checkout containing the accepted 16A model")
    parser.add_argument("--parent", type=Path, help="Extracted 16A model for use with a later project checkout")
    parser.add_argument("--frozen-root", type=Path, help="Optional directory containing the two archived worker scenes")
    parser.add_argument("--rederive-seeds", action="store_true", help="Derive and compare parent topology and radial section arrays")
    parser.add_argument("--report", type=Path, help="Write a verification receipt to this file")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    packet = Path(__file__).resolve().parent
    inv = json.loads((packet / "inventory.json").read_bytes())
    root = args.project.resolve()
    for key in ("source_repository_inputs", "geometry_run_project_dependencies"):
        for name, expected in inv[key].items():
            if args.parent and name in ("models/knight/knight-rebuilt.blend", "assets/knight/render.png", "assets/knight/guide-render.png"):
                continue
            verify_bytes(root / name, expected)
    parent = args.parent.resolve() if args.parent else root / "models/knight/knight-rebuilt.blend"
    verify_bytes(parent, inv["source_repository_inputs"]["models/knight/knight-rebuilt.blend"])
    for trial, inputs in inv["direct_recipe_inputs"].items():
        for name, expected in inputs.items():
            verify_bytes(packet / trial / name, expected)
    sys.path[:0] = [str(root / "scripts/knight"), str(packet / "mission008-mane"), str(packet / "mission008-neck")]
    import geometry
    import neck
    import chart
    import survey
    parent_scene = open_scene(parent)
    parent_parts = parts(parent_scene)
    assert len(parent_parts) == 9
    report = {"blender": bpy.app.version_string, "numpy": np.__version__, "parent_file_sha256": digest(parent.read_bytes()),
              "parent_evaluated_parts": parent_parts, "trials": {}}
    if args.rederive_seeds:
        mesh = parent_scene.objects["Knight | swept rounded mane"].data
        ordered = chart.mesh_chart(mesh)
        with np.load(packet / "mission008-mane/ring-chart.npz") as saved:
            assert all(np.array_equal(a, saved[k]) for a, k in zip(ordered, ("grid", "front", "back")))
        with tempfile.TemporaryDirectory() as tmp:
            original_dir = survey.D
            try:
                survey.D = Path(tmp)
                survey.run(parent_scene, "parent")
            finally:
                survey.D = original_dir
            with np.load(Path(tmp) / "sections-parent.npz") as actual, np.load(original_dir / "sections-parent.npz") as saved:
                assert set(actual.files) == set(saved.files)
                assert all(np.array_equal(actual[k], saved[k], equal_nan=True) for k in saved.files)
        report["rederived_seed_arrays_equal"] = ["mane station grid and both caps", "all neck survey arrays"]
    for trial, changed in inv["evaluated_component_hashes"].items():
        scene = open_scene(parent)
        if trial == "mission008-mane":
            geometry.carve(scene, registered=True)
        else:
            neck.apply(scene, 2)
        bpy.context.view_layer.update()
        actual = parts(scene)
        assert actual == {**parent_parts, **changed}, f"{trial} evaluated output differs"
        change_set = sorted(name for name in actual if actual[name] != parent_parts[name])
        assert set(change_set) == set(changed)
        proof = {"all_nine_parts_match_expected": True, "changed_evaluated_parts": changed}
        if args.frozen_root:
            frozen = args.frozen_root.resolve() / trial / "knight.blend"
            expected = inv["frozen_worker_outputs"][trial]["knight.blend"]
            verify_bytes(frozen, expected)
            assert actual == parts(open_scene(frozen)), f"{trial} differs from the frozen worker scene"
            proof["all_nine_parts_match_reopened_frozen_scene"] = True
            proof["frozen_file_sha256"] = expected
        report["trials"][trial] = proof
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

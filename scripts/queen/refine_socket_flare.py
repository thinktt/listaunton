"""Reshape the inner flare and socket on the accepted closed queen, then rebuild its light receivers."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import link, partition

BASELINE_SHA = "cf248e4a1766fbdb1e51b7e823931bc26729531dfda4ffbda12a83ee961ad460"
ARCHIVE = ROOT / "history/queen-mission-017/queen-rebuilt.blend"
CURRENT = ROOT / "models/queen/queen-rebuilt.blend"
FEATURE = "raised_flare_compact_socket"


def read_controls(mesh, segments):
    positions = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get("co", positions)
    return positions.reshape(-1, segments, 3)


def atlas_signature(mesh):
    uv = np.empty(len(mesh.loops) * 2, dtype=np.float32)
    mesh.uv_layers["Pigment atlas"].data.foreach_get("uv", uv)
    return hashlib.sha256(uv.tobytes()).hexdigest()


def verified_source():
    source = ARCHIVE if ARCHIVE.exists() else CURRENT
    if hashlib.sha256(source.read_bytes()).hexdigest() != BASELINE_SHA:
        raise ValueError(f"Expected the accepted seventeenth queen checkpoint at {source}")
    return source


def apply_profile(before, entries):
    after = before.copy()
    indices = [e["ring"] for e in entries]
    if not indices or indices != sorted(set(indices)) or min(indices) < 20 or max(indices) > 40:
        raise ValueError("Profile entries must identify distinct inner-flare and socket rings in ascending order")
    for entry in entries:
        ring = after[entry["ring"]]
        lengths = np.linalg.norm(ring[:, :2], axis=1)
        ring[:, :2] *= (entry["radius"] / lengths)[:, None]
        ring[:, 2] = entry["z"]
    lower_body = after[19:42]
    if not np.all(np.diff(lower_body[:, 0, 2]) > 0):
        raise ValueError("The proposed meridian doubles back vertically")
    radii = np.linalg.norm(lower_body[:, :, :2], axis=2).mean(axis=1)
    if not np.all(np.diff(radii) <= 1e-5):
        raise ValueError("The proposed meridian introduces a second ledge")
    return after


def check_scope(controls, settings, mesh_name):
    """Check edited rings and recover the real prior control for earlier checkpoint checks."""
    feature = settings.get(FEATURE)
    if not feature:
        return None, controls
    source = verified_source()
    assert feature["source_sha256"] == BASELINE_SHA
    with bpy.data.libraries.load(str(source), link=False) as (names, loaded):
        assert mesh_name in names.meshes, mesh_name
        loaded.meshes = [mesh_name]
    prior_mesh = loaded.meshes[0]
    before = read_controls(prior_mesh, controls.shape[1])
    bpy.data.meshes.remove(prior_mesh)
    entries = feature["rings"]
    expected = apply_profile(before, entries)
    assert np.array_equal(controls, expected), "Delivered meridian differs from the recorded profile"
    keep = np.ones(len(controls), dtype=bool)
    keep[[e["ring"] for e in entries]] = False
    assert np.array_equal(controls[keep], before[keep])
    assert hashlib.sha256(before.tobytes()).hexdigest() == feature["baseline_control_sha256"]
    radius = lambda arr, i: float(np.linalg.norm(arr[i, :, :2], axis=1).mean())
    wall = lambda arr: float(arr[31, 0, 2] - arr[29, 0, 2])
    assert radius(controls, 29) < radius(before, 29)
    assert controls[29, 0, 2] > before[29, 0, 2] and wall(controls) < wall(before)
    return {
        "baseline_sha256": BASELINE_SHA,
        "rings": [e["ring"] for e in entries],
        "all_other_control_vertices_identical": True,
        "socket_outer_radius_before_after": [radius(a, 29) for a in (before, controls)],
        "straight_wall_height_before_after": [wall(a) for a in (before, controls)],
        "flare_to_wall_join_height_before_after": [float(a[29, 0, 2]) for a in (before, controls)],
        "socket_to_stem_seat_height_before_after": [float(a[38, 0, 2]) for a in (before, controls)],
    }, before


def build(config, out):
    if config["source_sha256"] != BASELINE_SHA:
        raise ValueError("This profile belongs to another source model")
    source = verified_source()
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    obj = editable_mesh(scene)
    settings = json.loads(scene["mission_material_config"])
    before = read_controls(obj.data, int(obj["ring_segments"]))
    after = apply_profile(before, config["rings"])
    # Carry over actual per-light assignments, including the three finial-only lights.
    assignments = {}
    old_collections = set()
    for light in (o for o in scene.objects if o.type == "LIGHT"):
        collection = light.light_linking.receiver_collection
        if collection:
            assignments[light.name] = (collection.name, [o["mission_render_region"] for o in collection.objects])
            old_collections.add(collection)
            light.light_linking.receiver_collection = None
    receivers = {o["mission_render_region"]: o for o in scene.objects if o.get("mission_render_region")}
    socket_faces = len(receivers["stem-socket"].data.polygons)
    source_atlas = {name: atlas_signature(o.data) for name, o in receivers.items()}
    for receiver in receivers.values():
        bpy.data.objects.remove(receiver, do_unlink=True)
    for collection in old_collections:
        bpy.data.collections.remove(collection)
    bpy.data.collections.remove(bpy.data.collections["Queen render regions"])
    obj.data.vertices.foreach_set("co", after.ravel())
    obj.data.update()
    bpy.context.view_layer.update()
    parts, report = partition(scene, obj, socket_band=True, collar_band=True, split_collars=True,
                              socket_face_count=socket_faces)
    indexed = {part["mission_render_region"]: part for part in parts}
    new_atlas = {name: atlas_signature(o.data) for name, o in indexed.items()}
    if new_atlas != source_atlas:
        raise ValueError("A surface crossed into a different set of lights")
    floor = next(entry["lower_height"] for entry in report if entry["name"] == "stem-socket")
    settings["stem_socket_receiver_isolation"]["z_interval"][0] = floor
    for name, (group, regions) in assignments.items():
        link(bpy.data.objects[name], [indexed[key] for key in regions], group.removeprefix("Receivers "))
    for part in parts:
        part.hide_set(True)
    settings["finial_receiver_isolation"]["render_regions"] = report
    digest = hashlib.sha256(after.tobytes()).hexdigest()
    for key in ("stem_socket_receiver_isolation", "collar_receiver_isolation"):
        settings[key]["closed_controls_sha256"] = digest
    # The new normals catch the base strip and right shoulder spot differently.
    # Preserve their color, position and light links when setting the fitted powers.
    changes = {}
    specifications = {light["name"]: light for light in settings["lights"]}
    for name, factor in config.get("reflection_strength", {}).items():
        if name not in {"Display fitted base-key", "Socket crescent 08"} or not 0 < factor <= 1:
            raise ValueError(f"Unexpected local reflection adjustment: {name} {factor}")
        lamp = bpy.data.objects[name].data
        previous = lamp.energy
        lamp.energy = previous * factor
        specifications[name]["energy"] = lamp.energy
        changes[name] = {"factor": factor, "before": previous, "after": lamp.energy}
    settings[FEATURE] = {
        "source_sha256": BASELINE_SHA,
        "baseline_control_sha256": hashlib.sha256(before.tobytes()).hexdigest(),
        "rings": config["rings"],
        "socket_partition": {"lower_height": floor, "faces": socket_faces, "atlas_hashes": source_atlas},
        "reflection_power": changes,
    }
    settings["variant"] = config["variant"]
    scene["mission_material_config"] = json.dumps(settings)
    scene["mission_variant"] = config["variant"]
    out.mkdir(exist_ok=True, parents=True)
    scene.render.filepath = str(out / "wood.png")
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out / "queen.blend"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    cfg = json.loads(args.profile.read_text())
    variant = cfg["variant"]
    if Path(variant).name != variant or variant in ("", ".", ".."):
        raise ValueError("Expected a trial directory name")
    build(cfg, ROOT / "build/queen-mission" / variant)

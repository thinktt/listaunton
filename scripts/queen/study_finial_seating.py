"""Stage a reversible compact seated-egg study for the current queen.

The selected reference shows the finial as a compact egg held deeper inside the
inverted bowl. This study changes only the exposed cap rings 108–116, anchored
at ring 107. The crown, bowl, collar stack, stem, raised socket shelf/drop,
foot, material, light rig, UVs, saved camera, and source registration remain
fixed. It writes only a staged candidate under build/.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))

from queen_scene import editable_mesh
from refine_socket_flare import read_controls, replace_meridian
from study_foot_lip import digest, radius, render_views

ANCHOR_RING = 107
CAP_RINGS = tuple(range(108, 117))


def apply_compaction(before: np.ndarray, height_factor: float, radial_factor: float) -> np.ndarray:
    if not 0.70 <= height_factor < 1.0:
        raise ValueError("height factor must be in [0.70, 1.0)")
    if not 0.85 <= radial_factor <= 1.0:
        raise ValueError("radial factor must be in [0.85, 1.0]")
    after = before.copy()
    anchor = float(before[ANCHOR_RING, :, 2].mean())
    for ring in CAP_RINGS:
        after[ring, :, 2] = anchor + (before[ring, :, 2] - anchor) * height_factor
        lengths = np.linalg.norm(after[ring, :, :2], axis=1)
        after[ring, :, :2] *= radial_factor

    if not np.all(np.diff(after[ANCHOR_RING:, 0, 2]) > 0):
        raise ValueError("finial cap no longer rises monotonically from its seat")
    before_radii = np.array([radius(before, ring) for ring in range(ANCHOR_RING, 117)])
    after_radii = np.array([radius(after, ring) for ring in range(ANCHOR_RING, 117)])
    if not np.array_equal(np.sign(np.diff(after_radii)), np.sign(np.diff(before_radii))):
        raise ValueError("finial cap changed its established radial egg profile")
    if not np.all(after_radii > 0):
        raise ValueError("finial cap contains a nonpositive radius")
    keep = np.ones(len(before), dtype=bool)
    keep[list(CAP_RINGS)] = False
    if not np.array_equal(before[keep], after[keep]):
        raise ValueError("finial study escaped its declared cap rings")
    return after


def compose_validation_config(settings: dict, before: np.ndarray, after: np.ndarray, variant: str) -> dict:
    feature = settings.get("side_shape_study")
    if not feature or "config" not in feature:
        raise ValueError("This study needs a recorded side-shape baseline")
    config = copy.deepcopy(feature["config"])
    radii = config.setdefault("radii", {})
    offsets = config.setdefault("z_offsets", {})
    changed = []
    for ring in range(len(after)):
        before_radius = radius(before, ring)
        after_radius = radius(after, ring)
        if abs(after_radius - before_radius) > 1e-8:
            radii[str(ring)] = after_radius
            changed.append(ring)
        z_delta = float(after[ring, 0, 2] - before[ring, 0, 2])
        if abs(z_delta) > 1e-8:
            offsets[str(ring)] = float(offsets.get(str(ring), 0.0)) + z_delta
            changed.append(ring)
    if sorted(set(changed)) != list(CAP_RINGS):
        raise ValueError(f"unexpected finial control scope: {sorted(set(changed))}")
    config["variant"] = variant
    config["intent"] = {
        **config.get("intent", {}),
        "compact_seated_finial": {
            "changed_rings": list(CAP_RINGS),
            "anchor_ring": ANCHOR_RING,
            "description": "Compact only the exposed egg cap while retaining the existing bowl-to-finial junction.",
            "composed_from_variant": feature["config"].get("variant"),
        },
    }
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "models/queen/queen-rebuilt.blend")
    parser.add_argument("--variant", required=True)
    parser.add_argument("--height-factor", type=float, default=0.84)
    parser.add_argument("--radial-factor", type=float, default=0.94)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--output-root", type=Path, default=ROOT / "build/queen-mission")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    if Path(args.variant).name != args.variant or args.samples < 1:
        raise ValueError("variant must be a simple path component and samples must be positive")

    source = args.source.resolve()
    source_sha = digest(source)
    print("FINIAL_SEAT_STAGE load", flush=True)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    control = editable_mesh(scene)
    before = read_controls(control.data, int(control["ring_segments"]))
    after = apply_compaction(before, args.height_factor, args.radial_factor)
    settings = json.loads(scene["mission_material_config"])
    config = compose_validation_config(settings, before, after, args.variant)
    config["intent"]["compact_seated_finial"].update({
        "height_factor": args.height_factor, "radial_factor": args.radial_factor,
        "top_lowering": float(before[-1, 0, 2] - after[-1, 0, 2]),
    })

    print("FINIAL_SEAT_STAGE rebuild_receivers", flush=True)
    partition = replace_meridian(scene, control, settings, after, preserve_face_assignments=True)
    settings["side_shape_study"] = {
        "source_sha256": config["source_sha256"],
        "config": config,
        "control_sha256": hashlib.sha256(after.tobytes()).hexdigest(),
    }
    settings["finial_seating_study"] = {
        "source_sha256": source_sha, "anchor_ring": ANCHOR_RING, "cap_rings": list(CAP_RINGS),
        "height_factor": args.height_factor, "radial_factor": args.radial_factor,
        "top_lowering": float(before[-1, 0, 2] - after[-1, 0, 2]),
        "unchanged_body_sha256": hashlib.sha256(before[:ANCHOR_RING + 1].tobytes()).hexdigest(),
        "receiver_partition": partition,
    }
    settings["variant"] = args.variant
    scene["mission_material_config"] = json.dumps(settings, sort_keys=True)
    scene["mission_variant"] = args.variant

    output = args.output_root / args.variant
    output.mkdir(parents=True, exist_ok=True)
    (output / "profile.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    (output / "parameters.json").write_text(json.dumps({
        "source": str(source), "source_sha256": source_sha, "variant": args.variant,
        "samples": args.samples, "anchor_ring": ANCHOR_RING, "cap_rings": list(CAP_RINGS),
        "height_factor": args.height_factor, "radial_factor": args.radial_factor,
        "top_lowering": float(before[-1, 0, 2] - after[-1, 0, 2]), "geometry_only": True,
    }, indent=2) + "\n", encoding="utf-8")
    print("FINIAL_SEAT_STAGE save", flush=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "queen.blend"), compress=True)
    print("FINIAL_SEAT_STAGE render", flush=True)
    render_views(scene, output, args.samples)
    if digest(source) != source_sha:
        raise RuntimeError("source model changed during the study")
    print("FINIAL_SEAT_STUDY_RENDERED", args.variant, flush=True)


if __name__ == "__main__":
    main()

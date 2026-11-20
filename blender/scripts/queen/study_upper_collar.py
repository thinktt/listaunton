"""Stage a reversible, radius-only fine-upper-collar study for the current queen.

The selected-detail contour leaves a small amount of room to slim the upper
turned ring. This tool touches only the inner seven controls of that ring;
the socket shelf/drop, lower collars, crown body, bowl, seated egg, material,
lights, UVs, saved 54-degree camera, and source registration are preserved.
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


# Preserve the lower and upper join rings so the adjustment remains a fine
# turned bead rather than an unintended change to the neighbouring spacers.
UPPER_WEIGHTS = {75: 0.35, 76: 0.70, 77: 0.95, 78: 1.00, 79: 0.95, 80: 0.70, 81: 0.35}


def apply_narrowing(before: np.ndarray, peak_delta: float) -> np.ndarray:
    if not 0.0 < peak_delta <= 0.02:
        raise ValueError("peak delta must be between zero and 0.02 Blender units")
    after = before.copy()
    for ring, weight in UPPER_WEIGHTS.items():
        source_radius = radius(before, ring)
        target_radius = source_radius - peak_delta * weight
        if target_radius <= 0:
            raise ValueError("upper-collar radius became nonpositive")
        lengths = np.linalg.norm(after[ring, :, :2], axis=1)
        after[ring, :, :2] *= (target_radius / lengths)[:, None]

    profile = np.array([radius(after, ring) for ring in range(74, 83)])
    peak = int(np.argmax(profile)) + 74
    if peak != 78:
        raise ValueError(f"unexpected upper-collar crest at ring {peak}")
    if not np.all(np.diff(profile[:5]) >= -1e-6) or not np.all(np.diff(profile[4:]) <= 1e-6):
        raise ValueError("upper collar no longer forms one smooth rounded bead")
    untouched = np.ones(len(before), dtype=bool)
    untouched[list(UPPER_WEIGHTS)] = False
    if not np.array_equal(before[untouched], after[untouched]):
        raise ValueError("upper-collar study escaped its declared ring scope")
    return after


def compose_validation_config(settings: dict, before: np.ndarray, after: np.ndarray, variant: str) -> dict:
    feature = settings.get("side_shape_study")
    if not feature or "config" not in feature:
        raise ValueError("This study needs a recorded side-shape baseline")
    config = copy.deepcopy(feature["config"])
    radii = config.setdefault("radii", {})
    changed = []
    for ring in range(len(after)):
        if abs(radius(after, ring) - radius(before, ring)) > 1e-8:
            radii[str(ring)] = radius(after, ring)
            changed.append(ring)
        if abs(float(after[ring, 0, 2] - before[ring, 0, 2])) > 1e-8:
            raise ValueError("upper-collar study must not alter height")
    if sorted(changed) != sorted(UPPER_WEIGHTS):
        raise ValueError(f"unexpected upper-collar scope: {changed}")
    config["variant"] = variant
    config["intent"] = {
        **config.get("intent", {}),
        "upper_collar_narrowing": {
            "changed_rings": sorted(UPPER_WEIGHTS),
            "description": "Narrow only the upper collar's rounded bead while preserving all heights and join rings.",
            "composed_from_variant": feature["config"].get("variant"),
        },
    }
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "models/queen/queen-rebuilt.blend")
    parser.add_argument("--variant", required=True)
    parser.add_argument("--peak-delta", type=float, default=0.006)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--output-root", type=Path, default=ROOT / "build/queen-mission")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    if Path(args.variant).name != args.variant or args.samples < 1:
        raise ValueError("variant must be a simple path component and samples must be positive")

    source = args.source.resolve()
    source_sha = digest(source)
    print("UPPER_COLLAR_STAGE load", flush=True)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    control = editable_mesh(scene)
    before = read_controls(control.data, int(control["ring_segments"]))
    after = apply_narrowing(before, args.peak_delta)
    settings = json.loads(scene["mission_material_config"])
    config = compose_validation_config(settings, before, after, args.variant)
    config["intent"]["upper_collar_narrowing"]["peak_delta"] = args.peak_delta

    print("UPPER_COLLAR_STAGE rebuild_receivers", flush=True)
    partition = replace_meridian(scene, control, settings, after, preserve_face_assignments=True)
    settings["side_shape_study"] = {
        "source_sha256": config["source_sha256"],
        "config": config,
        "control_sha256": hashlib.sha256(after.tobytes()).hexdigest(),
    }
    settings["upper_collar_narrowing_study"] = {
        "source_sha256": source_sha,
        "ring_weights": UPPER_WEIGHTS,
        "peak_delta": args.peak_delta,
        "radii_before_after": {str(ring): [radius(before, ring), radius(after, ring)] for ring in range(74, 83)},
        "all_heights_identical": bool(np.array_equal(before[:, :, 2], after[:, :, 2])),
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
        "samples": args.samples, "peak_delta": args.peak_delta, "ring_weights": UPPER_WEIGHTS,
        "geometry_only": True, "all_heights_identical": bool(np.array_equal(before[:, :, 2], after[:, :, 2])),
    }, indent=2) + "\n", encoding="utf-8")
    print("UPPER_COLLAR_STAGE save", flush=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "queen.blend"), compress=True)
    print("UPPER_COLLAR_STAGE render", flush=True)
    render_views(scene, output, args.samples)
    if digest(source) != source_sha:
        raise RuntimeError("source model changed during the study")
    print("UPPER_COLLAR_STUDY_RENDERED", args.variant, flush=True)


if __name__ == "__main__":
    main()

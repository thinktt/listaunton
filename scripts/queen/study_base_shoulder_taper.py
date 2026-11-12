"""Stage a reversible source-constrained Queen upper-base shoulder study.

The active model is never overwritten.  A small radial taper is applied only
across the broad upper-base rings, leaving the low foot, raised socket shelf,
steep drop, stem, collar stack, crown, material, lighting, camera, and source
registration exact.  This isolates the fixed-camera residual where the model
is a few pixels wide through the upper flare while its accepted low-foot
support remains protected.
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

from queen_scene import editable_mesh, set_material
from refine_socket_flare import read_controls, replace_meridian
from study_foot_lip import render_views
from study_base_socket_compression import configure_cycles


# This covers only the broad raised base, not the low support ring (2–9) or
# the shelf/drop beginning at 24.  Symmetric weights preserve a continuous
# turned contour, peaking just below the shoulder's widest point.
SHOULDER_WEIGHTS = {
    13: 0.12,
    14: 0.34,
    15: 0.62,
    16: 0.88,
    17: 1.00,
    18: 0.82,
    19: 0.56,
    20: 0.32,
    21: 0.14,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def radius(controls: np.ndarray, ring: int) -> float:
    return float(np.linalg.norm(controls[ring, :, :2], axis=1).mean())


def taper(before: np.ndarray, peak_delta: float) -> np.ndarray:
    if not 0.0 < peak_delta <= 0.02:
        raise ValueError("peak_delta must be in (0, 0.02]")
    after = before.copy()
    for ring, weight in SHOULDER_WEIGHTS.items():
        old = radius(before, ring)
        target = old - peak_delta * weight
        if target <= 0:
            raise ValueError("shoulder taper inverted a radius")
        lengths = np.linalg.norm(after[ring, :, :2], axis=1)
        after[ring, :, :2] *= (target / lengths)[:, None]
    if not np.array_equal(before[:13], after[:13]) or not np.array_equal(before[22:], after[22:]):
        raise ValueError("study escaped its declared shoulder-ring scope")
    profile = np.array([radius(after, ring) for ring in range(12, 23)])
    crest = int(profile.argmax()) + 12
    if crest not in (16, 17):
        raise ValueError(f"unexpected upper-base crest at ring {crest}")
    if not np.all(np.diff(profile[: crest - 11]) >= -1e-6):
        raise ValueError("shoulder no longer rises smoothly to its crest")
    if not np.all(np.diff(profile[crest - 12 :]) <= 1e-6):
        raise ValueError("shoulder no longer falls smoothly into the flare")
    return after


def compose_config(settings: dict, before: np.ndarray, after: np.ndarray, variant: str, peak_delta: float) -> dict:
    feature = settings.get("side_shape_study")
    if not feature or "config" not in feature:
        raise ValueError("study needs the accepted side-shape configuration")
    config = copy.deepcopy(feature["config"])
    radii = config.setdefault("radii", {})
    for ring in SHOULDER_WEIGHTS:
        radii[str(ring)] = radius(after, ring)
    config["variant"] = variant
    config["intent"] = {
        **config.get("intent", {}),
        "base_shoulder_taper": {
            "changed_rings": sorted(SHOULDER_WEIGHTS),
            "peak_delta": peak_delta,
            "description": "Narrow only the broad upper-base shoulder to test the fixed-camera contour residual; preserve the accepted low foot and the shelf/drop socket exactly.",
            "composed_from_variant": feature["config"].get("variant"),
        },
    }
    return config


def render_fixed(scene: bpy.types.Scene, output: Path, samples: int) -> None:
    """Make the two registered camera renders needed for a fast source test."""
    configure_cycles(scene, samples)
    output.mkdir(parents=True, exist_ok=True)
    control = editable_mesh(scene)
    wood = control.data.materials[0]
    set_material(scene, wood)
    scene.render.filepath = str(output / "fixed-wood.png")
    bpy.ops.render.render(write_still=True)
    clay = bpy.data.materials.new("Queen shoulder taper inspection clay")
    clay.use_nodes = True
    shader = clay.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (0.24, 0.26, 0.29, 1.0)
    shader.inputs["Roughness"].default_value = 0.32
    set_material(scene, clay)
    scene.render.filepath = str(output / "fixed-neutral.png")
    bpy.ops.render.render(write_still=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "models/queen/queen-rebuilt.blend")
    parser.add_argument("--variant", required=True)
    parser.add_argument("--peak-delta", type=float, required=True)
    parser.add_argument("--samples", type=int, default=32)
    parser.add_argument("--fixed-only", action="store_true",
                        help="Render only the two registered camera views for a quick contour decision.")
    parser.add_argument("--output-root", type=Path, default=ROOT / "build/queen-mission")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    if Path(args.variant).name != args.variant or args.samples < 1:
        raise ValueError("variant must be a simple directory name and samples must be positive")

    source = args.source.resolve()
    source_sha = digest(source)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    control = editable_mesh(scene)
    before = read_controls(control.data, int(control["ring_segments"]))
    after = taper(before, args.peak_delta)
    settings = json.loads(scene["mission_material_config"])
    config = compose_config(settings, before, after, args.variant, args.peak_delta)
    partition = replace_meridian(scene, control, settings, after, preserve_face_assignments=True)
    settings["side_shape_study"] = {
        "source_sha256": config["source_sha256"],
        "config": config,
        "control_sha256": hashlib.sha256(after.tobytes()).hexdigest(),
    }
    settings["base_shoulder_taper_study"] = {
        "source_sha256": source_sha,
        "peak_delta": args.peak_delta,
        "ring_weights": SHOULDER_WEIGHTS,
        "radii_before_after": {
            str(ring): [radius(before, ring), radius(after, ring)]
            for ring in range(12, 23)
        },
        "receiver_partition": partition,
    }
    settings["variant"] = args.variant
    scene["mission_material_config"] = json.dumps(settings, sort_keys=True)
    scene["mission_variant"] = args.variant

    output = args.output_root / args.variant
    output.mkdir(parents=True, exist_ok=True)
    (output / "profile.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    (output / "parameters.json").write_text(
        json.dumps(
            {
                "source": str(source),
                "source_sha256": source_sha,
                "variant": args.variant,
                "peak_delta": args.peak_delta,
                "samples": args.samples,
                "fixed_only": args.fixed_only,
                "changed_rings": sorted(SHOULDER_WEIGHTS),
                "geometry_only": True,
                "all_other_rings_identical": bool(np.array_equal(before[:13], after[:13]) and np.array_equal(before[22:], after[22:])),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "queen.blend"), compress=True)
    if args.fixed_only:
        render_fixed(scene, output, args.samples)
    else:
        render_views(scene, output, args.samples)
    if digest(source) != source_sha:
        raise RuntimeError("source model changed during the study")
    print("BASE_SHOULDER_TAPER_STUDY_RENDERED", args.variant, flush=True)


if __name__ == "__main__":
    main()

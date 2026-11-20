"""Stage a reversible lower-foot profile study for the current queen.

The elevated Lichess silhouettes agree closely through the broad base, but the
active model's lowest visible lip closes a little too quickly. This tool only
widens the lower perimeter into a slightly straighter, more supported rim. It
does not alter the flare, raised socket shelf, steep socket drop, stem, collars,
crown, material, lights, camera, or reference registration.

It deliberately writes only a staged blend and renders under build/; promoting
an accepted candidate remains an explicit separate operation.
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
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))

from queen_scene import editable_mesh, set_material
from refine_socket_flare import read_controls, replace_meridian
from study_base_socket_compression import combined_validation_config, configure_cycles


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Ring 5 is the existing maximum lower-foot radius; ring 6 keeps the adjacent
# vertical rim from pinching back abruptly. The result is a flatter, slightly
# wider support rather than a new bulb or a change to the broad flared body.
LIP_WEIGHTS = {
    2: 0.22,
    3: 0.56,
    4: 0.89,
    5: 1.00,
    6: 0.78,
    7: 0.56,
    8: 0.33,
    9: 0.12,
}


def radius(controls: np.ndarray, ring: int) -> float:
    return float(np.linalg.norm(controls[ring, :, :2], axis=1).mean())


def apply_lip_roll(before: np.ndarray, peak_delta: float) -> np.ndarray:
    if not 0.0 < peak_delta <= 0.03:
        raise ValueError("peak delta must be between zero and 0.03 Blender units")
    after = before.copy()
    for ring, weight in LIP_WEIGHTS.items():
        source_radius = radius(before, ring)
        target_radius = source_radius + peak_delta * weight
        lengths = np.linalg.norm(after[ring, :, :2], axis=1)
        after[ring, :, :2] *= (target_radius / lengths)[:, None]

    # Keep the existing single, controlled outer foot crest. The profile rises
    # through the lower support and falls continuously toward the groove.
    revised = np.array([radius(after, ring) for ring in range(1, 12)])
    crest = int(np.argmax(revised)) + 1
    if crest not in (5, 6):
        raise ValueError(f"unexpected lower-foot crest at ring {crest}")
    if not np.all(np.diff(revised[:crest]) >= -1e-6):
        raise ValueError("lower foot no longer rises smoothly to its crest")
    if not np.all(np.diff(revised[crest - 1:]) <= 1e-6):
        raise ValueError("lower foot no longer falls smoothly toward the groove")
    if not np.array_equal(before[12:], after[12:]):
        raise ValueError("foot-lip study escaped its declared ring scope")
    return after


def compose_validation_config(
    settings: dict, before: np.ndarray, after: np.ndarray, variant: str
) -> dict:
    """Extend the current recorded meridian without flattening its history."""
    feature = settings.get("side_shape_study")
    if not feature or "config" not in feature:
        raise ValueError("This study needs a recorded side-shape baseline")
    if not np.array_equal(before[10:], after[10:]):
        raise ValueError("foot-lip study escaped its declared rings")
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
    if sorted(set(changed)) != sorted(LIP_WEIGHTS):
        raise ValueError(f"unexpected foot-lip control scope: {sorted(set(changed))}")
    config["variant"] = variant
    config["intent"] = {
        **config.get("intent", {}),
        "foot_lip_roll": {
            "changed_rings": sorted(LIP_WEIGHTS),
            "peak_delta": None,
            "description": "Broaden only the lowest foot into a flatter supported rim; all rings 12+ are bit-identical.",
            "composed_from_variant": feature["config"].get("variant"),
        },
    }
    return config


def render_views(scene: bpy.types.Scene, output: Path, samples: int) -> None:
    """Render a fixed-camera geometry diagnostic plus a shared-scale side view."""
    configure_cycles(scene, samples)
    output.mkdir(parents=True, exist_ok=True)
    control = editable_mesh(scene)
    wood = control.data.materials[0]
    set_material(scene, wood)
    scene.render.filepath = str(output / "fixed-wood.png")
    bpy.ops.render.render(write_still=True)

    clay = bpy.data.materials.new("Queen foot-lip inspection clay")
    clay.use_nodes = True
    bsdf = clay.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.24, 0.26, 0.29, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.32
    set_material(scene, clay)
    scene.render.filepath = str(output / "fixed-neutral.png")
    bpy.ops.render.render(write_still=True)

    camera = scene.camera
    camera.data.shift_x = camera.data.shift_y = 0.0
    camera.data.sensor_fit = "VERTICAL"
    camera.data.ortho_scale = 6.6
    camera.location = (0.0, -16.0, 2.55)
    camera.rotation_euler = (Vector((0.0, 0.0, 2.55)) - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 600, 900
    set_material(scene, wood)
    scene.render.filepath = str(output / "side-wood.png")
    bpy.ops.render.render(write_still=True)
    set_material(scene, clay)
    scene.render.filepath = str(output / "side-neutral.png")
    bpy.ops.render.render(write_still=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "models/queen/queen-rebuilt.blend")
    parser.add_argument("--variant", required=True)
    parser.add_argument("--peak-delta", type=float, default=0.018)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--output-root", type=Path, default=ROOT / "build/queen-mission")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    if Path(args.variant).name != args.variant or args.samples < 1:
        raise ValueError("variant must be a simple path component and samples must be positive")

    source = args.source.resolve()
    source_sha = digest(source)
    print("FOOT_LIP_STAGE load", flush=True)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    control = editable_mesh(scene)
    before = read_controls(control.data, int(control["ring_segments"]))
    after = apply_lip_roll(before, args.peak_delta)

    settings = json.loads(scene["mission_material_config"])
    config = compose_validation_config(settings, before, after, args.variant)
    config["intent"]["foot_lip_roll"]["peak_delta"] = args.peak_delta
    print("FOOT_LIP_STAGE rebuild_receivers", flush=True)
    partition = replace_meridian(scene, control, settings, after, preserve_face_assignments=True)
    settings["side_shape_study"] = {
        "source_sha256": config["source_sha256"],
        "config": config,
        "control_sha256": hashlib.sha256(after.tobytes()).hexdigest(),
    }
    settings["foot_lip_study"] = {
        "source_sha256": source_sha,
        "ring_weights": LIP_WEIGHTS,
        "peak_delta": args.peak_delta,
        "radii_before_after": {
            str(ring): [radius(before, ring), radius(after, ring)] for ring in range(1, 12)
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
                "samples": args.samples,
                "peak_delta": args.peak_delta,
                "ring_weights": LIP_WEIGHTS,
                "geometry_only": True,
                "all_rings_12_plus_identical": bool(np.array_equal(before[12:], after[12:])),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("FOOT_LIP_STAGE save", flush=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "queen.blend"), compress=True)
    print("FOOT_LIP_STAGE render", flush=True)
    render_views(scene, output, args.samples)
    if digest(source) != source_sha:
        raise RuntimeError("source model changed during the study")
    print("FOOT_LIP_STUDY_RENDERED", args.variant, flush=True)


if __name__ == "__main__":
    main()


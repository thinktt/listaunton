"""Render a reversible, shelf-preserving queen base/socket compression study.

The active queen is never overwritten.  The complete foot-through-socket
assembly is compressed vertically as one continuous group, then eased back to
the unchanged lower collar.  Its radial profile is deliberately untouched so
the socket's horizontal shelf and steep flare drop remain legible.
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smoothstep(value: np.ndarray) -> np.ndarray:
    value = np.clip(value, 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def compress(
    before: np.ndarray,
    factor: float,
    direct_until: int,
    blend_end: int,
    flare_bulk: float,
) -> np.ndarray:
    """Compress base controls, with an exact unchanged endpoint at blend_end."""
    if not 0.0 < factor < 1.0:
        raise ValueError("factor must be between zero and one")
    if not 1.0 <= flare_bulk <= 1.08:
        raise ValueError("flare_bulk must be between 1.0 and 1.08")
    if not 0 < direct_until < blend_end < len(before):
        raise ValueError("invalid direct/blend control-ring bounds")
    after = before.copy()
    floor = float(before[:, :, 2].min())
    z = before[:, :, 2]
    after[: direct_until + 1, :, 2] = floor + factor * (z[: direct_until + 1] - floor)
    start = float(z[direct_until, 0])
    stop = float(z[blend_end, 0])
    if not floor <= start < stop:
        raise ValueError("base-to-collar blend is not vertically ordered")
    t = (z[direct_until + 1 : blend_end + 1] - start) / (stop - start)
    # The displacement is exact at the socket top and fades smoothly to zero
    # before the accepted lower-collar geometry.
    displacement = (factor - 1.0) * (z[direct_until + 1 : blend_end + 1] - floor)
    after[direct_until + 1 : blend_end + 1, :, 2] = (
        z[direct_until + 1 : blend_end + 1] + displacement * (1.0 - smoothstep(t))
    )
    # Preserve the existing lower-collar handoff bit-for-bit rather than
    # relying on the floating-point value of smoothstep(1).
    after[blend_end] = before[blend_end]
    # A restrained outward swell in the lower flare provides the separate
    # 'fatter base' interpretation requested by the owner.  It fades before
    # both the broad foot and the socket shelf, so those established profiles
    # remain intact.
    for ring, weight in zip(range(24, 29), (0.4, 0.8, 1.0, 0.8, 0.4)):
        after[ring, :, :2] *= 1.0 + (flare_bulk - 1.0) * weight
    flare_radii = np.linalg.norm(after[23:30, :, :2], axis=2).mean(axis=1)
    if not np.all(np.diff(flare_radii) <= 1e-6):
        raise ValueError("flare bulking must retain a continuously inward drop to the socket shelf")
    return after


def measurements(
    before: np.ndarray,
    after: np.ndarray,
    factor: float,
    direct_until: int,
    blend_end: int,
    flare_bulk: float,
) -> dict:
    floor = float(before[:, :, 2].min())
    radius = lambda controls, ring: float(np.linalg.norm(controls[ring, :, :2], axis=1).mean())
    height = lambda controls, ring: float(controls[ring, 0, 2] - floor)
    named = {
        "foot_outer": 5,
        "flare_low": 24,
        "socket_shelf": 29,
        "socket_wall_top": 31,
        "socket_to_stem": 38,
        "lower_collar_start": blend_end,
    }
    return {
        "factor": factor,
        "directly_compressed_rings": [0, direct_until],
        "blend_rings": [direct_until, blend_end],
        "flare_bulk": flare_bulk,
        "radii_preserved_outside_flare": bool(
            np.array_equal(before[:24, :, :2], after[:24, :, :2])
            and np.array_equal(before[29:, :, :2], after[29:, :, :2])
        ),
        "floor_preserved": abs(float(after[:, :, 2].min()) - floor) < 1e-7,
        "upper_collar_entry_preserved": bool(np.array_equal(before[blend_end], after[blend_end])),
        "vertical_order_preserved": bool(np.all(np.diff(after[: blend_end + 1, 0, 2]) >= -1e-6)),
        "rings": {
            name: {
                "ring": ring,
                "radius": radius(before, ring),
                "height_before_after": [height(before, ring), height(after, ring)],
            }
            for name, ring in named.items()
        },
        "socket_wall_height_before_after": [
            float(before[31, 0, 2] - before[29, 0, 2]),
            float(after[31, 0, 2] - after[29, 0, 2]),
        ],
        "socket_wall_radius_before_after": [radius(before, 29), radius(after, 29)],
        "flare_radii_before_after": {
            str(ring): [radius(before, ring), radius(after, ring)] for ring in range(24, 29)
        },
    }


def configure_cycles(scene: bpy.types.Scene, samples: int) -> None:
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = True
    scene.cycles.use_light_tree = False
    scene.render.use_persistent_data = True
    try:
        preferences = bpy.context.preferences.addons["cycles"].preferences
        preferences.compute_device_type = "OPTIX"
        preferences.get_devices()
        for device in preferences.devices:
            device.use = device.type == "OPTIX"
        if any(device.use for device in preferences.devices):
            scene.cycles.device = "GPU"
    except (KeyError, TypeError, RuntimeError):
        scene.cycles.device = "CPU"


def render_views(scene: bpy.types.Scene, output: Path, samples: int) -> None:
    """Render the saved fixed camera plus a shared-scale front side view."""
    configure_cycles(scene, samples)
    output.mkdir(parents=True, exist_ok=True)
    control = editable_mesh(scene)
    wood = control.data.materials[0]
    set_material(scene, wood)
    scene.render.filepath = str(output / "fixed-wood.png")
    bpy.ops.render.render(write_still=True)

    clay = bpy.data.materials.new("Queen base compression inspection clay")
    clay.use_nodes = True
    shader = clay.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value = (0.24, 0.26, 0.29, 1.0)
    shader.inputs["Roughness"].default_value = 0.32
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


def combined_validation_config(
    settings: dict, before: np.ndarray, after: np.ndarray, variant: str
) -> dict:
    """Extend checkpoint 24's frozen-source config by the compression delta.

    This lets the established side-shape validator reconstruct the candidate
    directly from checkpoint 22 while preserving the already accepted collar
    refinements.  It is a validation record, not a change to the source image.
    """
    feature = settings.get("side_shape_study")
    if not feature or "config" not in feature:
        raise ValueError("This study must start from the accepted checkpoint-24 side-shape model")
    config = copy.deepcopy(feature["config"])
    if config.get("variant") != "224-collars-only-baseline-base":
        raise ValueError("Unexpected side-shape baseline; refuse to compose an ambiguous trial")
    offsets = {str(key): float(value) for key, value in config.get("z_offsets", {}).items()}
    radii = {str(key): float(value) for key, value in config.get("radii", {}).items()}
    # Ring 0 is the preserved floor and ring 50 is the exact lower-collar
    # handoff; only intervening affected rings need extra offsets.
    for ring in range(1, 50):
        delta = float(after[ring, 0, 2] - before[ring, 0, 2])
        if abs(delta) > 1e-8:
            offsets[str(ring)] = offsets.get(str(ring), 0.0) + delta
    for ring in range(len(after)):
        before_radius = float(np.linalg.norm(before[ring, :, :2], axis=1).mean())
        after_radius = float(np.linalg.norm(after[ring, :, :2], axis=1).mean())
        if abs(after_radius - before_radius) > 1e-8:
            radii[str(ring)] = after_radius
    config["variant"] = variant
    config["z_offsets"] = offsets
    config["radii"] = radii
    config["intent"] = {
        **config.get("intent", {}),
        "base_socket_uniform_compression": True,
        "socket_shelf_and_steep_flare_drop_preserved": True,
        "compression_source_variant": feature["config"]["variant"],
    }
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "models/queen/queen-rebuilt.blend")
    parser.add_argument("--variant", required=True)
    parser.add_argument("--factor", type=float, required=True)
    parser.add_argument("--direct-until", type=int, default=38)
    parser.add_argument("--blend-end", type=int, default=50)
    parser.add_argument("--samples", type=int, default=64)
    parser.add_argument("--flare-bulk", type=float, default=1.0)
    parser.add_argument(
        "--output-root",
        type=Path,
        help="Optional local staging root; defaults to build/queen-mission in the repository.",
    )
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])
    if Path(args.variant).name != args.variant or args.samples < 1:
        raise ValueError("variant must be a single path component and samples must be positive")

    source = args.source.resolve()
    source_sha = digest(source)
    print("BASE_COMPRESSION_STAGE load", flush=True)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False)
    scene = bpy.context.scene
    control = editable_mesh(scene)
    before = read_controls(control.data, int(control["ring_segments"]))
    after = compress(before, args.factor, args.direct_until, args.blend_end, args.flare_bulk)
    report = measurements(before, after, args.factor, args.direct_until, args.blend_end, args.flare_bulk)
    if not all(
        report[key]
        for key in ("radii_preserved_outside_flare", "floor_preserved", "upper_collar_entry_preserved", "vertical_order_preserved")
    ):
        raise RuntimeError("compression did not preserve its declared constraints")

    settings = json.loads(scene["mission_material_config"])
    validation_config = combined_validation_config(settings, before, after, args.variant)
    print("BASE_COMPRESSION_STAGE rebuild_receivers", flush=True)
    # The profile moves across historical Z partition boundaries.  Carry the
    # original per-face receiver membership by its immutable atlas UV instead
    # of reclassifying it by a shifted height.
    partition = replace_meridian(scene, control, settings, after, preserve_face_assignments=True)
    settings["base_socket_compression_study"] = {
        "source_sha256": source_sha,
        "method": "Uniform vertical compression through the socket-to-stem ring, smooth return to the unchanged lower collar, plus an explicitly recorded restrained lower-flare swell; all non-flare radii, UVs, material and lights preserved.",
        "partition": partition,
        "measurements": report,
    }
    settings["side_shape_study"] = {
        "source_sha256": validation_config["source_sha256"],
        "config": validation_config,
        "control_sha256": hashlib.sha256(after.tobytes()).hexdigest(),
    }
    settings["variant"] = args.variant
    scene["mission_material_config"] = json.dumps(settings, sort_keys=True)
    scene["mission_variant"] = args.variant

    output = (args.output_root if args.output_root else ROOT / "build" / "queen-mission") / args.variant
    output.mkdir(parents=True, exist_ok=True)
    (output / "profile.json").write_text(json.dumps(validation_config, indent=2) + "\n", encoding="utf-8")
    print("BASE_COMPRESSION_STAGE save", flush=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "queen.blend"), compress=True)
    print("BASE_COMPRESSION_STAGE render", flush=True)
    render_views(scene, output, args.samples)
    if digest(source) != source_sha:
        raise RuntimeError("source model changed during the study")
    (output / "parameters.json").write_text(
        json.dumps(
            {
                "source": str(source),
                "source_sha256": source_sha,
                "variant": args.variant,
                "samples": args.samples,
                "measurements": report,
                "geometry_only": True,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("BASE_SOCKET_COMPRESSION_STUDY_RENDERED", args.variant, flush=True)


if __name__ == "__main__":
    main()

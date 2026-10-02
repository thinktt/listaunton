"""Export the evaluated queen meshes for a standalone WebGL2 viewer.

Run with Blender in background mode. The source .blend is only read.
Binary layout: interleaved little-endian float32 XYZ/NXYZ vertices followed by
little-endian uint32 triangle indices. No geometry is decimated or simplified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np


DELIVERABLES = Path(__file__).resolve().parent
WORK = DELIVERABLES.parents[1] / "work" / "queen-hires"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def bounds(positions: np.ndarray) -> dict:
    low = positions.min(axis=0)
    high = positions.max(axis=0)
    return {"min": low.tolist(), "max": high.tolist(),
            "center": ((low + high) * .5).tolist(),
            "size": (high - low).tolist()}


def camera_metadata(scene, graph):
    camera = scene.camera
    if camera is None:
        raise RuntimeError("Saved scene has no active reference camera.")
    width = int(scene.render.resolution_x * scene.render.resolution_percentage / 100)
    height = int(scene.render.resolution_y * scene.render.resolution_percentage / 100)
    projection = camera.calc_matrix_camera(
        graph, x=width, y=height,
        scale_x=scene.render.pixel_aspect_x, scale_y=scene.render.pixel_aspect_y)
    return {
        "type": camera.data.type,
        "worldToCamera": [float(value) for row in camera.matrix_world.inverted() for value in row],
        "projectionMatrix": [float(value) for row in projection for value in row],
        "orthoScale": float(camera.data.ortho_scale),
        "shiftX": float(camera.data.shift_x), "shiftY": float(camera.data.shift_y),
        "width": width, "height": height,
        "pixelAspectX": float(scene.render.pixel_aspect_x),
        "pixelAspectY": float(scene.render.pixel_aspect_y),
        "clipStart": float(camera.data.clip_start), "clipEnd": float(camera.data.clip_end),
        "matrixConvention": "4x4 row-major; multiplication by a column vector",
    }


def main():
    args_after_separator = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blend", type=Path, default=DELIVERABLES / "queen-rebuilt.blend")
    parser.add_argument("--binary", type=Path, default=WORK / "viewer-mesh.bin")
    parser.add_argument("--metadata", type=Path, default=WORK / "viewer-mesh.json")
    args = parser.parse_args(args_after_separator)
    blend_path = args.blend.resolve()
    before_hash = sha256(blend_path)
    before_stat = blend_path.stat()
    bpy.ops.wm.open_mainfile(filepath=str(blend_path), load_ui=False)

    objects = sorted((obj for obj in bpy.context.scene.objects
                      if obj.type == "MESH" and not obj.hide_render), key=lambda obj: obj.name)
    expected_count = 1 if bpy.context.scene.get('continuous_crown') else 2
    if len(objects) != expected_count:
        raise RuntimeError(f"Expected {expected_count} queen mesh objects, found {len(objects)}: {[obj.name for obj in objects]}")
    # Match render subdivision settings in memory. Nothing is saved back to Blender.
    for obj in objects:
        for modifier in obj.modifiers:
            modifier.show_viewport = modifier.show_render
            if modifier.type == "SUBSURF":
                modifier.levels = modifier.render_levels
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    graph.update()

    vertex_blocks, index_blocks, parts = [], [], []
    vertex_offset = index_offset = 0
    for obj in objects:
        evaluated = obj.evaluated_get(graph)
        evaluated_mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=graph)
        try:
            evaluated_mesh.calc_loop_triangles()
            vertex_count = len(evaluated_mesh.vertices)
            triangle_count = len(evaluated_mesh.loop_triangles)
            if vertex_count == 0 or triangle_count == 0:
                raise RuntimeError(f"Empty evaluated mesh: {obj.name}")
            if not all(poly.use_smooth for poly in evaluated_mesh.polygons):
                raise RuntimeError(f"{obj.name} contains flat-shaded faces; shared-vertex normals would not preserve their shading.")
            positions = np.empty(vertex_count * 3, dtype=np.float32)
            normals = np.empty(vertex_count * 3, dtype=np.float32)
            indices = np.empty(triangle_count * 3, dtype=np.int32)
            evaluated_mesh.vertices.foreach_get("co", positions)
            evaluated_mesh.vertices.foreach_get("normal", normals)
            evaluated_mesh.loop_triangles.foreach_get("vertices", indices)
            positions = positions.reshape((-1, 3))
            normals = normals.reshape((-1, 3))

            transform = np.array(evaluated.matrix_world, dtype=np.float64)
            positions = positions @ transform[:3, :3].T + transform[:3, 3]
            normal_transform = np.linalg.inv(transform[:3, :3]).T
            normals = normals @ normal_transform.T
            lengths = np.linalg.norm(normals, axis=1)
            if not np.all(np.isfinite(positions)) or not np.all(np.isfinite(normals)):
                raise RuntimeError(f"Non-finite mesh attributes: {obj.name}")
            if np.any(lengths < 1e-8):
                raise RuntimeError(f"Zero-length normals in {obj.name}")
            normals /= lengths[:, None]
            if indices.min() < 0 or indices.max() >= vertex_count:
                raise RuntimeError(f"Out-of-range triangle index in {obj.name}")
            if np.linalg.det(transform[:3, :3]) < 0:
                indices = indices.reshape((-1, 3))[:, [0, 2, 1]].reshape(-1)

            interleaved = np.empty((vertex_count, 6), dtype="<f4")
            interleaved[:, :3] = positions
            interleaved[:, 3:] = normals
            global_indices = (indices.astype(np.uint64) + vertex_offset)
            if global_indices.max() > np.iinfo(np.uint32).max:
                raise RuntimeError("Combined mesh exceeds uint32 index range.")
            global_indices = global_indices.astype("<u4")
            vertex_blocks.append(interleaved)
            index_blocks.append(global_indices)
            parts.append({
                "name": obj.name,
                "vertexOffset": vertex_offset, "vertexCount": vertex_count,
                "indexOffset": index_offset, "indexCount": int(indices.size),
                "triangleCount": triangle_count, "bounds": bounds(interleaved[:, :3]),
                "subdivisionLevels": [modifier.render_levels for modifier in obj.modifiers
                                      if modifier.type == "SUBSURF" and modifier.show_render],
            })
            vertex_offset += vertex_count
            index_offset += int(indices.size)
        finally:
            evaluated.to_mesh_clear()

    vertices = np.concatenate(vertex_blocks)
    indices = np.concatenate(index_blocks)
    if indices.size % 3:
        raise RuntimeError("Triangle index buffer length is not a multiple of three.")
    normal_lengths = np.linalg.norm(vertices[:, 3:].astype(np.float64), axis=1)
    if not np.all(np.isfinite(vertices)) or not np.allclose(normal_lengths, 1.0, atol=2e-6):
        raise RuntimeError("Combined mesh failed finite/unit-normal validation.")
    mesh_bounds = bounds(vertices[:, :3])
    if min(mesh_bounds["size"]) <= 0 or mesh_bounds["size"][2] <= max(mesh_bounds["size"][:2]):
        raise RuntimeError(f"Unexpected queen bounds: {mesh_bounds}")

    args.binary.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    binary_tmp = args.binary.with_suffix(args.binary.suffix + ".tmp")
    with binary_tmp.open("wb") as stream:
        stream.write(vertices.tobytes(order="C"))
        stream.write(indices.tobytes(order="C"))
    expected_length = int(vertices.nbytes + indices.nbytes)
    if binary_tmp.stat().st_size != expected_length:
        raise RuntimeError("Binary length does not match vertex/index buffer lengths.")
    # Verify the actual serialized file, not only the arrays used to construct it.
    serialized = binary_tmp.read_bytes()
    read_vertices = np.frombuffer(serialized, dtype="<f4", count=vertices.size).reshape((-1, 6))
    read_indices = np.frombuffer(serialized, dtype="<u4", offset=vertices.nbytes)
    if not np.array_equal(vertices, read_vertices) or not np.array_equal(indices, read_indices):
        raise RuntimeError("Binary round-trip validation failed.")
    after_hash = sha256(blend_path)
    after_stat = blend_path.stat()
    if before_hash != after_hash or before_stat.st_mtime_ns != after_stat.st_mtime_ns:
        raise RuntimeError("Source .blend changed while exporting; output withheld.")

    metadata = {
        "schemaVersion": 1,
        "sourceBlend": str(blend_path), "sourceSha256": before_hash,
        "sourceUnchanged": True, "binary": str(args.binary.resolve()),
        "coordinateSystem": "Blender world XYZ, right-handed, +Z up; no axis conversion",
        "endianness": "little", "vertexType": "float32", "indexType": "uint32",
        "vertexCount": int(vertices.shape[0]), "indexCount": int(indices.size),
        "triangleCount": int(indices.size // 3),
        "vertexStrideBytes": 24, "positionOffsetBytes": 0, "normalOffsetBytes": 12,
        "vertexByteOffset": 0, "vertexByteLength": int(vertices.nbytes),
        "indexByteOffset": int(vertices.nbytes), "indexByteLength": int(indices.nbytes),
        "totalByteLength": expected_length, "bounds": mesh_bounds, "parts": parts,
        "referenceCamera": camera_metadata(bpy.context.scene, graph),
        "validation": {
            "allAttributesFinite": True, "allIndicesInRange": bool(indices.max() < len(vertices)),
            "normalLengthMin": float(normal_lengths.min()), "normalLengthMax": float(normal_lengths.max()),
            "binaryRoundTripExact": True, "sourceHashAndMtimeUnchanged": True,
            "simplificationApplied": False,
        },
    }
    binary_tmp.replace(args.binary)
    metadata_tmp = args.metadata.with_suffix(args.metadata.suffix + ".tmp")
    metadata_tmp.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    metadata_tmp.replace(args.metadata)
    print("VIEWER_MESH_EXPORT " + json.dumps(metadata))


if __name__ == "__main__":
    main()

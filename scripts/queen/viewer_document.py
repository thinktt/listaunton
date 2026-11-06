"""Assemble the queen WebGL viewer from a verified mesh and wood atlas."""
import base64
import json
from pathlib import Path

FIELDS = (
    "vertexCount", "indexCount", "triangleCount", "vertexStrideBytes", "vertexByteLength",
    "indexByteOffset", "totalByteLength", "bounds", "sourceSha256", "referenceCamera",
    "uvOffsetBytes", "uvLayer", "materialConfig",
)


def make_document(meta, mesh_bytes, texture_bytes, *, studies=None, payload=""):
    if len(mesh_bytes) != meta["totalByteLength"] or meta["referenceCamera"]["type"] != "ORTHO":
        raise ValueError("Expected the complete queen mesh and its orthographic reference camera")
    public = {key: meta[key] for key in FIELDS}
    if studies:
        public["baseStudies"] = studies
    template = Path(__file__).with_name("viewer-template.html").read_text(encoding="utf-8")
    return (template.replace("__MESH_META__", json.dumps(public,separators=(",",":")))
            .replace("__MESH_BASE64__", base64.b64encode(mesh_bytes).decode("ascii"))
            .replace("__WOOD_BASE64__", base64.b64encode(texture_bytes).decode("ascii"))
            .replace("__STUDY_PATCHES__",payload))

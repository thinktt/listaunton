"""File layout and reversible externalization of the legacy page payloads."""

import base64
import binascii
import hashlib
from pathlib import PurePosixPath
import re


TOKEN = re.compile(rb"[A-Za-z0-9+/]{256,}={0,2}")
ASSET = re.compile(rb"@LISTAUNTON_ASSET:([a-f0-9]{64})@")
RASTER = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tif", ".tiff", ".exr"}
OUTPUT = {".bin", ".glb", ".gltf", ".obj", ".stl", ".fbx", ".log", ".blend1", ".blend2"}
WEB = {".html", ".htm", ".js", ".css"}
CODE = {".py", ".cjs", ".ps1"}
REFERENCE = re.compile(r"^(?:(?:black|white)-)?(?:original(?:-white)?|reference|ref|hi-res-queen|side-01(?:-cutout)?)$")
TEXTURE = re.compile(
    r"^(?:wood-atlas[-\w]*|king-pigment-atlas[-\w]*|queen-pigment-albedo[-\w]*|"
    r"pawn-(?:walnut|fine-slopes|varnish)[-\w]*|bishop-boxwood-albedo|"
    r"walnut-(?:fine-)?albedo|albedo|pigment|fixed-source|.*-generated|"
    r"(?:inferred|derived|reference-delit)[-\w]*)$"
)


def classify(path):
    """Return the category of a file at its pre-migration relative path."""
    p = PurePosixPath(path)
    root, suffix = p.parts[0], p.suffix.lower()
    if (root in {"build", "dist", "output", "_site"} or suffix in OUTPUT
            or p.name == "mesh.json" or path == "docs/camera-study/angle-residuals.svg"):
        return "output"
    if root == "references":
        return "input"
    if suffix in RASTER:
        if root == "assets" and p.parts[1] in {"candidates", "side-views"}:
            return "input"
        if p.name == "empty-board.png":
            return "input"
        if REFERENCE.fullmatch(p.stem) or TEXTURE.fullmatch(p.stem):
            return "input"
        return "output"
    if root in {"models", "history", "scripts"} or suffix in CODE | {".blend", ".npz", ".npy"}:
        return "blender"
    if suffix in WEB | {".svg"} or p.name == ".nojekyll":
        return "page"
    if root == "assets":
        if p.parts[1] in {"candidates", "side-views"}:
            return "input"
        return "blender"
    return "root"


def source_path(path, kind):
    base = {"output": "dist/replay-cache", "input": "inputs", "blender": "blender", "page": "page"}
    return f"{base[kind]}/{path}" if kind in base else path


def externalize(raw, write=None):
    """Keep page source and replace media tokens with content-addressed keys."""
    def replace(match):
        token = match[0]
        if len(token) % 4:
            return token
        lead = raw[max(0, match.start() - 256):match.start()]
        try:
            payload = base64.b64decode(token, validate=True)
        except binascii.Error:
            return token
        image = (
            payload.startswith((b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"glTF"))
            or payload.startswith(b"RIFF") and payload[8:12] == b"WEBP"
            or re.search(rb"data:image/[\w.+-]+;base64,$", lead)
        )
        octets = b"application/octet-stream" in lead.rsplit(b"<script", 1)[-1] and lead.endswith(b">")
        if not (image or octets or len(token) >= 16_384):
            return token
        # Preserve the exact original encoding, including malformed unused bits.
        if base64.b64encode(payload) != token:
            raise ValueError("A page contains noncanonical base64")
        digest = hashlib.sha256(payload).hexdigest()
        if write is not None:
            write(digest, payload)
        return f"@LISTAUNTON_ASSET:{digest}@".encode()

    return TOKEN.sub(replace, raw)


def hydrate(raw, read):
    def replace(match):
        digest = match[1].decode()
        data = read(digest)
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError(f"Corrupted page payload {digest}")
        return base64.b64encode(data)

    return ASSET.sub(replace, raw)


def site_path(path):
    p = PurePosixPath(path)
    if p.suffix in CODE | {".blend", ".npz", ".npy", ".log"}:
        return False
    return (
        len(p.parts) == 1 and (p.suffix in {".html", ".md"} or p.name == ".nojekyll")
        or p.parts[0] in {"assets", "references"}
        or path.startswith(("docs/camera-study/", "docs/pawn-shared-base/"))
    )

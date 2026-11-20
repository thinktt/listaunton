#!/usr/bin/env python3
"""Build the site and create isolated legacy-layout Blender workspaces."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile

from layout import ASSET, WEB, classify, externalize, hydrate, site_path, source_path


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PAYLOADS = DIST / "payloads"
CACHE = DIST / "replay-cache"
MIGRATION = ROOT / "blender/migrated-output-manifest.json"


def project_paths():
    for folder in ("inputs", "blender", "page"):
        base = ROOT / folder
        for path in sorted(base.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            relative = path.relative_to(base)
            if folder == "blender" and len(relative.parts) == 1:
                continue
            yield relative.as_posix(), path
    for path in sorted((ROOT / "docs").rglob("*")):
        if path.is_file():
            yield path.relative_to(ROOT).as_posix(), path
    for path in sorted(ROOT.glob("*.md")):
        yield path.name, path


def output_paths(website=False):
    if CACHE.is_dir():
        for path in sorted(CACHE.rglob("*")):
            if path.is_file():
                name = path.relative_to(CACHE).as_posix()
                if not website or site_path(name):
                    yield name, path


def copy_files(entries, destination):
    for name, path in entries:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix in WEB:
            code = path.read_bytes()
            if ASSET.search(code):
                target.write_bytes(hydrate(code, lambda digest: (PAYLOADS / digest).read_bytes()))
                continue
        shutil.copy2(path, target)


def build_site():
    """Assemble a disposable static site; keep existing view behavior and CSP."""
    need = json.loads(MIGRATION.read_text())["outputs"]
    missing = [name for name in need if site_path(name) and not (CACHE / name).is_file()]
    if missing:
        raise SystemExit(f"Site output cache is missing {len(missing)} files, including {missing[0]}. "
                         "Run project.py unpack with the matching site output archive.")
    DIST.mkdir(exist_ok=True)
    output = DIST / "site"
    staging = DIST / "site-staging"
    if staging.exists():
        shutil.rmtree(staging)
    copy_files(((name, path) for name, path in project_paths() if site_path(name)), staging)
    copy_files(output_paths(website=True), staging)
    if output.exists():
        shutil.rmtree(output)
    staging.rename(output)
    print(output)


def pack_site():
    """Package only the site outputs and payloads needed by the tracked pages."""
    DIST.mkdir(exist_ok=True)
    destination = DIST / "site-outputs.tar.gz"
    listed_outputs = json.loads(MIGRATION.read_text())["outputs"]
    payloads = set()
    for name, path in project_paths():
        if site_path(name) and path.suffix in WEB:
            payloads.update(value.decode() for value in ASSET.findall(path.read_bytes()))
    with tarfile.open(destination, "w:gz", compresslevel=1) as archive:
        for name, path in output_paths(website=True):
            if name in listed_outputs:
                archive.add(path, f"replay-cache/{name}")
        for digest in sorted(payloads):
            archive.add(PAYLOADS / digest, f"payloads/{digest}")
    print(destination)


def unpack_site(archive_path):
    """Install only regular cache files under dist from a site-output archive."""
    expected = json.loads(MIGRATION.read_text())["outputs"]
    DIST.mkdir(exist_ok=True)
    with tarfile.open(archive_path) as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if (not member.isfile() or name.is_absolute() or ".." in name.parts
                    or len(name.parts) < 2):
                raise ValueError(f"Unexpected archive entry {member.name}")
            key = name.relative_to(name.parts[0]).as_posix()
            if name.parts[0] == "payloads" and "/" not in key:
                digest = key
            elif name.parts[0] == "replay-cache" and site_path(key) and key in expected:
                digest = expected[key]
            else:
                raise ValueError(f"Unexpected archive entry {member.name}")
            data = archive.extractfile(member).read()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError(f"Output hash mismatch for {member.name}")
            path = DIST / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)


def make_workspace():
    """Give legacy scripts their original paths without writing into tracked sources."""
    target = DIST / "workspace"
    if target.exists():
        raise SystemExit(f"{target} already exists. Move it aside to make a fresh workspace.")
    copy_files(project_paths(), target)
    copy_files(output_paths(), target)
    if (DIST / "legacy-build").is_dir():
        (target / "build").symlink_to("../legacy-build", target_is_directory=True)
    print(target)


def capture(files):
    """Import explicit updated pages or generated files from the Blender workspace."""
    manifest = json.loads(MIGRATION.read_text())
    workspace = DIST / "workspace"
    pending = []
    for name in files:
        source = (workspace / name).resolve()
        if not source.is_relative_to(workspace) or not source.is_file():
            raise ValueError(f"Expected a workspace file: {name}")
        name = source.relative_to(workspace).as_posix()
        kind = classify(name)
        if kind not in {"output", "page"}:
            raise ValueError(f"Expected a page or generated output: {name}")
        pending.append((name, source, kind))

    def write_payload(digest, data):
        PAYLOADS.mkdir(parents=True, exist_ok=True)
        (PAYLOADS / digest).write_bytes(data)

    for name, source, kind in pending:
        content = source.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        target = ROOT / source_path(name, kind)
        if kind == "output":
            manifest["outputs"][name] = digest
        elif source.suffix in WEB:
            template = externalize(content, write_payload)
            manifest["externalized_pages"].pop(name, None)
            if template != content:
                manifest["externalized_pages"][name] = digest
            content = template
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    MIGRATION.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def recover(backup, revision):
    """Check out exact pre-rewrite sources and outputs in an ignored directory."""
    git = ["git", "-C", str(backup.resolve())]
    oid = subprocess.check_output([*git, "rev-parse", "--verify", revision + "^{commit}"]).decode().strip()
    target = DIST / "recovered" / oid
    target.mkdir(parents=True, exist_ok=False)
    process = subprocess.Popen([*git, "archive", oid], stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            archive.extractall(target, filter="data")
    finally:
        process.stdout.close()
        code = process.wait()
    if code:
        raise SystemExit(code)
    print(target)


def render(model, blender, frame):
    """Render a saved Blender scene and camera into dist/renders."""
    model = model.resolve()
    if model.suffix.lower() != ".blend" or not model.is_file():
        raise SystemExit(f"Invalid Blender model {model}")
    output = DIST / "renders" / model.stem
    output.mkdir(parents=True, exist_ok=True)
    paths = [str(model), str(output / "frame-####")]
    if blender.lower().endswith(".exe") and os.name != "nt":
        paths = [subprocess.check_output(["wslpath", "-w", path], text=True).strip() for path in paths]
    subprocess.run([blender, "-b", paths[0], "-o", paths[1], "-F", "PNG", "-f", str(frame)], check=True)
    print(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("site", "pack", "workspace"):
        commands.add_parser(name)
    commands.add_parser("unpack").add_argument("archive", type=Path)
    commands.add_parser("capture").add_argument("files", nargs="+")
    restore = commands.add_parser("recover")
    restore.add_argument("backup", type=Path)
    restore.add_argument("revision")
    renderer = commands.add_parser("render")
    renderer.add_argument("model", type=Path)
    renderer.add_argument("--blender", default="blender")
    renderer.add_argument("--frame", type=int, default=1)
    args = parser.parse_args()
    if args.command == "site":
        build_site()
    elif args.command == "pack":
        pack_site()
    elif args.command == "unpack":
        unpack_site(args.archive)
    elif args.command == "capture":
        capture(args.files)
    elif args.command == "workspace":
        make_workspace()
    elif args.command == "recover":
        recover(args.backup, args.revision)
    else:
        render(args.model, args.blender, args.frame)


if __name__ == "__main__":
    main()

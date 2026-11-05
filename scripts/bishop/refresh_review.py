"""Refresh accepted bishop review pages, optionally syncing the existing local preview.

Run only after accepting and validating model/render/mesh/atlas assets.
This does not render, choose a trial, push, or deploy a site.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--preview-dir', type=Path)
args = parser.parse_args()
for script in ['build_viewer.py', 'build_review.py']:
    subprocess.run([sys.executable, str(root/'scripts/bishop'/script)], cwd=root, check=True)
if args.preview_dir:
    destination = args.preview_dir.resolve()
    if destination == root.resolve():
        parser.error('The preview destination must be separate from the source repository.')
    destination.mkdir(parents=True, exist_ok=True)
    for relative in ['bishop-review.html', 'bishop-model.html']:
        shutil.copy2(root/relative, destination/relative)
    for relative in ['assets/bishop', 'models/bishop']:
        shutil.copytree(root/relative, destination/relative, dirs_exist_ok=True)
    print(f'Synchronized accepted bishop pages and assets to {destination}')

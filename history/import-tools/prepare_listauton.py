"""Assemble the project without removing the original working files."""
from pathlib import Path
import hashlib
import json
import shutil

SOURCE = Path(__file__).resolve().parent.parent
DEST = SOURCE / 'work/listauton-staging'
OUT = SOURCE / 'outputs/queen-hires'
WORK = SOURCE / 'work/queen-hires'
manifest = []

def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    manifest.append({'source': str(source.relative_to(SOURCE)).replace('\\', '/'),
                     'destination': str(target.relative_to(DEST)).replace('\\', '/'),
                     'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})

def tree(source, target):
    for path in sorted(source.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix not in {'.pyc', '.blend1'}:
            copy(path, target / path.relative_to(source))

for path in OUT.iterdir():
    if path.suffix in {'.png', '.json'}:
        copy(path, DEST / 'assets/queen' / path.name)
copy(OUT / 'queen-rebuilt.blend', DEST / 'models/queen/queen-rebuilt.blend')
copy(OUT / 'README.txt', DEST / 'docs/queen-notes.txt')
copy(OUT / 'queen-parts.html', DEST / 'queen-parts.html')
for name in ['review.html', 'queen-3d.html']:
    html = (OUT / name).read_text(encoding='utf-8')
    for png in OUT.glob('*.png'):
        html = html.replace(png.name, 'assets/queen/' + png.name)
    html = html.replace('href="queen-rebuilt.blend"', 'href="models/queen/queen-rebuilt.blend"')
    (DEST / name).write_text(html, encoding='utf-8')
tree(SOURCE / 'outputs/lichess-staunton-3d', DEST / 'references/lichess-staunton-3d')
tree(WORK, DEST / 'history/queen-hires')
tree(SOURCE / 'outputs/queen-model', DEST / 'history/queen-original/outputs')
tree(SOURCE / 'work/queen-before-revision', DEST / 'history/queen-original/before-revision')
for path in (SOURCE / 'work').iterdir():
    if path.is_file() and path.name != Path(__file__).name:
        copy(path, DEST / 'history/queen-original/work' / path.name)
for name in ['viewer-mesh.bin', 'viewer-mesh.json', 'viewer-camera.json', 'viewer-camera-check.json']:
    copy(WORK / name, DEST / 'build/queen' / name)
# Preserve source layout as evidence, while active scripts live under scripts/queen.
for name in ['build_queen.py', 'export_viewer_mesh.py', 'overlay_qa.py']:
    copy(OUT / name, DEST / 'history/imported-active-scripts' / name)
(DEST / 'docs/import-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'copied_files': len(manifest), 'staging': str(DEST),
                  'copied_bytes': sum((DEST / item['destination']).stat().st_size for item in manifest)}, indent=2))

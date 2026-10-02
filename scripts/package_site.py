"""Assemble only the files needed by the public presentation."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / '_site'
DEST.mkdir(exist_ok=True)
for name in ('index.html', 'queen-3d.html', 'review.html', 'queen-parts.html'):
    shutil.copy2(ROOT / name, DEST / name)
for name in ('assets', 'models'):
    shutil.copytree(ROOT / name, DEST / name, dirs_exist_ok=True)
(DEST / '.nojekyll').touch()
print(f'Site packaged: {DEST}')

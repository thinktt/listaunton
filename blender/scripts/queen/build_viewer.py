"""Embed the exact evaluated queen viewer and preserved parts map into review.html."""
from pathlib import Path
from viewer_document import make_document
import json
import hashlib
import re

root = Path(__file__).resolve().parents[2]
work = root / 'build' / 'queen'
out = root / 'review.html'
meta = json.loads((work / 'viewer-mesh.json').read_text())
blend = root / 'models' / 'queen' / 'queen-rebuilt.blend'
if hashlib.sha256(blend.read_bytes()).hexdigest() != meta['sourceSha256']:
    raise RuntimeError('Export the current Blender model before rebuilding its viewer.')
if meta.get('referenceCamera', {}).get('type') != 'ORTHO':
    raise RuntimeError('This viewer requires the saved orthographic reference camera.')
texture = root / meta['materialConfig'].get('texture','assets/queen/walnut-albedo.png')
html = make_document(meta, (work / 'viewer-mesh.bin').read_bytes(), texture.read_bytes())
page=out.read_text(encoding='utf-8')
parts=(Path(__file__).resolve().parent/'parts-template.html').read_text(encoding='utf-8')
for ident,document in [('viewer-document',html),('parts-document',parts)]:
    encoded=json.dumps(document,ensure_ascii=False).replace('</','<\\/')
    pattern=r'(<script id="'+ident+r'"[^>]*>).*?(</script>)'
    page,count=re.subn(pattern,lambda m:m.group(1)+encoded+m.group(2),page,flags=re.S)
    if count!=1:raise RuntimeError('Expected exactly one embedded '+ident)
out.write_text(page,encoding='utf-8')
print(f'{out}: {out.stat().st_size:,} bytes; {meta["triangleCount"]:,} triangles')

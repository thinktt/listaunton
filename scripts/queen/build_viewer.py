"""Embed the exact evaluated queen viewer and preserved parts map into review.html."""
from pathlib import Path
import base64
import json
import hashlib
import re

root = Path(__file__).resolve().parents[2]
work = root / 'build' / 'queen'
out = root / 'review.html'
meta = json.loads((work / 'viewer-mesh.json').read_text())
fields = ['vertexCount', 'indexCount', 'triangleCount', 'vertexStrideBytes',
          'vertexByteLength', 'indexByteOffset', 'totalByteLength', 'bounds', 'sourceSha256',
          'referenceCamera']
blend = root / 'models' / 'queen' / 'queen-rebuilt.blend'
if hashlib.sha256(blend.read_bytes()).hexdigest() != meta['sourceSha256']:
    raise RuntimeError('Export the current Blender model before rebuilding its viewer.')
if meta.get('referenceCamera', {}).get('type') != 'ORTHO':
    raise RuntimeError('This viewer requires the saved orthographic reference camera.')
public_meta = {k: meta[k] for k in fields}
template = (Path(__file__).resolve().parent / 'viewer-template.html').read_text(encoding='utf-8')
payload = base64.b64encode((work / 'viewer-mesh.bin').read_bytes()).decode('ascii')
html = template.replace('__MESH_META__', json.dumps(public_meta, separators=(',', ':')))
html = html.replace('__MESH_BASE64__', payload)
page=out.read_text(encoding='utf-8')
parts=(Path(__file__).resolve().parent/'parts-template.html').read_text(encoding='utf-8')
for ident,document in [('viewer-document',html),('parts-document',parts)]:
    encoded=json.dumps(document,ensure_ascii=False).replace('</','<\\/')
    pattern=r'(<script id="'+ident+r'"[^>]*>).*?(</script>)'
    page,count=re.subn(pattern,lambda m:m.group(1)+encoded+m.group(2),page,flags=re.S)
    if count!=1:raise RuntimeError('Expected exactly one embedded '+ident)
out.write_text(page,encoding='utf-8')
print(f'{out}: {out.stat().st_size:,} bytes; {meta["triangleCount"]:,} triangles')

"""Package the exact evaluated queen mesh in a standalone, offline HTML viewer."""
from pathlib import Path
import base64
import json
import hashlib

root = Path(__file__).resolve().parents[2]
work = root / 'build' / 'queen'
out = root / 'queen-3d.html'
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
out.write_text(html, encoding='utf-8')
print(f'{out}: {out.stat().st_size:,} bytes; {meta["triangleCount"]:,} triangles')

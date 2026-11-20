"""Package the exact evaluated queen mesh in a standalone, offline HTML viewer."""
from pathlib import Path
import base64
import json

root = Path(__file__).resolve().parents[2]
work = root / 'work' / 'queen-hires'
out = root / 'outputs' / 'queen-hires' / 'queen-3d.html'
meta = json.loads((work / 'viewer-mesh.json').read_text())
fields = ['vertexCount', 'indexCount', 'triangleCount', 'vertexStrideBytes',
          'vertexByteLength', 'indexByteOffset', 'totalByteLength', 'bounds', 'sourceSha256']
public_meta = {k: meta[k] for k in fields}
template = (work / 'viewer-template.html').read_text(encoding='utf-8')
payload = base64.b64encode((work / 'viewer-mesh.bin').read_bytes()).decode('ascii')
html = template.replace('__MESH_META__', json.dumps(public_meta, separators=(',', ':')))
html = html.replace('__MESH_BASE64__', payload)
out.write_text(html, encoding='utf-8')
print(f'{out}: {out.stat().st_size:,} bytes; {meta["triangleCount"]:,} triangles')

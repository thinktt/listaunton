"""Embed the bishop reference, render and exact exported mesh in a local HTML page."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import struct

root = Path(__file__).resolve().parents[2]
assets = root/'assets/bishop'
out = root/'bishop-model.html'
parser = argparse.ArgumentParser()
parser.add_argument('--allow-placeholder', action='store_true', help='Write a waiting page when model inputs have not arrived yet.')
args = parser.parse_args()
required = [assets/name for name in ['mesh.json', 'mesh.bin', 'reference.png', 'render.png', 'render-clay.png', 'original.png']]
missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
if missing:
    if not args.allow_placeholder:
        raise SystemExit('Bishop model inputs missing: '+', '.join(missing))
    out.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Bishop model</title><style>:root{color-scheme:dark;font:16px system-ui;background:#15191f;color:#e9e5dc}body{display:grid;place-items:center;min-height:85vh;margin:0}p{color:#a8afb8}</style><div><h1>Bishop model</h1><p>The first geometry comparison is being prepared.</p></div></html>')
    print('Wrote temporary bishop-model.html while waiting for model assets.')
    raise SystemExit(0)

meta = json.loads((assets/'mesh.json').read_text())
blend = root/'models/bishop/bishop-rebuilt.blend'
if not blend.is_file() or hashlib.sha256(blend.read_bytes()).hexdigest() != meta['sourceSha256']:
    raise RuntimeError('Export the current Blender model before rebuilding its viewer.')
if meta.get('referenceCamera', {}).get('type') != 'ORTHO':
    raise RuntimeError('The bishop viewer requires its saved orthographic reference camera.')
fields = ['vertexCount', 'indexCount', 'triangleCount', 'vertexStrideBytes', 'vertexByteLength', 'indexByteOffset', 'totalByteLength', 'bounds', 'sourceSha256', 'referenceCamera']
if 'material' in meta: fields.append('material')
public_meta = {key: meta[key] for key in fields}
mesh = (assets/'mesh.bin').read_bytes()
assert len(mesh) == meta['totalByteLength'], 'Mesh binary length does not match metadata.'
assert meta['vertexStrideBytes'] == 32, 'Expected interleaved position, normal and UV.'
assert meta['vertexCount'] * 32 == meta['vertexByteLength'] == meta['indexByteOffset']
assert meta['indexCount'] == meta['triangleCount'] * 3
assert meta['indexByteOffset'] + meta['indexCount'] * 4 == len(mesh)
for image in ['reference.png', 'render.png', 'render-clay.png', 'original.png']:
    raw = (assets/image).read_bytes()
    assert raw[:8] == b'\x89PNG\r\n\x1a\n', 'Expected PNG input: '+image
    width,height = struct.unpack('>II',raw[16:24])
    assert width == height, 'Comparison images must share a square frame.'

override = assets/'original-alignment.json'
if override.is_file():
    alignment = json.loads(override.read_text())
else:
    registrations = json.loads((root/'assets/candidates/alignment.json').read_text())
    alignment = next(item for item in registrations['pieces']['bishop'] if item['id'] == 'candidate-1')
alignment = {key: alignment[key] for key in ['scale', 'x', 'y']}
assert alignment['scale'] > 0

def data_uri(path):
    return 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')

html = (Path(__file__).with_name('viewer-template.html')).read_text(encoding='utf-8')
html = html.replace('__MESH_META__',json.dumps(public_meta,separators=(',',':')))
html = html.replace('__MESH_BASE64__',base64.b64encode(mesh).decode('ascii'))
html = html.replace('__REFERENCE_IMAGE__',data_uri(assets/'reference.png'))
html = html.replace('__RENDER_IMAGE__',data_uri(assets/'render.png'))
html = html.replace('__NEUTRAL_IMAGE__',data_uri(assets/'render-clay.png'))
texture=root/meta['material']['texture']
assert hashlib.sha256(texture.read_bytes()).hexdigest()==meta['material']['textureSha256']
html = html.replace('__WOOD_IMAGE__',data_uri(texture))
html = html.replace('__ORIGINAL_IMAGE__',data_uri(assets/'original.png'))
html = html.replace('__ORIGINAL_ALIGNMENT__',json.dumps(alignment,separators=(',',':')))
html = html.replace('__BLACK_IMAGE__',data_uri(assets/'black-original.png'))
black_alignment=json.loads((assets/'black-alignment.json').read_text())
html = html.replace('__BLACK_ALIGNMENT__',json.dumps(black_alignment,separators=(',',':')))
out.write_text(html,encoding='utf-8')
print(f'{out}: {out.stat().st_size:,} bytes; {meta["triangleCount"]:,} triangles')

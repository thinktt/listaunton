"""Pin the side gallery to its accepted bishop measurements before small detail edits."""
from pathlib import Path
import hashlib
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
path = ROOT/'assets/side-views/scale.json'
data = json.loads(path.read_text())
row = next(item for item in data['pieces'] if item['piece']=='bishop')
old = row['model'].copy()
baseline = 'history/bishop-mission-001/'
meta_path = ROOT/(baseline+'mesh.json')
binary_path = ROOT/(baseline+'mesh.bin')
profile_path = ROOT/(baseline+'profile.json')
meta = json.loads(meta_path.read_text());raw = binary_path.read_bytes()
vertices = np.ndarray((meta['vertexCount'],3), dtype='<f4', buffer=raw,
                      strides=(meta['vertexStrideBytes'],4)).astype(float)
lo = vertices.min(0);hi = vertices.max(0);height = float(hi[2]-lo[2])
base = vertices[vertices[:,2]<=lo[2]+.25*height]
diameter = float(max(base[:,:2].max(0)-base[:,:2].min(0)))
assert height==old['height'] and diameter==old['base_diameter'] and len(base)==old['base_vertex_count']
assert json.loads(profile_path.read_text())['elevation']==54
row['model'].update(
    file=baseline+'mesh.json',
    sha256=hashlib.sha256(meta_path.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
    binary=baseline+'mesh.bin',
    binary_sha256=hashlib.sha256(raw).hexdigest(),
    camera_file=baseline+'profile.json',
    camera_sha256=hashlib.sha256(profile_path.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),
    sizing_baseline='Accepted side-gallery sizing pinned to the first boxwood checkpoint; later button/foot refinements do not rescale the owner-chosen gallery.'
)
path.write_text(json.dumps(data,indent=2)+'\n')
print('Pinned bishop sizing provenance to its byte-identical archive; display, manual scales and order unchanged.')

"""Refresh bishop source hashes only when the approved sizing remains exact."""
from pathlib import Path
import hashlib,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'assets/side-views/scale.json';report=json.loads(path.read_text());row=next(r for r in report['pieces'] if r['piece']=='bishop');old=row['model'].copy()
meta=json.loads((ROOT/old['file']).read_text());raw=(ROOT/old['binary']).read_bytes()
pts=np.ndarray((meta['vertexCount'],3),dtype='<f4',buffer=raw,strides=(meta['vertexStrideBytes'],4)).astype(float)
lo=pts.min(0);hi=pts.max(0);height=float(hi[2]-lo[2]);base=pts[pts[:,2]<=lo[2]+.25*height];widths=base[:,:2].max(0)-base[:,:2].min(0)
assert height==old['height'] and float(max(widths))==old['base_diameter'] and len(base)==old['base_vertex_count'],'Do not silently change approved sizing.'
row['model']['sha256']=hashlib.sha256((ROOT/old['file']).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
row['model']['binary_sha256']=hashlib.sha256(raw).hexdigest()
path.write_text(json.dumps(report,indent=2)+'\n')
out=ROOT/'docs/bishop-mission/iteration-001/measurement-provenance.json'
out.write_text(json.dumps({'measurements_and_display_unchanged':True,'height':height,'base_diameter':float(max(widths)),'base_vertex_count':len(base),'previous_metadata_hash':old['sha256'],'current_metadata_hash':row['model']['sha256'],'previous_binary_hash':old['binary_sha256'],'current_binary_hash':row['model']['binary_sha256']},indent=2)+'\n')
print('Refreshed two bishop provenance hashes; all side-view sizing preserved.')

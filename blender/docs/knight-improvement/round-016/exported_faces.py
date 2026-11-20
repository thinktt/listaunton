"""Check face area and corner data in the geometry actually consumed by WebGL."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
objects=Path(sys.argv[1]);model=Path(sys.argv[2]);out=Path(sys.argv[3])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
meta=json.loads((objects/'mesh.json').read_bytes());stream=objects/'mesh.bin';raw=stream.read_bytes()
assert meta['sourceSha256']==sha(model) and meta['vertexStrideBytes']==32
assert len(raw)==meta['totalByteLength']
verts=np.frombuffer(raw[:meta['indexByteOffset']],dtype='<f4').reshape(-1,8)
indices=np.frombuffer(raw[meta['indexByteOffset']:],dtype='<u4');assert len(indices)==meta['indexCount']
assert np.isfinite(verts).all() and np.allclose(np.linalg.norm(verts[:,3:6],axis=1),1,atol=.002)
summary={}
for group in meta['parts']:
    start=group['indexOffset'];inds=indices[start:start+group['indexCount']].reshape(-1,3)
    points=verts[inds,:3].astype(np.float64)
    double=np.linalg.norm(np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0]),axis=1)
    summary[group['name']]={'triangle_count':len(double),'double_area_minimum':float(double.min()),'double_area_below_1e-10':int((double<1e-10).sum())}
info={'model':sha(model),'mesh':sha(stream),'parts':summary,'method':'Decode the WebGL vertex and index streams in world coordinates. Check finite positions, normals and UVs, unit normals, and doubled area below 1e-10 for each triangle.'}
out.write_text(json.dumps(info,indent=2)+'\n')
print({name:value['double_area_below_1e-10'] for name,value in summary.items()})
assert not any(row['double_area_below_1e-10'] for row in summary.values())

"""Compare a fresh bishop export with an archived identical-geometry checkpoint."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',required=True);p.add_argument('--current',default='assets/bishop');p.add_argument('--out',required=True)
a=p.parse_args();old=ROOT/a.baseline;new=ROOT/a.current
om=json.loads((old/'mesh.json').read_text());nm=json.loads((new/'mesh.json').read_text())
ab=(old/'mesh.bin').read_bytes();bb=(new/'mesh.bin').read_bytes()
aa=np.frombuffer(ab[:om['vertexByteLength']],dtype='<f4').reshape(-1,8)
ba=np.frombuffer(bb[:nm['vertexByteLength']],dtype='<f4').reshape(-1,8)
assert aa.shape==ba.shape and np.isfinite(ba).all()
assert np.array_equal(aa[:,:6],ba[:,:6])
assert ab[om['indexByteOffset']:]==bb[nm['indexByteOffset']:]
for name in ['parts','bounds','referenceCamera','triangleCount','vertexCount','vertexStrideBytes']:
    assert om[name]==nm[name],name
uv_error=float(np.max(np.abs(aa[:,6:]-ba[:,6:])))
ulps=np.abs(aa[:,6:].view(np.int32).astype(np.int64)-ba[:,6:].view(np.int32).astype(np.int64))
# This is the same established 1e-7 Boolean evaluated-UV bound used by the
# checkpoint-012 receiver audit. Control UVs are checked exactly elsewhere.
assert uv_error<1e-7 and ulps.max()<=1
record={'passed':True,'baseline':a.baseline,'current':a.current,'strict_binary_equal':ab==bb,
 'positions_normals_indices_parts_bounds_camera_exact':True,'evaluated_uv_max_error':uv_error,
 'evaluated_uv_max_float32_ulps':int(ulps.max()),'evaluated_uv_changed_components':int(np.count_nonzero(ulps)),
 'existing_uv_tolerance':1e-7,'triangles':nm['triangleCount'],
 'mesh_binary_sha256':hashlib.sha256(bb).hexdigest(),'source_model_sha256':nm['sourceSha256'],
 'texture_sha256':nm['material']['textureSha256'],
 'note':'Reevaluating the unchanged Boolean rounds some evaluated UV components by one float32 ULP. Positions, normals and topology remain exact; the independent scene audit checks exact control UVs.'}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

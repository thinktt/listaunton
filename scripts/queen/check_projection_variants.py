"""Validate physically distinct exports, original registration, and file integrity."""
from pathlib import Path
import argparse,hashlib,json,math,re
import numpy as np
from PIL import Image
parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
parser.add_argument('--allow-partial-baseline',action='store_true',help='Only for staging: validate available canonical inputs; the repository check requires all preserved files.')
args=parser.parse_args()
ROOT=args.root.resolve();A=ROOT/'assets/queen-projections'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=read(A/'variants.json');rows=manifest['variants'];info=read(A/'baseline-info.json')
preservation=read(A/'baseline-preservation.json');preserved=0
for item in preservation['files']:
 path=ROOT/item['path']
 if args.allow_partial_baseline and not path.exists():continue
 raw=path.read_bytes();actual=hashlib.sha256(raw).hexdigest()
 if actual!=item['sha256']:
  assert path.suffix.lower() in {'.json','.py','.cjs','.js','.html','.txt','.md','.css'},item['path']
  assert item.get('textLfSha256')==hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest(),item['path']
 preserved+=1
assert [r['elevation'] for r in rows]==[48,51.5,52,54,56,60,64]
assert manifest['baseline']=='angle-51-5'
assert sha(ROOT/'models/queen/queen-rebuilt.blend')==info['sourceSha256']
assert sha(ROOT/'assets/queen/reference.png')==sha(A/'reference.png')
canonical_original=ROOT/'references/lichess-staunton-3d/Black-Queen.png'
if canonical_original.exists():assert sha(canonical_original)==sha(A/'original.png')
reg=read(ROOT/'assets/queen/original-reference-alignment.json');a=read(A/'original-alignment.json')
assert abs(a['scale']-1254/(300*reg['scale']))<1e-12
assert abs(a['x']+reg['offset_x']/(3*reg['scale']))<1e-12
assert abs(a['y']+reg['offset_y']/(3*reg['scale']))<1e-12
results=[];widths=[];heights=[];profiles=[];meshes=[];saved=[]
for row in rows:
 folder=ROOT/row['assetDir'];meta=read(folder/'mesh.json');cam=read(folder/'camera.json');qa=read(folder/'geometry-check.json');binary=(folder/'mesh.bin').read_bytes()
 assert sha(ROOT/row['model'])==meta['sourceSha256'];assert cam==meta['referenceCamera'];assert cam['type']=='ORTHO'
 assert len(binary)==meta['totalByteLength']==meta['vertexByteLength']+meta['indexCount']*4
 assert meta['vertexStrideBytes']==24 and meta['indexByteOffset']==meta['vertexByteLength']==meta['vertexCount']*24
 attrs=np.frombuffer(binary[:meta['vertexByteLength']],dtype='<f4').reshape(-1,6);idx=np.frombuffer(binary[meta['indexByteOffset']:],dtype='<u4')
 assert np.isfinite(attrs).all() and idx.min()>=0 and idx.max()<len(attrs)
 assert np.max(abs(np.linalg.norm(attrs[:,3:],axis=1)-1))<2e-6
 p=attrs[:,:3];size=np.ptp(p,axis=0);assert np.allclose(p.min(0),meta['bounds']['min'],atol=1e-7);assert np.allclose(p.max(0),meta['bounds']['max'],atol=1e-7)
 assert abs(p[:,2].min())<1e-5 and qa['nonManifoldEdges']==qa['boundaryEdges']==0 and qa['signedVolume']>0
 actual=math.degrees(math.atan2(cam['worldToCamera'][9]*-1,cam['worldToCamera'][10]))
 # Camera's backward Z vector is (0,-cos(e),sin(e)).
 elevation=math.degrees(math.atan2(cam['worldToCamera'][10],-cam['worldToCamera'][9]))
 assert abs(elevation-row['elevation'])<1e-4
 assert Image.open(folder/'render.png').size==(1254,1254)
 assert Image.open(folder/'profile.png').size==(600,900)
 profile=read(folder/'profile-camera.json');profiles.append(profile)
 widths.append(float(size[0]));heights.append(float(size[2]));meshes.append(p.copy())
 results.append(dict(id=row['id'],elevation=elevation,baseWidth=float(size[0]),height=float(size[2]),triangleCount=meta['triangleCount'],meshBytes=len(binary),modelSha256=meta['sourceSha256'],closedPositiveVolume=True))
assert max(widths)-min(widths)<1e-6
assert all(heights[i+1]>heights[i] for i in range(len(heights)-1))
assert all(p==profiles[0] for p in profiles),'Front profile camera changed between variants.'
baseline=meshes[[r['id'] for r in rows].index(manifest['baseline'])]
for row,p in zip(rows,meshes):
 if row['id']!=manifest['baseline']:assert np.max(abs(p-baseline))>.015,'Geometry did not change.'
html=ROOT/'queen-projections.html'
assert html.stat().st_size<65_000_000,'Offline viewer exceeds intended65MB budget.'
assert info['reduced_mesh_check']['surface_distance_max_original_pixels']<.5
report=dict(passed=True,variants=results,fixedPhysicalBaseWidth=True,floorAtZero=True,commonProfileCamera=True,actualGeometryRefits=True,originalAndSelectedHashesAndAlignmentValid=True,reducedSurfaceCheck=info['reduced_mesh_check'],htmlBytes=html.stat().st_size,canonicalBaselineSha256=info['sourceSha256'],preservedBaselineFilesVerified=preserved,fullBaselineVerified=preserved==len(preservation['files']))
(A/'check-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))

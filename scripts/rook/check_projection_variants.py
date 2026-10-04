"""Verify preserved canonical rook, physical geometry variants and render provenance."""
from pathlib import Path
import argparse,base64,hashlib,json,math,re,struct
import numpy as np
from PIL import Image

def check(root):
 directory=root/'assets/rook-projections';manifest=json.loads((directory/'variants.json').read_text(encoding='utf-8'));baseline=json.loads((directory/'baseline-preservation.json').read_text(encoding='utf-8'))
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 def local(name):
  p=(root/name).resolve();assert p.is_relative_to(root) and p.is_file(),name;return p
 for name,expected in baseline['sha256'].items():assert sha(local(name))==expected,('Canonical rook changed',name)
 variants=manifest['variants'];assert [v['elevation'] for v in variants]==[48,52,54,56,60,64];assert manifest['baseline']=='angle-54'
 assert len({v['id'] for v in variants})==6
 canonical=json.loads((root/'assets/rook/mesh.json').read_text(encoding='utf-8'));original_cfg=json.loads((root/'scripts/rook/profile.json').read_text(encoding='utf-8'));reports=[];profile_cameras=[]
 for item in variants:
  folder=root/item['assetDir'];meta=json.loads((folder/'mesh.json').read_text(encoding='utf-8'));camera=json.loads((folder/'camera.json').read_text(encoding='utf-8'));validation=json.loads((folder/'validation.json').read_text(encoding='utf-8'));cfg=json.loads((folder/'profile.json').read_text(encoding='utf-8'));qa=json.loads((folder/'qa.json').read_text(encoding='utf-8'))
  model_hash=sha(local(item['model']));assert model_hash==meta['sourceSha256']==validation['sourceSha256'];assert validation['source_hash_matches']
  for name,key in [('render.png','renderSha256'),('profile.png','profileSha256'),('camera.json','cameraSha256')]:assert sha(folder/name)==validation[key]
  components=validation['components'];assert len(components)==5 and sum(not c['hidden_construction'] for c in components)==1
  for c in components:assert c['nonmanifold_edges']==0 and c['signed_volume']>0 and math.isfinite(c['signed_volume'])
  volumes=[c['signed_volume'] for c in components if c['hidden_construction']];assert max(volumes)-min(volumes)<1e-7
  d=cfg['turret'];assert abs((d['outer_radius']-d['inner_radius'])/d['outer_radius']-23/177)<1e-10;assert d['slot_angle_degrees']==20 and d['azimuth_degrees']==0
  assert d['top_y']+14<=d['notch_y'];assert cfg['profile'][56][1]>=d['notch_y']+8
  if item['elevation']==54:
   assert cfg['profile']==original_cfg['profile'] and cfg['turret']==original_cfg['turret'];assert cfg['y0']==cfg['profile'][0][1]
   assert np.allclose(meta['bounds']['size'],canonical['bounds']['size'],atol=1e-6)
  raw=(folder/'mesh.bin').read_bytes();assert len(raw)==meta['totalByteLength'];assert meta['vertexStrideBytes']==24;assert meta['vertexByteLength']==meta['vertexCount']*24==meta['indexByteOffset'];assert meta['indexCount']==meta['triangleCount']*3
  assert meta['indexByteOffset']+meta['indexCount']*4==len(raw);assert len(meta['parts'])==1 and meta['parts'][0]['triangleCount']==meta['triangleCount']
  vertices=np.frombuffer(raw,dtype='<f4',count=meta['vertexCount']*6).reshape(-1,6);indices=np.frombuffer(raw,dtype='<u4',offset=meta['indexByteOffset']);assert np.isfinite(vertices).all() and indices.max()<meta['vertexCount']
  normal_error=float(np.max(np.abs(np.linalg.norm(vertices[:,3:],axis=1)-1)));assert normal_error<1e-4
  lo=vertices[:,:3].min(0);hi=vertices[:,:3].max(0);assert np.allclose(lo,meta['bounds']['min']) and np.allclose(hi,meta['bounds']['max']);assert abs(float(lo[2]))<1e-6
  assert abs(float(hi[0]-lo[0])-canonical['bounds']['size'][0])<1e-6
  assert abs(item['heightToBaseWidth']-float((hi[2]-lo[2])/(hi[0]-lo[0])))<1e-6
  assert camera==meta['referenceCamera'] and camera['type']=='ORTHO' and camera['width']==camera['height']==1254
  world=np.asarray(camera['worldToCamera']).reshape(4,4);elevation=math.degrees(math.atan2(abs(world[2,2]),math.hypot(world[2,0],world[2,1])));assert abs(elevation-item['elevation'])<.001
  pc=json.loads((folder/'profile-camera.json').read_text(encoding='utf-8'));profile_cameras.append(pc)
  for name,dimensions in [('render.png',(1254,1254)),('profile.png',(600,900))]:
   with Image.open(folder/name) as image:assert image.size==dimensions;image.verify()
  for key,name in [('original','original.png'),('selected','ref.png')]:
   score=qa['images'][key];assert score['reference_sha256']==sha(root/'assets/rook'/name);assert 0<=score['silhouette_iou']<=1
  reports.append({'id':item['id'],'elevation':elevation,'baseDiameter':float(hi[0]-lo[0]),'height':float(hi[2]-lo[2]),'heightToBaseWidth':item['heightToBaseWidth'],'triangleCount':meta['triangleCount'],'closedEditableObjects':5,'uniformWallThicknessFraction':(d['outer_radius']-d['inner_radius'])/d['outer_radius'],'modelSha256':model_hash,'meshSha256':sha(folder/'mesh.bin'),'renderSha256':sha(folder/'render.png'),'originalIoU':qa['images']['original']['silhouette_iou'],'originalMask8IoU':qa['original_mask_sensitivity']['8'],'selectedIoU':qa['images']['selected']['silhouette_iou'],'normalLengthMaxError':normal_error})
 assert all(pc==profile_cameras[0] for pc in profile_cameras)
 for field in ['modelSha256','meshSha256','renderSha256']:assert len({v[field] for v in reports})==6
 html=root/'rook-projections.html'
 if html.is_file():
  text=html.read_text(encoding='utf-8');embedded=json.loads(re.search(r'<script id="projection-data"[^>]*>(.*?)</script>',text,re.S).group(1));assert embedded['baseline']=='angle-54'
  for v in embedded['variants']:
   folder=root/'assets/rook-projections'/v['id'];meta=json.loads((folder/'mesh.json').read_text(encoding='utf-8'));assert all(v['meta'][k]==meta[k] for k in v['meta'])
   blob=base64.b64decode(re.search(r'<script id="mesh-'+v['id']+r'"[^>]*>(.*?)</script>',text,re.S).group(1));assert blob==(folder/'mesh.bin').read_bytes()
   blob=base64.b64decode(re.search(r'<img id="render-'+v['id']+r'"[^>]*src="data:image/png;base64,([^"]+)"',text).group(1));assert blob==(folder/'render.png').read_bytes()
  for ident,name in [('reference-image','ref.png'),('original-image','original.png')]:
   blob=base64.b64decode(re.search(r'<img id="'+ident+r'"[^>]*src="data:image/png;base64,([^"]+)"',text).group(1));assert blob==(root/'assets/rook'/name).read_bytes()
 return {'passed':True,'canonicalRookUnchanged':True,'preservedFiles':list(baseline['sha256']),'expectedElevations':[48,52,54,56,60,64],'sameBaseDiameterAndGround':True,'sameProfileCamera':True,'actualDifferentGeometryAndRenders':True,'closedComponentsEvidence':'Blender evaluated each body union and all four equal hidden editable merlons; this checker binds those reports and image hashes to the current exported model.','variants':reports}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args=ap.parse_args();root=args.root.resolve();report=check(root)
 (root/'assets/rook-projections/check-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'docs/bishop-mission/iteration-013';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cfgpath=root/'scripts/bishop/pigment-106.json';cfg=json.loads(cfgpath.read_text());folder=root/'build/bishop-mission/106-middle-body-boxwood-grade'
record=json.loads((folder/'pigment.json').read_text());assert record['parameters']==cfg
source=root/'history/bishop-mission-012/bishop-rebuilt.blend'
assert sha(source)=='89ff709b7cb2bd3f931ee6acd083e0cb8f993e86d424c9784ec2006830b3b231'
old=np.array(Image.open(root/cfg['source']).convert('RGBA'));new=np.array(Image.open(folder/'albedo.png').convert('RGBA'))
meta=json.loads((root/cfg['capture']/'manifest.json').read_text());field=np.load(root/cfg['capture']/'position.npy');valid=np.load(root/cfg['capture']/'valid.npy')
z=(field[:,:,2]-.1)/.8*meta['encode_extent'][2]+meta['encode_min'][2]
outside=(~valid)|(z<=.96)|(z>=3.43)
assert np.array_equal(old[outside],new[outside]);assert np.array_equal(old[:,:,3],new[:,:,3])
delta=new.astype(int)-old.astype(int);assert delta.min()>=0 and delta.max()<=15
scope={'passed':True,'source_atlas_sha256':sha(root/cfg['source']),'atlas_sha256':sha(folder/'albedo.png'),
 'protected_height_intervals':[[-.1,.96],[3.43,4.7]],'protected_texels':int(outside.sum()),
 'protected_and_alpha_pixels_exact':True,'max_channel_lift_8bit':int(delta.max()),
 'no_darkening':True,'changed_texels':int(np.any(delta[:,:,:3]!=0,axis=2).sum()),
 'note':'Checks actual saved PNG bytes independently of the grade implementation. The accepted wood pattern is multiplied by a bounded smooth height field, not repainted from a new reference.'}
(out/'grade-scope.json').write_text(json.dumps(scope,indent=2)+'\n')
declaration={'source':'history/bishop-mission-012/bishop-rebuilt.blend','source_sha256':sha(source),
 'atlas':'assets/bishop/bishop-boxwood-albedo.png','atlas_sha256':sha(folder/'albedo.png'),
 'config':'scripts/bishop/pigment-106.json','config_sha256':sha(cfgpath),
 'description':'Smooth bounded boxwood color lift on socket, stem and collars. Foot, lower base, head and button atlas pixels remain exact. Old relief, geometry, lamps and 54-degree camera are retained.',
 'residual_limitation':'The inherited pigment retains broad illumination and a side/rear projection boundary. This local grade does not resolve intrinsic texture/lighting separation.'}
(out/'pigment-checkpoint.json').write_text(json.dumps(declaration,indent=2)+'\n')
print(json.dumps(scope,indent=2))

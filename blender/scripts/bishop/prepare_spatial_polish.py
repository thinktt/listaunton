"""Prepare data-only fine-grain roughness fields without editing color or normals."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--out',default='build/bishop-mission/126-polish-fields')
a=p.parse_args();out=ROOT/a.out
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve());out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
atlas=ROOT/'history/bishop-mission-015/bishop-boxwood-albedo.png'
source=ROOT/'history/bishop-mission-015/bishop-rebuilt.blend'
assert sha(source)=='dc3a11db2800b79bf45baee458d5b6a53a7602b3531137afe5db9b914a45cf07'
assert sha(atlas)=='c09df839f9ab363f5e4c2ed3d669293f99a81de59a449f85096a49e849aa8f2a'
capture=ROOT/'build/bishop-mission/099-atlas-surface';cm=json.loads((capture/'manifest.json').read_text())
assert sha(ROOT/cm['source'])==cm['source_sha256']
previous=cm['source_sha256'];lineage=[]
for relative in ['docs/bishop-mission/iteration-013/validation/pigment-validation.json','docs/bishop-mission/iteration-015/validation/pigment-validation.json']:
    report=json.loads((ROOT/relative).read_text())
    assert report['passed'] and report['geometry_uvs_material_graph_relief_camera_lights_world_and_render_path_preserved']
    assert report['source_sha256']==previous;previous=report['model_sha256'];lineage.append(dict(path=relative,sha256=sha(ROOT/relative)))
assert previous==sha(source)
position=np.load(capture/'position.npy');valid=np.load(capture/'valid.npy')
z=(position[:,:,2]-cm['encode_offset'])/cm['encode_scale']*cm['encode_extent'][2]+cm['encode_min'][2]
def smooth(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)
band=smooth((z-.19)/.08)*smooth((1.02-z)/.14)*valid
rgb=np.array(Image.open(atlas).convert('RGB'),dtype=np.float32)/255
linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
lum=np.maximum(linear@np.array([.2126,.7152,.0722],dtype=np.float32),.003)
detail=blur(np.log(lum),1)-blur(np.log(lum),6)
grain=-np.tanh(detail/.06)
variants=[('coat-grain',0,.08,1),('base-and-coat',.1,.08,1),('reversed-grain',.1,.08,-1)]
records=[]
for label,base_amp,coat_amp,sign in variants:
    field=np.ones((*grain.shape,4),dtype=np.float32)
    field[:,:,0]=np.clip(.23+base_amp*sign*grain*band,.06,.45)
    field[:,:,1]=np.clip(.10+coat_amp*sign*grain*band,.02,.3)
    field[:,:,2]=band
    assert np.all(field[:,:,0][band==0]==np.float32(.23)) and np.all(field[:,:,1][band==0]==np.float32(.10))
    path=out/(label+'.npy');np.save(path,field)
    records.append(dict(label=label,path=path.relative_to(ROOT).as_posix(),sha256=sha(path),base_amplitude=base_amp,
        coat_amplitude=coat_amp,sign=sign,base_range=[float(field[:,:,0].min()),float(field[:,:,0].max())],
        coat_range=[float(field[:,:,1].min()),float(field[:,:,1].max())]))
manifest=dict(source=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),atlas=atlas.relative_to(ROOT).as_posix(),
    atlas_sha256=sha(atlas),surface_inheritance=lineage,body_height_band=[.19,.27,.88,1.02],
    field_format='float32 RGBA, top-down rows: R base roughness, G coat roughness, B band mask, A one',
    log_luminance_blur_radii=[1,6],detail_scale=.06,source_color_preserved=True,variants=records,
    caveat='Pigment high-frequency detail is an artistic hypothesis for polish variation, not measured roughness. Broad color and shading are excluded; actual BSDF trials decide acceptance.')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
print('SPATIAL_POLISH_FIELDS_PREPARED',json.dumps(manifest),flush=True)

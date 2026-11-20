"""Bake a bounded smooth height-based pigment grade, retaining the original atlas."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',required=True)
a=p.parse_args();cfg=json.loads((ROOT/a.config).read_text());source=ROOT/cfg['source']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==cfg['source_sha256']
capture=ROOT/cfg['capture'];meta=json.loads((capture/'manifest.json').read_text())
assert sha(ROOT/meta['source'])==meta['source_sha256']
encoded=np.load(capture/'position.npy');valid=np.load(capture/'valid.npy')
height=(encoded[:,:,2]-.1)/.8*meta['encode_extent'][2]+meta['encode_min'][2]
knots=np.array([v[0] for v in cfg['height_gain_knots']]);values=np.log(np.array([v[1] for v in cfg['height_gain_knots']]))
assert np.all(np.diff(knots)>0) and np.isfinite(values).all()
index=np.clip(np.searchsorted(knots,height,side='right')-1,0,len(knots)-2)
t=np.clip((height-knots[index])/(knots[index+1]-knots[index]),0,1);t=t*t*(3-2*t)
gain=np.exp(cfg['amount']*((1-t[:,:,None])*values[index]+t[:,:,None]*values[index+1]))
old=np.array(Image.open(source).convert('RGBA'));rgb=old[:,:,:3].astype(np.float64)/255
assert old.shape[:2]==height.shape
linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
graded=linear*gain
srgb=np.where(graded<=.0031308,graded*12.92,1.055*np.maximum(graded,0)**(1/2.4)-.055)
new=old.copy();new[:,:,:3][valid]=np.uint8(np.rint(np.clip(srgb[valid],0,1)*255))
assert np.array_equal(new[~valid],old[~valid]) and np.array_equal(new[:,:,3],old[:,:,3])
out=ROOT/'build/bishop-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
Image.fromarray(new).save(out/'albedo.png')
record={'config':a.config,'config_sha256':sha(ROOT/a.config),'parameters':cfg,
 'capture_source_sha256':meta['source_sha256'],'position_field_sha256':sha(capture/'position.npy'),
 'valid_mask_sha256':sha(capture/'valid.npy'),'output_sha256':sha(out/'albedo.png'),
 'changed_texels':int(np.any(old!=new,axis=2).sum()),'alpha_and_non_surface_pixels_unchanged':True,
 'surface_gain_min':gain[valid].min(0).tolist(),'surface_gain_max':gain[valid].max(0).tolist(),
 'clipped_surface_channel_values':int((graded[valid]>=1).sum()),
 'status':'Unaccepted real-pigment trial; fresh BSDF renders and saved scope audit required.'}
(out/'pigment.json').write_text(json.dumps(record,indent=2)+'\n')
assert sha(source)==cfg['source_sha256'];print('HEIGHT_PIGMENT_GRADE_PREPARED',json.dumps(record),flush=True)

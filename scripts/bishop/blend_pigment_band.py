"""Restrict a physically rendered pigment candidate to a smooth height band.

Uses the unchanged evaluated surface positions, without editing source images.
Outside the declared band, original atlas bytes and all alpha remain exact.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--config',required=True)
a=p.parse_args(); config_path=ROOT/a.config; cfg=json.loads(config_path.read_text())
source=ROOT/cfg['source']; candidate=ROOT/cfg['candidate']; capture=ROOT/cfg['capture']
assert sha(source)==cfg['source_sha256'] and sha(candidate)==cfg['candidate_sha256']
meta=json.loads((capture/'manifest.json').read_text())
assert sha(ROOT/meta['source'])==meta['source_sha256']
encoded=np.load(capture/'position.npy'); valid=np.load(capture/'valid.npy')
z=(encoded[:,:,2]-meta['encode_offset'])/meta['encode_scale']*meta['encode_extent'][2]+meta['encode_min'][2]
lo,full_lo,full_hi,hi=cfg['heights']
assert 0<=lo<full_lo<=full_hi<hi<4.4
def smooth(t):
    t=np.clip(t,0,1);return t*t*(3-2*t)
weight=smooth((z-lo)/(full_lo-lo))*smooth((hi-z)/(hi-full_hi))*valid
old=np.array(Image.open(source).convert('RGBA')); trial=np.array(Image.open(candidate).convert('RGBA'))
assert old.shape==trial.shape and old.shape[:2]==weight.shape
def linear(rgb):
    rgb=rgb.astype(np.float64)/255
    return np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
mix=linear(old[:,:,:3])*(1-weight[:,:,None])+linear(trial[:,:,:3])*weight[:,:,None]
srgb=np.where(mix<=.0031308,mix*12.92,1.055*np.maximum(mix,0)**(1/2.4)-.055)
new=old.copy();active=weight>0
new[:,:,:3][active]=np.uint8(np.rint(np.clip(srgb[active],0,1)*255))
assert np.array_equal(new[~active],old[~active]) and np.array_equal(new[:,:,3],old[:,:,3])
out=ROOT/'build/bishop-mission'/cfg['variant']
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True);Image.fromarray(new).save(out/'albedo.png')
report=dict(config=a.config,config_sha256=sha(config_path),parameters=cfg,
    source_sha256=sha(source),candidate_sha256=sha(candidate),output_sha256=sha(out/'albedo.png'),
    capture_source_sha256=meta['source_sha256'],position_sha256=sha(capture/'position.npy'),
    protected_texels=int((~active).sum()),changed_texels=int(np.any(new!=old,axis=2).sum()),
    protected_and_alpha_pixels_exact=True,
    note='Smooth all-azimuth pigment blend, no geometry, lighting or relief edit. Candidate remains unaccepted until saved BSDF views and scope audits pass.')
(out/'pigment.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
print('BAND_PIGMENT_PREPARED',json.dumps(report),flush=True)

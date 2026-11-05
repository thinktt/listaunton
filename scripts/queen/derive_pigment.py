"""Estimate view-visible albedo, suppressing specular and poorly constrained pixels."""
from pathlib import Path
import argparse,json
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('directory');args=p.parse_args();out=ROOT/args.directory
s=np.load(out/'black-bsdf.npy');white=np.load(out/'white-bsdf.npy');old=np.load(out/'pigment.npy');target=np.load(out/'reference-linear.npy');srgb=np.load(out/'reference-srgb.npy')
diffuse=np.maximum(white[:,:,:3]-s[:,:,:3],.001)
inferred=np.maximum(target-s[:,:,:3],0)/diffuse
# Bound corrections; leave highlights and model-dominated reflections to the
# actual shader. This is not a photograph pasted over the beauty render.
inferred=np.clip(inferred,np.maximum(old[:,:,:3]*.3,.0001),np.minimum(old[:,:,:3]*3.5+.002,.8))
ratio=s[:,:,:3].max(2)/np.maximum(target.max(2),.001)
confidence=np.clip((.7-ratio)/.5,0,1)*np.clip((.28-srgb.min(2))/.16,0,1)
confidence*=np.clip((diffuse.mean(2)-.015)/.06,0,1)
confidence*=((old[:,:,3]>.995)&(srgb.max(2)>.05));confidence*=.9
rgba=np.dstack((inferred,confidence)).astype(np.float32);np.save(out/'inferred-pigment.npy',rgba)
mask=old[:,:,3]>.995
report={'response_source':json.loads((out/'manifest.json').read_text()),'method':'(reference-linear - black-BSDF response) / (white-BSDF response - black-BSDF response), bounded and confidence weighted','foreground_pixels':int(mask.sum()),'pixels_with_weight_above_half':int((confidence>.5).sum()),'mean_foreground_weight':float(confidence[mask].mean()),'highlight_exclusion_srgb_min_channel':[.12,.28],'correction_factor_limits':[.3,3.5],'caveat':'Inferred pigment under estimated geometry and illumination; residual shading remains possible. Hidden surfaces keep the existing continuous wood.'}
(out/'inference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

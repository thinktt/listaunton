"""Infer pigment from measured diffuse response after estimating source highlights."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image,ImageFilter
from image_math import blur
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('directory');args=p.parse_args();out=ROOT/args.directory
black=np.load(out/'black-bsdf.npy');white=np.load(out/'white-bsdf.npy');old=np.load(out/'pigment.npy');target=np.load(out/'reference-linear.npy')
d=np.array([1,.23,.08]);c=np.array([1,.58,.4]);coefficients=target@np.linalg.pinv(np.column_stack((d,c))).T
spec=np.maximum(coefficients[:,:,1],0);diffuse_target=np.maximum(target-spec[:,:,None]*c,0)
response=np.maximum(white[:,:,:3]-black[:,:,:3],.001)
pigment=diffuse_target/response
pigment=np.clip(pigment,np.maximum(old[:,:,:3]*.15,.0001),np.minimum(old[:,:,:3]*6+.005,.9))
fraction=spec/np.maximum(target[:,:,0],.001)
confidence=np.clip((.65-fraction)/.25,0,1)
confidence*=np.clip((response.mean(2)-.01)/.05,0,1)
interior=np.array(Image.fromarray(np.uint8(old[:,:,3]>.995)*255).filter(ImageFilter.MinFilter(15)))>127
confidence=blur(confidence,r=1,passes=2)*interior*(target.max(2)>.0001)*.98
np.save(out/'inferred-pigment.npy',np.dstack([pigment,confidence]).astype(np.float32))
report={'method':'Estimate a warm specular component from the unchanged reference, subtract it, and divide remaining color by measured white-minus-black BSDF response','diffuse_chromaticity_hypothesis':d.tolist(),'specular_chromaticity_hypothesis':c.tolist(),'relative_pigment_bounds':[.15,6],'absolute_pigment_max':.9,'maximum_projection_weight':.98,'bright_specular_fraction_confidence_transition':[.4,.65],'mean_interior_confidence':float(confidence[interior].mean()),'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'caveat':'Reference-derived inferred pigment. Unknown source shading and color processing make diffuse/specular separation approximate; residual shadows may remain. Source image is unchanged; hidden surfaces keep continuous prior pigment.'}
(out/'inference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

"""Fill uncertain glossy regions from nearby reliable pigment before projection."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageFilter
from image_math import blur
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'build/queen-mission/pigment-fit-039';out=ROOT/'build/queen-mission/pigment-filled-039';out.mkdir(parents=True,exist_ok=True)
black=np.load(source/'black-bsdf.npy');white=np.load(source/'white-bsdf.npy');old=np.load(source/'pigment.npy');target=np.load(source/'reference-linear.npy')
d=np.array([1,.23,.08]);c=np.array([1,.58,.4]);coefficients=target@np.linalg.pinv(np.column_stack((d,c))).T
spec=np.maximum(coefficients[:,:,1],0);fraction=spec/np.maximum(target[:,:,0],.001)
response=np.maximum(white[:,:,:3]-black[:,:,:3],.001)
raw=np.clip(target/response,np.maximum(old[:,:,:3]*.15,.0001),np.minimum(old[:,:,:3]*6+.005,.9))
mask=old[:,:,3]>.995
reliable=np.clip((.25-fraction)/.15,0,1)*np.clip((response.mean(2)-.01)/.05,0,1)*mask
numerator=blur(raw*reliable[:,:,None],r=10,passes=3);denominator=blur(reliable,r=10,passes=3)
filled=numerator/np.maximum(denominator[:,:,None],1e-7)
wide_num=blur(raw*reliable[:,:,None],r=25,passes=3);wide_den=blur(reliable,r=25,passes=3)
filled=np.where((denominator>.015)[:,:,None],filled,wide_num/np.maximum(wide_den[:,:,None],1e-7))
filled=np.where((wide_den>.001)[:,:,None],filled,old[:,:,:3])
blend=blur(reliable,r=3,passes=2)
pigment=raw*blend[:,:,None]+filled*(1-blend[:,:,None])
interior=np.array(Image.fromarray(np.uint8(mask)*255).filter(ImageFilter.MinFilter(11)),dtype=np.float32)/255
coverage=blur(interior,r=2,passes=2)*.96
np.save(out/'inferred-pigment.npy',np.dstack([pigment,coverage]).astype(np.float32));shutil.copyfile(source/'manifest.json',out/'manifest.json')
report={'method':'Use reference color divided by measured diffuse response only where estimated specular fraction is low; normalized local convolution fills uncertain highlights from nearby reliable pigment before uniform visible-surface projection','source_response_directory':source.relative_to(ROOT).as_posix(),'reliable_specular_fraction_transition':[.1,.25],'local_fill_radii':[10,25],'projection_weight':.96,'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'caveat':'Filled grain is smoothed inference in highlight regions; low-level residual shading can remain. No reference is modified and hidden surfaces retain continuous prior wood.'}
(out/'inference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

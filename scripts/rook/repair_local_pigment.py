"""Repair low-frequency pigment contamination locally; preserve fine atlas detail."""
from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'assets/rook/pigment.png';assert hashlib.sha256(source.read_bytes()).hexdigest()=='37de531d5e4bef1eb0bd370c1aa2c85171297032677552aac26d659c9352b9b6';im=Image.open(source).convert('RGB');a=np.asarray(im,dtype=np.float32)
low=np.asarray(im.filter(ImageFilter.GaussianBlur(8)),dtype=np.float32)
surround=np.asarray(im.filter(ImageFilter.GaussianBlur(38)),dtype=np.float32)
h,w=a.shape[:2];u=(np.arange(w)+.5)/w;v=1-(np.arange(h)+.5)/h;U,V=np.meshgrid(u,v)
mask=np.zeros((h,w),np.float32)
for center,spread in [((.5645,.4727),(.017,.010)),((.56,.430),(.045,.013)),((.5643,.369),(.028,.016))]:
 q=((U-center[0])/spread[0])**2+((V-center[1])/spread[1])**2
 patch=np.exp(-q*2);patch[q>4]=0;mask=np.maximum(mask,patch)
for num,strength in [(55,1),(56,1.6)]:
 out=ROOT/f'build/rook-mission/{num:03d}-local-pigment';out.mkdir(parents=True,exist_ok=True)
 result=np.clip(a+strength*mask[:,:,None]*(surround-low),0,255).round().astype(np.uint8)
 Image.fromarray(result).save(out/'pigment.png')
 params={'source_atlas_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'strength':strength,'blur_radii_px':[8,38],'method':'Local difference-of-Gaussian pigment correction; no UV resampling; original high-frequency detail retained before clipping. Not physical albedo recovery.','unmasked_pixels_exact':bool(np.array_equal(result[mask==0],a.astype(np.uint8)[mask==0]))}
 (out/'parameters.json').write_text(json.dumps(params,indent=2)+'\n')
 print(num,params)


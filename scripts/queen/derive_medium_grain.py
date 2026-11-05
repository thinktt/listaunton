"""Replace coarse invented pigment detail with bounded actual reference grain."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageFilter
from image_math import blur
ROOT=Path(__file__).resolve().parents[2];response=ROOT/'build/queen-mission/pigment-fit-039';out=ROOT/'build/queen-mission/medium-grain-039';out.mkdir(parents=True,exist_ok=True)
source=ROOT/'models/queen/queen-rebuilt.blend';old=np.load(response/'pigment.npy');ref=np.load(response/'reference-linear.npy')
mask=(old[:,:,3]>.995).astype(np.float32)
# Smooth away the old large winding pigment lines, preserving the broad field.
broad=blur(old[:,:,:3]*mask[:,:,None],r=12,passes=3)/np.maximum(blur(mask,r=12,passes=3)[:,:,None],1e-6)
lum=np.maximum(ref@np.array([.2126,.7152,.0722],dtype=np.float32),0);log=np.log(lum+.003)
refmask=(ref.max(2)>.001).astype(np.float32)
local=blur(log*refmask,r=7,passes=3)/np.maximum(blur(refmask,r=7,passes=3),1e-6)
ratio=np.exp(np.clip(log-local,np.log(.68),np.log(1.42))*.85)
dc=np.column_stack(([1,.23,.08],[1,.58,.4]));spec=np.maximum((ref@np.linalg.pinv(dc).T)[:,:,1],0)
fraction=spec/np.maximum(ref[:,:,0],.001)
grain_weight=blur(np.clip((.3-fraction)/.2,0,1),r=3,passes=2)
ratio=1+(ratio-1)*grain_weight
pigment=broad*ratio[:,:,None]
interior=np.array(Image.fromarray(np.uint8(mask)*255).filter(ImageFilter.MinFilter(11)),dtype=np.float32)/255
coverage=blur(interior,r=2,passes=2)*.96
np.save(out/'inferred-pigment.npy',np.dstack([pigment,coverage]).astype(np.float32))
manifest={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'borrowed_unlit_response':response.relative_to(ROOT).as_posix()+'/pigment.npy','borrowed_response_sha256':hashlib.sha256((response/'pigment.npy').read_bytes()).hexdigest(),'note':'The 039 pre-publication source and third accepted checkpoint have identical geometry and pigment; only saved scene bookkeeping/render settings differ.'}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
report={'method':'Retain a broad normalized pigment field; replace coarse invented color lines with bounded fine/medium log-luminance variation from the unchanged reference','old_color_blur_radius':12,'reference_log_blur_radius':7,'box_blur_passes':3,'grain_bounds_before_exponent':[.68,1.42],'grain_exponent':.85,'highlight_detail_weight_fraction_transition':[.1,.3],'projection_weight':.96,'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'caveat':'Low-frequency inferred color is preserved; some carving or shading edges may enter the bounded detail field. Highlight grain is suppressed, not painted into a reflective light map. Hidden surfaces retain prior continuous wood.'}
(out/'inference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

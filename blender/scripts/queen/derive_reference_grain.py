"""Transfer fine reference grain while retaining the accepted broad pigment field."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageFilter
from image_math import blur
ROOT=Path(__file__).resolve().parents[2];responses=ROOT/'build/queen-mission/pigment-fit-033';out=ROOT/'build/queen-mission/grain-transfer-026';out.mkdir(parents=True,exist_ok=True)
source=ROOT/'build/queen-mission/026-graded-atlas/queen.blend'
old=np.load(responses/'pigment.npy');reference=np.load(responses/'reference-linear.npy');srgb=np.load(responses/'reference-srgb.npy')
luma=np.maximum(reference@np.array([.2126,.7152,.0722],dtype=np.float32),0)
ratio=np.clip(((luma+.004)/(blur(luma)+.004))**.8,.45,1.8)
base=old[:,:,:3]*.25+blur(old[:,:,:3])*.75
pigment=base*ratio[:,:,None]
interior=np.array(Image.fromarray(np.uint8(old[:,:,3]>.995)*255).filter(ImageFilter.MinFilter(15)))>127
confidence=blur(np.clip((.28-srgb.min(2))/.16,0,1),r=4,passes=3)*interior*(srgb.max(2)>.05)*.85
np.save(out/'inferred-pigment.npy',np.dstack([pigment,confidence]).astype(np.float32))
manifest={'source':'build/queen-mission/026-graded-atlas/queen.blend','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'unlit_pigment_pass':'build/queen-mission/pigment-fit-033/pigment.npy','unlit_pigment_pass_sha256':hashlib.sha256((responses/'pigment.npy').read_bytes()).hexdigest(),'note':'The 033 scene uses the identical 026 pigment and geometry; its emission pass is independent of changed lights.'}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
report={'method':'Fine luminance grain from the unchanged reference divided by its local mean; accepted low-frequency pigment and hue retained','blur':'Three radius-3 box passes, approximately 3.46-pixel Gaussian sigma','grain_ratio_limits':[.45,1.8],'retained_old_detail_weight':.25,'source_highlights_feathered_out':True,'silhouette_interior_margin_pixels':7,'max_projection_weight':.85,'reference_sha256':hashlib.sha256((ROOT/'assets/queen/reference.png').read_bytes()).hexdigest(),'caveat':'Some fine carving/shading edges can enter a high-pass grain estimate; inspect geometry and other views independently.'}
(out/'inference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

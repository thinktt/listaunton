"""Derive bounded, fine surface height from the current pigment atlas."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
from image_math import blur
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'assets/queen/queen-pigment-albedo-v3.png';out=ROOT/'build/queen-mission/atlas-relief-v3';out.mkdir(parents=True,exist_ok=True)
a=np.asarray(Image.open(source).convert('RGB'),dtype=np.float32)/255
linear=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
lum=linear@np.array([.2126,.7152,.0722],dtype=np.float32)
log=np.log(lum+.001);detail=log-blur(log,r=5,passes=3)
height=np.clip(.5+.20*detail,.35,.65)
# The lathe atlas wraps in U. Make only the outermost samples agree.
edge=(height[:,0]+height[:,-1])/2;height[:,0]=height[:,-1]=edge
path=out/'height.png';Image.fromarray(np.uint16(np.round(height*65535))).save(path)
record={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'height_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'method':'Bounded log-luminance high pass of linear pigment, not rendered shading','blur_radius':5,'blur_passes':3,'gain':.2,'height_range':[.35,.65],'caveat':'Pigment-derived relief is an artistic inference. Grain color does not uniquely determine height.'}
(out/'derivation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

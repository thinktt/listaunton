"""Extract only local grain variation from a quiet area of the knight pedestal."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/queen"))
from image_math import blur

OUT = ROOT/"build/knight-mission/material-observations"
OUT.mkdir(parents=True,exist_ok=True)
reference = ROOT/"assets/knight/ref.png"
image = np.asarray(Image.open(reference).convert("RGBA"), dtype=np.float32) / 255
# Inside the carved base, away from the upper collar, foot seam and rim.
box = (350, 888, 604, 963)
x0,y0,x1,y1 = box
tile = image[y0:y1,x0:x1,:3]
assert np.quantile(image[y0:y1,x0:x1,3],.01) > .75
linear = np.where(tile<=.04045, tile/12.92, ((tile+.055)/1.055)**2.4)
log = np.log(.003+linear @ np.array([.2126,.7152,.0722], dtype=np.float32))
variation = np.clip(log-blur(log,10,3), -.65, .50)
# Reflecting a small measured patch removes seams at both repeat boundaries.
variation = np.concatenate((variation,variation[:,::-1]), axis=1)
variation = np.concatenate((variation,variation[::-1]), axis=0)
base = np.array([.11,.031,.0085],dtype=np.float32)
pigment = base*np.exp(variation[:,:,None]*1.2)
srgb = np.where(pigment<=.0031308, 12.92*pigment,1.055*pigment**(1/2.4)-.055)
Image.fromarray(np.rint(np.clip(srgb,0,1)*255).astype("uint8")).save(OUT/"continuous-grain.png")
np.save(OUT/"reference-display.npy",image)
(OUT/"tile.json").write_text(json.dumps({"reference_sha256":hashlib.sha256(reference.read_bytes()).hexdigest(),
    "source_box":box,"base_linear_pigment":base.tolist(),"log_detail_bounds":[-.65,.5],
    "method":"Retain bounded local luminance texture after removing broad illumination. Reflect across tile edges and apply to a world-volume wood grain field."},indent=2)+"\n")

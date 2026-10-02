"""Register the untouched Lichess queen to the selected high-res reference.

Fit only uniform scale and translation to the silhouettes, independently of
the reconstructed model. The browser displays the original PNG directly.
"""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
from PIL import Image
from overlay_qa import largest_component, fill_holes, bounds

ROOT=Path(__file__).resolve().parents[2]
HIGH=ROOT/'assets/queen/reference.png'
LOW=ROOT/'references/lichess-staunton-3d/Black-Queen.png'
def mask(path):
 image=Image.open(path).convert('RGBA')
 pixels=np.asarray(image)
 return image,fill_holes(largest_component((pixels[:,:,:3].max(axis=2)>12)&(pixels[:,:,3]>127)))
hi,hi_mask=mask(HIGH)
lo,lo_mask=mask(LOW)
hx0,hy0,hx1,hy1=bounds(hi_mask);lx0,ly0,lx1,ly1=bounds(lo_mask)
base=(hy1-hy0+1)/(ly1-ly0+1)
down=4
size=((hi.width+down-1)//down,(hi.height+down-1)//down)
target=np.asarray(Image.fromarray(hi_mask).resize(size,Image.Resampling.NEAREST))
bitmap=Image.fromarray(lo_mask.astype('uint8')*255)
def score(scale,x,y):
 image=bitmap.transform(size,Image.Transform.AFFINE,(down/scale,0,-x/scale,0,down/scale,-y/scale),Image.Resampling.NEAREST)
 transformed=np.asarray(image)>127
 return float((target&transformed).sum()/(target|transformed).sum())
best=(-1,None,None,None)
for scale in np.linspace(base*.94,base*1.06,25):
 x=(hx0+hx1)/2-scale*(lx0+lx1)/2
 y=(hy0+hy1)/2-scale*(ly0+ly1)/2
 for dx in range(-16,17,4):
  for dy in range(-16,17,4):
   result=(score(scale,x+dx,y+dy),scale,x+dx,y+dy)
   if result[0]>best[0]:best=result
_,initial_scale,initial_x,initial_y=best
for scale in np.linspace(initial_scale*.996,initial_scale*1.004,9):
 # Keep the center of the piece fixed when adjusting the scale.
 x=initial_x+(initial_scale-scale)*(lx0+lx1)/2
 y=initial_y+(initial_scale-scale)*(ly0+ly1)/2
 for dx in range(-3,4):
  for dy in range(-3,4):
   result=(score(scale,x+dx,y+dy),scale,x+dx,y+dy)
   if result[0]>best[0]:best=result
overlap,scale,x,y=best
record={'method':'Uniform scale and translation; no rotation, anisotropic stretch or warp',
 'fit_target':'Selected high-resolution reference silhouette; not the reconstructed model',
 'source':'references/lichess-staunton-3d/Black-Queen.png','target':'assets/queen/reference.png',
 'source_sha256':hashlib.sha256(LOW.read_bytes()).hexdigest(),'target_sha256':hashlib.sha256(HIGH.read_bytes()).hexdigest(),
 'source_size':[lo.width,lo.height],'canvas_size':[hi.width,hi.height],
 'scale':float(scale),'offset_x':float(x),'offset_y':float(y),
 'silhouette_iou_at_quarter_resolution':overlap,
 'mask':'max RGB >12 and alpha >127; largest component and filled holes',
 'display':'Browser enlarges the untouched PNG with smooth interpolation. No new detail is generated.'}
(ROOT/'assets/queen/original-reference-alignment.json').write_text(json.dumps(record,indent=2)+'\n')
review=ROOT/'review.html'
page=review.read_text(encoding="utf-8")
if 'id="original-reference-alignment"' in page:
 page=re.sub(r'(<script id="original-reference-alignment"[^>]*>).*?(</script>)',lambda m:m.group(1)+json.dumps(record,separators=(',',':'))+m.group(2),page,flags=re.S)
 review.write_text(page,encoding="utf-8")
print(json.dumps(record,indent=2))

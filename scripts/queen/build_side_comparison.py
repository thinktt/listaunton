"""Register the new side render uniformly to the imagined side guide.

The generated guide is kept unchanged. A single uniform scale and translation
align the model's base width and floor; no image warping or anisotropic scaling.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'assets/queen'
# Measured from the unmodified, opaque side-01.png (colored edge of the foot).
source={'file':'assets/queen/concepts/side-01.png','base_left':344,'base_right':876,'floor_y':1105}
target_width=source['base_right']-source['base_left'];target_center=(source['base_right']+source['base_left'])/2
model=Image.open(out/'queen-finished-profile.png').convert('RGBA')
mask=np.asarray(model)[:,:,3]>127;ys,xs=np.nonzero(mask)
floor=int(ys.max()+1);top=int(ys.min());cut=floor-(floor-top)*.25
rows=[]
for y in range(max(0,int(cut)),min(floor,mask.shape[0])):
 x=np.flatnonzero(mask[y])
 if len(x):rows.append((int(x[-1]-x[0]+1),int(x[0]),int(x[-1]),y))
width,left,right,row=max(rows);center=(left+right+1)/2
padding_top=160;canvas_height=1254+padding_top
scale=target_width/width;offset_x=target_center-scale*center;offset_y=source['floor_y']+padding_top-scale*floor
for name in ['queen-finished-profile.png','queen-wood-profile.png']:
 img=Image.open(out/name).convert('RGBA')
 registered=img.transform((1254,canvas_height),Image.Transform.AFFINE,(1/scale,0,-offset_x/scale,0,1/scale,-offset_y/scale),Image.Resampling.BICUBIC)
 registered.save(out/('side-aligned-neutral.png' if name.startswith('queen-finished') else 'side-aligned-wood.png'))
record={'method':'Single uniform scale and translation: align measured foot width, horizontal center and floor. Side guide itself unchanged.',
 'side_guide_is_interpretation':True,'guide':source,
 'model_base':{'width_px':width,'center_px':center,'floor_y_px':floor,'measured_row':row},
 'scale':scale,'offset_x':offset_x,'offset_y':offset_y,'guide_top_padding_px':padding_top,
 'canvas':[1254,canvas_height]}
(out/'side-registration.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))

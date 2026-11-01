"""Fit a uniform camera scale and translation to the actual rendered outline.

The target is the original Lichess sprite in its existing uniform registration.
The mesh, 54° elevation, and physical side proportions do not change.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from overlay_qa import largest_component,fill_holes
root=Path(__file__).resolve().parents[2];out=root/'assets/queen'
fit=json.loads((out/'scratch-fit.json').read_text())
reg=json.loads((out/'original-reference-alignment.json').read_text())
t,dx,dy=reg['scale'],reg['offset_x'],reg['offset_y']
im=Image.open(root/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/t,0,-dx/t,0,1/t,-dy/t),Image.Resampling.BILINEAR)
a=np.asarray(im);target=fill_holes(largest_component((a[:,:,3]>127)&(a[:,:,:3].max(2)>12)))
model=np.asarray(Image.open(out/'queen-matched.png').convert('RGBA'))[:,:,3]>127
def small(mask):return np.asarray(Image.fromarray((mask*255).astype('uint8')).resize((314,314),Image.Resampling.BOX))>127
target=small(target);model=small(model)
cx=fit['camera_cx']/4;floor=fit['camera_floor']/4
best=(-1,None)
before=float((target&model).sum()/(target|model).sum())
for factor in np.arange(.975,1.0201,.0025):
    # Forward transform is anchor + factor*(pixel-anchor).
    affine=(1/factor,0,cx-cx/factor,0,1/factor,floor-floor/factor)
    img=Image.fromarray((model*255).astype('uint8')).transform((314,314),Image.Transform.AFFINE,affine,Image.Resampling.BILINEAR)
    scaled=np.asarray(img)>127
    for shiftx in range(-3,4):
        for shifty in range(-3,4):
            candidate=np.roll(scaled,(shifty,shiftx),axis=(0,1))
            score=float((target&candidate).sum()/(target|candidate).sum())
            if score>best[0]:best=(score,(float(factor),shiftx*4,shifty*4))
factor,shiftx,shifty=best[1]
fit['camera_scale']*=factor;fit['camera_cx']+=shiftx;fit['camera_floor']+=shifty
fit['camera_refit']={'method':'Uniform image scale and x/y translation fitted to the actual rendered silhouette against the original black sprite at quarter resolution; no geometry or camera elevation changes.',
 'scale_factor':factor,'translation_highres_px':[shiftx,shifty],
 'quarter_resolution_iou_before':before,'quarter_resolution_iou_after':best[0]}
(out/'scratch-fit.json').write_text(json.dumps(fit,indent=2)+'\n')
print(json.dumps(fit['camera_refit'],indent=2))

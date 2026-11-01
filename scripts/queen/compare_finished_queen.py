"""Compare actual rendered silhouettes with both registered references."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from overlay_qa import largest_component, fill_holes

root=Path(__file__).resolve().parents[2];out=root/'assets/queen';size=(1254,1254)
reg=json.loads((out/'original-reference-alignment.json').read_text())
t,dx,dy=reg['scale'],reg['offset_x'],reg['offset_y']
original=Image.open(root/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform(size,Image.Transform.AFFINE,(1/t,0,-dx/t,0,1/t,-dy/t),Image.Resampling.BILINEAR)
selected=Image.open(out/'reference.png').convert('RGBA')
def refmask(im):
    a=np.asarray(im);return fill_holes(largest_component((a[:,:,3]>127)&(a[:,:,:3].max(2)>12)))
def modelmask(path):
    a=np.asarray(Image.open(path).convert('RGBA'));return fill_holes(largest_component(a[:,:,3]>127))
def iou(a,b):return float((a&b).sum()/(a|b).sum())
references={'original_black':refmask(original),'selected_highres':refmask(selected)}
models={'previous_revision':modelmask(out/'queen-previous.png'),
        'new_from_scratch':modelmask(out/'queen-matched.png')}
results={name:{target:iou(mask,reference) for target,reference in references.items()} for name,mask in models.items()}
report={'camera_assumption_degrees_above_board':54,'method':'Actual render alpha and reference max RGB >12, largest component with holes filled. Original sprite uniformly registered to selected image; no separate model alignment.',
        'silhouette_iou':results,
        'limitations':'Silhouette overlap does not measure internal contours, material, lighting or unseen geometry. The generated high-resolution source is an interpretation, not ground-truth geometry.'}
(out/'finish-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

"""Read the two approved black references at the gallery registration, without side effects."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent
ASSETS=D.parents[2]/'assets/knight'
def registered():
    selected=Image.open(ASSETS/'ref.png').convert('RGBA')
    data=json.loads((ASSETS/'original-alignment.json').read_text())
    s=data['scale']*300/selected.width
    original=Image.open(ASSETS/'original.png').convert('RGBA').transform(
        selected.size,Image.Transform.AFFINE,(s,0,data['x']*3,0,s,data['y']*3),Image.Resampling.BILINEAR)
    return {'original':original,'selected':selected}
def black(image):
    return Image.alpha_composite(Image.new('RGBA',image.size,(0,0,0,255)),image.convert('RGBA')).convert('RGB')
def silhouette(image,reference=False):
    rgba=np.asarray(image.convert('RGBA'));m=rgba[:,:,3]>127
    if reference:m&=rgba[:,:,:3].max(2)>12
    joined=Image.fromarray(m.astype(np.uint8)*255).copy()
    ImageDraw.floodfill(joined,(449,635),129,thresh=0)
    filled=Image.fromarray(np.pad(np.uint8(np.asarray(joined)==129)*255,1)).copy()
    ImageDraw.floodfill(filled,(0,0),128,thresh=0)
    return np.asarray(filled)[1:-1,1:-1]!=128
def iou(a,b):
    return float((a&b).sum()/(a|b).sum())

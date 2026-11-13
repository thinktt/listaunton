"""Overlay measured cut-interior boundaries on unchanged registered references."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--capture',default='build/bishop-mission/144-surface-audit');a=p.parse_args()
out=ROOT/a.capture;mask=np.load(out/'surface-labels.npy')==2
edge=mask&~(np.roll(mask,1,0)&np.roll(mask,-1,0)&np.roll(mask,1,1)&np.roll(mask,-1,1))
def original(name,alignment):
    al=json.loads((ROOT/'assets/bishop'/alignment).read_text());s=al['scale']*300/1254
    return Image.open(ROOT/'assets/bishop'/name).convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,
        (s,0,al['x']*3,0,s,al['y']*3),Image.Resampling.BILINEAR)
items=[('Original white',original('original.png','original-alignment.json')),('Original black',original('black-original.png','black-alignment.json')),
    ('Selected white 3',Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA')),('Current neutral',Image.open(ROOT/'assets/bishop/render-clay.png').convert('RGBA'))]
box=(450,210,595,460);scale=2;w=(box[2]-box[0])*scale;h=(box[3]-box[1])*scale
canvas=Image.new('RGB',(4*w,2*h+60),'#13171b');draw=ImageDraw.Draw(canvas)
for i,(name,im) in enumerate(items):
    raw=np.array(im);over=raw.copy();over[edge]=[30,235,255,255]
    for row,value in enumerate([raw,over]):
        patch=Image.fromarray(value).crop(box).resize((w,h),Image.Resampling.NEAREST)
        y=row*(h+30);canvas.paste(patch,(i*w,y+30),patch)
        draw.text((i*w+8,y+10),name+(' + actual cut' if row else ''),fill='white')
canvas.save(out/'slit-boundary-comparison.png')
print(out/'slit-boundary-comparison.png')

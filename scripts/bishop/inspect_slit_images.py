"""Unaltered diagnostic crops at fixed registration; never rewrite references."""
from pathlib import Path
import argparse, json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--trial');p.add_argument('--out',required=True);p.add_argument('--checkpoint',default='005');a=p.parse_args()
def original(name,alignment):
    v=json.loads((ROOT/'assets/bishop'/alignment).read_text());scale=v['scale']*300/1254
    return Image.open(ROOT/'assets/bishop'/name).convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(scale,0,v['x']*3,0,scale,v['y']*3),Image.Resampling.BILINEAR)
items=[('Original white',original('original.png','original-alignment.json')),
       ('Original black',original('black-original.png','black-alignment.json')),
       ('Selected white 3',Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA')),
       ('Accepted '+a.checkpoint,Image.open(ROOT/f'history/bishop-mission-{a.checkpoint}/render.png').convert('RGBA')),
       ('Neutral '+a.checkpoint,Image.open(ROOT/f'history/bishop-mission-{a.checkpoint}/render-clay.png').convert('RGBA'))]
if a.trial:items.append(('Trial',Image.open(ROOT/a.trial).convert('RGBA')))
box=(460,335,590,455);size=(520,480)
canvas=Image.new('RGB',(1560,1040),'#12161b');d=ImageDraw.Draw(canvas)
for i,(label,im) in enumerate(items):
    x=(i%3)*520;y=(i//3)*520;d.text((x+12,y+12),label,fill='white')
    crop=im.crop(box).resize(size,Image.Resampling.NEAREST)
    canvas.paste(crop,(x,y+40),crop)
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);canvas.save(out)

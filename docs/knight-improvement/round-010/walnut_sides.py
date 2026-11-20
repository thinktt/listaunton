"""Arrange the identically lit side photographs for direct comparison."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageOps
out=Path(sys.argv[1]);keys=sys.argv[2:]
w,h=290,286
canvas=Image.new('RGB',(w*len(keys),2*h+65),'#272a29');d=ImageDraw.Draw(canvas)
for i,k in enumerate(keys):
    for row,v in enumerate(['near','far']):
        im=Image.open(out/f'wood-{k}'/(v+'.png')).convert('RGBA')
        if v=='far':im=ImageOps.mirror(im)
        bg=Image.new('RGBA',im.size,'#25292a');bg.alpha_composite(im)
        ref=bg.convert('RGB').crop((129,82,525,433))
        ref.thumbnail((w-6,h-28),Image.Resampling.LANCZOS)
        canvas.paste(ref,(w*i+(w-ref.width)//2,h*row+25))
        d.text((w*i+8,h*row+3),f'{k} · {v} flank',fill='#ece8e1')
d.text((8,2*h+12),'Same walnut studio on both sides. Far view mirrored for comparison.',fill='#dedbd3')
canvas.save(out/'paired-walnut.png')

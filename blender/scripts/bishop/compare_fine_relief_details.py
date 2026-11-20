"""Present fixed-coordinate detail crops from the two fine-relief trials."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'build/bishop-mission/114-115-detail-comparison.png'
sources=[('Selected white 3','assets/bishop/reference.png'),
         ('Accepted 013','assets/bishop/render.png'),
         ('114: fine relief gain 2','build/bishop-mission/114-fine-relief/wood.png'),
         ('115: fine relief gain 4','build/bishop-mission/115-fine-relief-stronger/wood.png')]
boxes=[('Head grain',(500,295,590,400)),('Collar finish',(425,520,575,605)),
       ('Socket lip',(430,760,565,835)),('Base glint',(545,925,655,1010))]
cw,ch=420,450;canvas=Image.new('RGB',(cw*4,ch*4),'#171b21');d=ImageDraw.Draw(canvas)
for j,(feature,box) in enumerate(boxes):
    for i,(label,path) in enumerate(sources):
        im=Image.open(ROOT/path).convert('RGBA').crop(box)
        im.thumbnail((400,400),Image.Resampling.LANCZOS) if max(im.size)>400 else None
        scale=min(400/im.width,400/im.height)
        im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
        x=i*cw+(cw-im.width)//2;y=j*ch+45+(400-im.height)//2
        canvas.paste(im,(x,y),im)
        d.text((i*cw+10,j*ch+10),feature+' / '+label,fill='white')
canvas.save(out)
print(out)

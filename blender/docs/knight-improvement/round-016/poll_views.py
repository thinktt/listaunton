"""Compare the actual poll head-on, from behind and from the elevated reference."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
root=Path(sys.argv[1]).resolve()
n=int(sys.argv[2]);keys=sys.argv[3:]
build=root/'build/knight-mission';directory=build/f'round-{n:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import black,registered
ref=registered()
cell_w,cell_h=270,194
canvas=Image.new('RGB',(3*cell_w,cell_h*(len(keys)+1)+12),'#262827');d=ImageDraw.Draw(canvas)
font=ImageFont.load_default(size=14)
def open_image(path):
    with Image.open(path) as inp:return inp.convert('RGBA')
def place(im,label,row,col):
    im.thumbnail((cell_w-6,cell_h-26),Image.Resampling.LANCZOS)
    x,y=col*cell_w,row*cell_h
    d.text((x+7,y+3),label,fill='#eee9df',font=font)
    canvas.paste(im,(x+(cell_w-im.width)//2,y+23))
for col,(label,name) in enumerate([('Original black','original'),('Black candidate 2','selected'),('Original white, mirrored','white_mirrored')]):
    place(black(ref[name]).crop((200,275,535,480)),label+' · 54°',0,col)
for row,k in enumerate(keys,1):
    img=open_image(root/'assets/knight/render.png' if k=='parent' else build/f'improvement-{n:03}-{k}/wood.png')
    for col,v in enumerate(['54°','front-poll','back-poll']):
        if col:
            im=open_image(directory/f'clay-{k}'/(v+'.png'))
            bg=Image.new('RGBA',im.size,'#282b2b');bg.alpha_composite(im)
            im=bg.convert('RGB').crop((87,10,425,267))
        else:
            im=black(img).crop((200,275,535,480))
        place(im,k+' · '+{'front-poll':'front','back-poll':'back'}.get(v,v),row,col)
canvas.save(directory/'poll-views.png')

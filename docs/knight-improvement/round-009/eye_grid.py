"""Show the source eye and rendered eye on the shared fixed-camera pixel grid."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
r=Path(sys.argv[1]).resolve();dest=Path(sys.argv[2])
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import black,registered
refs=registered()
ims={'Black 2':refs['selected'],'Released knight':Image.open(r/'assets/knight/render.png')}
if len(sys.argv)>3:ims[sys.argv[3]]=Image.open(r/f'build/knight-mission/{sys.argv[3]}/wood.png')
box=(454,449,565,519);s=4
w=(box[2]-box[0])*s;h=(box[3]-box[1])*s
canvas=Image.new('RGB',((w+52)*len(ims),h+59),'#252629');d=ImageDraw.Draw(canvas)
font=ImageFont.load_default(size=11)
for i,(k,im) in enumerate(ims.items()):
    x=i*(w+52)+31;y=50
    canvas.paste(black(im.convert('RGBA')).crop(box).resize((w,h),Image.Resampling.LANCZOS),(x,y))
    d.text((x,3),k,font=font,fill='white')
    for pos in range(460,565,10):
        dx=x+(pos+.5-box[0])*s
        d.text((dx-10,27),str(pos),font=font,fill='white')
        d.line((dx,y-4,dx,y+2),fill='white')
    for pos in range(450,519,10):
        dy=y+(pos+.5-box[1])*s
        d.text((x-26,dy-4),str(pos),font=font,fill='white')
        d.line((x-3,dy,x+2,dy),fill='white')
canvas.save(dest/'eye-grid.png')

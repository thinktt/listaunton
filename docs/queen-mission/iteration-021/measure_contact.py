"""Inspect the reference contact crescent without modifying source pixels."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
HERE=Path(__file__).resolve().parent
ROOT=next((p for p in HERE.parents if (p/'assets/queen').is_dir()),HERE.parent/'queen-profile-019')
ref=Image.open(ROOT/'assets/queen/reference.png').convert('RGB')
a=np.asarray(ref.filter(ImageFilter.GaussianBlur(1)),dtype=float)/255
points=[]
for left,right,top,bottom in [(427,440,250,273),(440,454,268,283),(454,471,271,287),(471,489,272,287),(496,514,263,281),(514,529,250,272)]:
    score=a[top:bottom,left:right].min(2)
    yy,xx=np.unravel_index(score.argmax(),score.shape)
    points.append({'window':[left,top,right,bottom],'pixel':[int(xx+left),int(yy+top)],'min_rgb':float(score.max())})
font_path=next(p for p in ['C:/Windows/Fonts/segoeui.ttf','/mnt/c/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if Path(p).exists())
out=ref.crop((410,230,550,297)).resize((840,402),Image.Resampling.NEAREST);d=ImageDraw.Draw(out);font=ImageFont.truetype(font_path,18)
for point in points:
    x,y=point['pixel'];xx=(x-410)*6;yy=(y-230)*6
    d.ellipse((xx-9,yy-9,xx+9,yy+9),outline='cyan',width=2);d.text((xx-35,yy+12),str((x,y)),font=font,fill='cyan')
out.save(HERE/'contact-targets.png')
(HERE/'contact-targets.json').write_text(json.dumps(points,indent=2)+'\n',encoding='utf-8')
print(json.dumps(points,indent=2))

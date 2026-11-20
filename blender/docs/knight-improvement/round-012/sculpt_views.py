"""Compose a same-scale comparison of the carving in the registered side and elevated views."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('output',type=Path)
p.add_argument('entries',nargs='+',help='label:fixed walnut file,clay side file (relative to root)')
a=p.parse_args()
def image(file):
    with Image.open(a.root/file) as opened:
        mat=opened.convert('RGBA')
    b=Image.new('RGBA',mat.size,'#232626')
    b.alpha_composite(mat)
    return b.convert('RGB')
def crop(im,coords,size):
    # Cameras and uncropped film gates are shared across all columns.
    q=im.width/1254
    bounds=tuple(round(v*q) for v in coords)
    return im.crop(bounds).resize(size,Image.Resampling.LANCZOS)
try:
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
except OSError:
    font=ImageFont.load_default()
cols=[entry.split(':',1) for entry in a.entries]
w=344
sheet=Image.new('RGB',(w*len(cols),739),'#232626');d=ImageDraw.Draw(sheet)
for i,(label,files) in enumerate(cols):
    fixed,clay=[image(file) for file in files.split(',')]
    x=i*w
    d.text((x+10,4),label,font=font,fill='#eee9e0')
    sheet.paste(crop(clay,(274,130,944,830),(335,350)),(x+4,31))
    d.text((x+10,384),'Walnut at 54°',font=font,fill='#eee9e0')
    sheet.paste(crop(fixed,(178,269,780,568),(336,167)),(x+4,411))
    d.text((x+10,582),'Eye detail',font=font,fill='#eee9e0')
    sheet.paste(crop(fixed,(405,419,596,492+20),(268,130)),(x+38,608))
a.output.parent.mkdir(exist_ok=True,parents=True)
sheet.save(a.output)

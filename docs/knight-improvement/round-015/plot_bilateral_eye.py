"""Draw opposite sides in the same eye-centered coordinates at a shared scale."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(sys.argv[1])
labels=sys.argv[2:]
scale=2
w,h=145*scale,65*scale
canvas=Image.new('RGB',(len(labels)*(w+10)+10,3*h+120),'#232626')
draw=ImageDraw.Draw(canvas)
try:font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
except OSError:font=ImageFont.load_default()
def img(array):return Image.fromarray(np.uint8(np.clip(array,0,255)))
for col,name in enumerate(labels):
    data=np.load(root/f'eyes-{name}.npz')
    x=col*(w+10)+10
    for row,key in enumerate(['near','far']):
        depth=data[key];finite=np.isfinite(depth);safe=np.where(finite,depth,0)
        dv,du=np.gradient(safe,-.005,.005)
        m=np.sqrt(dv**2+du**2+1)
        grey=52+178*np.clip((.23*du-.66*dv+.71)/m,0,1)
        grey[~finite]=33
        y=34+(h+28)*row
        draw.text((x,y-25),f'{name} · {key} eye',fill='#eee8de',font=font)
        canvas.paste(img(grey).convert('RGB').resize((w,h),Image.Resampling.BICUBIC),(x,y))
    a,b=data['near_insert'],data['far_insert']
    patch=np.zeros((*a.shape,3),np.uint8)+51
    patch[a&b]=[227,219,195];patch[a&~b]=[255,153,78];patch[b&~a]=[42,182,207]
    y=34+(h+28)*2
    draw.text((x,y-25),'Eye visible through lids',fill='#eee8de',font=font)
    canvas.paste(img(patch).resize((w,h),Image.Resampling.NEAREST),(x,y))
draw.text((10,canvas.height-24),'Cream: both sides    Orange: near only    Blue: far only',fill='#eee8de',font=font)
canvas.save(root/'bilateral-eyes.png')

"""Trace the reference fold from the brow onto the bridge of the nose."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
r=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);codes=sys.argv[3:]
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import registered,black
b=r/'build/knight-mission';j=b/f'round-{n:03}-judge'
sources=registered()
photos={'Original black':sources['original'],'Black 2':sources['selected'],'Parent':Image.open(r/'assets/knight/render.png')}
for k in codes:photos[k]=Image.open(b/f'improvement-{n:03}-{k}/wood.png')
anchor=np.array([(459,467),(474,465),(488,464),(497,464),(506,466),(516,468),(526,471),(535,475),(544,481),(553,487),(562,492),(572,497),(580,500)])
x=np.arange(anchor[0,0],anchor[-1,0]+1)
y=np.rint(np.interp(x,anchor[:,0],anchor[:,1])).astype(int)
box=(451,447,585,521);w,h=268,148;font=ImageFont.load_default(size=13)
panels=Image.new('RGB',(w*len(photos),h*2+50),'#242825');draw=ImageDraw.Draw(panels)
measured={}
for i,(name,img) in enumerate(photos.items()):
    im=black(img.convert('RGBA'));t=im.crop(box).resize((w,h),Image.Resampling.LANCZOS)
    l=i*w;draw.text((l+4,4),name,font=font,fill='#eeeee5');panels.paste(t,(l,23));panels.paste(t,(l,h+29))
    curve=[(l+(xx+.5-box[0])*2,h+29+(yy+.5-box[1])*2) for xx,yy in zip(x,y)]
    draw.line(curve,fill='#88c3b0',width=1)
    a=np.asarray(im.filter(ImageFilter.GaussianBlur(1.4)),float)@[.2126,.7152,.0722]
    offsets=np.arange(-12,13)
    bands=a[y[None,:]+offsets[:,None],x[None,:]]
    measured[name]={}
    for name2,lo,hi in [('rear',467,492),('mid',493,521),('nose corner',530,547),('beyond eye',550,576)]:
        mask=(x>=lo)&(x<=hi);profile=np.median(bands[:,mask],axis=1)
        measured[name][name2]={'trough_offset_px':int(offsets[profile.argmin()]),
                                'luma_at_fold':round(float(profile[12]),2),
                                'upper_minus_fold':round(float(np.mean(profile[4:8])-profile[12]),2),
                                'lower_minus_fold':round(float(np.mean(profile[17:21])-profile[12]),2)}
draw.text((6,2*h+33),'Green follows the visible shadow under the brow in black candidate 2. Upper row shows the unmarked photos.',font=font,fill='#deded4')
panels.save(j/'brow-to-nose.png')
(j/'brow-to-nose.json').write_text(json.dumps({'method':'Hand-registered trace of the dark upper lid and its continuation toward the nose in black candidate 2. Brightness is measured along local vertical profiles. A fold in the sculpture and a cast shadow can differ in position. The original provides lower-resolution corroboration.','anchor_points':anchor.tolist(),'results':measured},indent=2)+'\n')
print(measured)

"""Locate the dominant reflection inside the reference eye, away from the lower cheek."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
r=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);names=sys.argv[3:]
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import registered,black
b=r/'build/knight-mission';out=b/f'round-{n:03}-judge'
refs=registered();pics={'Original black':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(r/'assets/knight/render.png')}
for k in names:pics[k]=Image.open(b/f'improvement-{n:03}-{k}/wood.png')
# A common, conservatively inset window. Coordinates follow the visible oblique eye surface.
polygon=[(478,469),(490,465),(504,466),(514,469),(525,474),(537,482),(541,487),
         (535,490),(522,490),(508,487),(497,484),(486,479),(477,474)]
xmin,ymin,xmax,ymax=(463,454,551,497);box=(xmin,ymin,xmax,ymax)
mask=Image.new('L',(xmax-xmin,ymax-ymin));ImageDraw.Draw(mask).polygon([(x-xmin,y-ymin) for x,y in polygon],fill=255)
m=np.asarray(mask)>0;yy,xx=np.indices(m.shape);xx+=xmin;yy+=ymin
f=ImageFont.load_default(size=12);w,h=192,95
sheet=Image.new('RGB',(w*len(pics),2*h+70),'#232924');d=ImageDraw.Draw(sheet);data={}
for i,(label,image) in enumerate(pics.items()):
    pic=black(image.convert('RGBA'));im=pic.crop(box)
    light=np.asarray(pic.filter(ImageFilter.GaussianBlur(1.25)).crop(box),float)@[.2126,.7152,.0722]
    base=np.percentile(light[m],65);high=np.maximum(light-base,0)*m
    weights=high/max(float(high.sum()),.0001)
    cx,cy=(float((values*weights).sum()) for values in (xx,yy))
    ypeak,xpeak=np.unravel_index(high.argmax(),m.shape)
    data[label]={'center_of_bright_contrast_x_y':[round(cx,2),round(cy,2)],'brightest_x_y':[xpeak.item()+xmin,ypeak.item()+ymin],
                 'local_baseline':round(float(base),2),'strongest_luma':round(float(light[m].max()),2),'bright_weight_noseward_of_x517_percent':round(float(weights[xx>=517].sum()*100),2)}
    ox=i*w;d.text((ox+4,5),label,fill='#eef0e6',font=f)
    tile=im.resize((w-2,h),Image.Resampling.LANCZOS);sheet.paste(tile,(ox,24));sheet.paste(tile,(ox,h+32))
    def pos(x,y):return (ox+(x+.5-xmin)*(w-2)/(xmax-xmin),h+32+(y+.5-ymin)*h/(ymax-ymin))
    p=[pos(x,y) for x,y in polygon];d.line(p+[p[0]],fill='#77a99a',width=1)
    px,py=pos(cx,cy);d.line((px-4,py,px+4,py),fill='#f4c680',width=2);d.line((px,py-4,px,py+4),fill='#f4c680',width=2)
d.text((5,2*h+44),'Gold marks the center of the brighter reflection inside the shared green window.',font=f,fill='#e7eadc')
sheet.save(out/'inner-eye-light.png')
(out/'inner-eye-light.json').write_text(json.dumps({'method':'1.25 px blur in sRGB with Rec.709 luminance. Keep positive contrast above the 65th percentile within the identical source-defined polygon. Measure its brightness-weighted centroid and distribution. The original offers coarse guidance at this magnification.','polygon':polygon,'results':data},indent=2)+'\n')
print(data)

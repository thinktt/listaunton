"""Plot vertical sections through the central eye and lower lid in reference pixels."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter,ImageFont
root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);codes=sys.argv[3:]
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import black,registered
build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
refs=registered()
sources={'Original black':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(root/'assets/knight/render.png')}
for code in codes:sources[code]=Image.open(build/f'improvement-{n:03}-{code}/wood.png')
windows=[(484,492),(496,504),(508,516),(521,529)]
rgb={'Original black':'#989e9d','Black 2':'#f6c777','Parent':'#e593a6','A':'#6fbadf','B':'#8ad1a4'}
paths={}
for name,im in sources.items():
    a=np.asarray(black(im.convert('RGBA')).filter(ImageFilter.GaussianBlur(1.2)),float)@[.2126,.7152,.0722]
    paths[name]=[np.median(a[454:511,x0:x1+1],axis=1) for x0,x1 in windows]
font=ImageFont.load_default(size=14)
sheet=Image.new('RGB',(960,570),'#232625');draw=ImageDraw.Draw(sheet)
draw.text((19,8),'Light through the eye and lower lid at the fixed 54° camera',font=font,fill='white')
for i,k in enumerate(sources):
    start=19+i*153;draw.line((start,46,start+18,46),fill=rgb[k],width=3);draw.text((start+25,38),k,font=font,fill='white')
for i,(x0,x1) in enumerate(windows):
    x=48+(i%2)*476;y=87+(i//2)*244;w=402;h=167
    draw.text((x,y-18),f'x = {x0} to {x1} px',font=font,fill='white')
    for yy in (0,50,100,150,200,250):
        yp=y+h-yy*h/255
        draw.line((x,yp,x+w,yp),fill='#454a48')
        draw.text((x-30,yp-7),str(yy),font=font,fill='#c7c8c5')
    for ypix in (460,470,480,490,500,510):
        xp=x+(ypix-454)*w/56
        draw.line((xp,y,xp,y+h),fill='#414643')
        draw.text((xp-10,y+h+3),str(ypix),font=font,fill='#d7d9d6')
    for name,traces in paths.items():
        line=traces[i];points=[(x+j*w/56,y+h-float(v)*h/255) for j,v in enumerate(line)]
        draw.line(points,fill=rgb[name],width=2)
draw.text((21,545),'Horizontal position tracks image y. Vertical position gives sRGB luminance (0 to 255). Each line uses the median over nine columns.',font=font,fill='white')
sheet.save(out/'eye-traces.png')
encoded={name:[np.round(curve,2).tolist() for curve in traces] for name,traces in paths.items()}
(out/'eye-traces.json').write_text(json.dumps({'x_ranges':windows,'y_first':454,'y_last':510,'blur_radius':1.2,'luminance':encoded},indent=2)+'\n')

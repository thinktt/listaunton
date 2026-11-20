"""Locate the secondary dark marking on the mane using the model's unlit pigment."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
r=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);b=r/'build/knight-mission';j=b/f'round-{n:03}-judge'
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import black,registered,silhouette
ref=registered();edge=silhouette(ref['selected'],True)
trace=json.loads((b/'round-011-judge/mane-hollow.json').read_bytes())['Black 2']['samples']
ys,xx=np.array([p[:2] for p in trace]).T
rows=np.arange(478,587,2)
outer=np.array([np.flatnonzero(edge[y])[0] for y in rows]);inner=np.interp(rows,ys,xx)
photos={'Black 2':ref['selected'],'Saved walnut':Image.open(r/'assets/knight/render.png'),'Saved pigment':Image.open(j/'mane-passes-parent/pigment.png'),'Earlier pigment':Image.open(j/'mane-pigment-before/pigment.png'),'Neutral polish':Image.open(j/'mane-passes-parent/polish.png')}
def Y(im,sigma):return np.asarray(im.filter(ImageFilter.GaussianBlur(sigma)),float)@[.2126,.7152,.0722]
imgs={k:black(v.convert('RGBA')) for k,v in photos.items()}
base=imgs['Saved pigment']
small=Y(base,2.);broad=Y(base,9.)
detail=(small-broad)/np.maximum(broad,12)
# Pick a continuous path through the negative residual, inside the broad face.
cost=np.full((len(rows),edge.shape[1]),1e5);back=np.zeros_like(cost,dtype=int)
for i,row in enumerate(rows):
    width=inner[i]-outer[i]
    candidates=np.arange(round(outer[i]+.24*width),round(outer[i]+.72*width)+1)
    if i==0:cost[i,candidates]=detail[row,candidates];continue
    steps=np.arange(-3,4);near=candidates[:,None]+steps[None,:]
    penalty=cost[i-1,near]+.020*abs(steps)[None,:]
    choice=np.argmin(penalty,axis=1)
    cost[i,candidates]=detail[row,candidates]+penalty[np.arange(len(candidates)),choice]
    back[i,candidates]=near[np.arange(len(candidates)),choice]
line=[int(cost[-1].argmin())]
for i in range(len(rows)-1,0,-1):line.append(int(back[i,line[-1]]))
x=np.array(line[::-1]);w,h=180,220;crop=(175,448,311,614)
sheet=Image.new('RGB',(w*len(imgs),h*2+66),'#252a26');d=ImageDraw.Draw(sheet);f=ImageFont.load_default(size=13)
result={}
for i,(k,im) in enumerate(imgs.items()):
    a=Y(im,2)
    dark=a[rows,x];left=a[rows,x-8];right=a[rows,x+8]
    local=(left+right)/2
    result[k]={'center_luminance_median':round(float(np.median(dark)),2),'mean_of_shoulders_minus_center_median':round(float(np.median(local-dark)),2),'relative_recess_median':round(float(np.median((local-dark)/np.maximum(local,12))),3)}
    l=i*w;d.text((l+4,4),k,font=f,fill='#eef0e7')
    im=im.crop(crop).resize((w-2,h),Image.Resampling.LANCZOS)
    sheet.paste(im,(l,25));sheet.paste(im,(l,h+33))
    pts=[(l+(v+.5-crop[0])*(w-2)/(crop[2]-crop[0]),h+33+(y+.5-crop[1])*h/(crop[3]-crop[1])) for y,v in zip(rows,x)]
    d.line(pts,fill='#84cabb',width=1)
d.text((6,2*h+43),'Green follows the secondary marking in the unlit atlas. The native carved hollow lies to its right.',font=f,fill='#e7e8dc')
sheet.save(j/'mane-pigment-origin.png')
(j/'mane-pigment-origin.json').write_text(json.dumps({'method':'Learn the strongest continuous dark residual on the central mane face from the saved unlit pigment. Compare that exact path with the earlier atlas on identical geometry and UVs, fitted reference, final render and neutral polish, using 2px Gaussian luminance. Shoulder samples are eight pixels either side. Units are displayed sRGB luminance, or a fraction for relative recess.','path_y_x':np.stack((rows,x),axis=1).tolist(),'results':result},indent=2)+'\n')
print(result)

"""Compact fixed- and side-view evidence for the chosen chest and eyelid."""
from pathlib import Path
import json
import sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'scripts/knight'))
from audit_mission import black,registered
refs=registered()
names=['Original','Black 2','Parent 6A','Candidate 7B']
ims=[refs['original'],refs['selected'],Image.open(OUT/'parent-wood.png'),Image.open(OUT/'wood.png')]
side=[Image.open(OUT/n) for n in ['parent-side.png','wood-side.png']]
canvas=Image.new('RGB',(1016,785),'#252727')
d=ImageDraw.Draw(canvas)
f=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
objects=[(269,500,730,767),(449,443,557,516)]
for i,(label,im) in enumerate(zip(names,ims)):
    d.text((5+i*254,5),label,font=f,fill='white')
    rgb=black(im.convert('RGBA'))
    for row,(box,hh,top) in enumerate(zip(objects,(155,171),(32,200))):
        patch=rgb.crop(box)
        patch.thumbnail((248,hh),Image.Resampling.LANCZOS) if row==0 else None
        if row==1:patch=patch.resize((248,168),Image.Resampling.LANCZOS)
        canvas.paste(patch,(i*254,top))
    cut=rgb.crop((493,434,770,694)).resize((248,233),Image.Resampling.LANCZOS)
    canvas.paste(cut,(i*254,383))
for i,im in enumerate(side):
    cut=black(im.convert('RGBA')).crop((379,220,871,813))
    cut.thumbnail((153,159),Image.Resampling.LANCZOS)
    canvas.paste(cut,(i*425+110,623))
    cut=black(im.convert('RGBA')).crop((590,283,735,371)).resize((199,121),Image.Resampling.LANCZOS)
    canvas.paste(cut,(i*425+269,645))
    d.text((269+425*i,620),['Parent side','Candidate side'][i],font=f,fill='white')
canvas.save(OUT/'selected-details.png')

xx=np.arange(476,531,1)
yy=np.rint(np.interp(xx,[476,488,504,518,530],[488,495,499,500,499])).astype(int)
areas={}
paths=json.loads((OUT.parent/'chest-carving-study/paths-fit.json').read_text())['curves']
ys,xs=np.indices((1254,1254))
def band(name):
    co=np.array([v['pixel'] for v in paths[name]])
    return np.interp(ys,co[:,1],co[:,0])
crest=band('crest')
shoulder=band('shoulder')
light=lambda im:np.asarray(black(im.convert('RGBA')).filter(ImageFilter.GaussianBlur(2.4)))@np.array([.2126,.7152,.0722])
target=light(ims[1])
for name,im in zip(names,ims):
    v=light(im)
    shoulder_mask=(ys>=580)&(ys<=728)&(abs(xs-shoulder)<=3)
    crest_mask=(ys>=580)&(ys<=728)&(abs(xs-crest)<=3)
    end=(ys>=675)&(ys<=739)&(abs(xs-crest-48)<15)
    eye=(xs>=470)&(xs<=534)&(ys>=469)&(ys<502)
    areas[name]={'chest_shoulder_luma':round(float(v[shoulder_mask].mean()),2),
            'chest_crest_luma':round(float(v[crest_mask].mean()),2),
            'terminus_luma_p90':round(float(np.percentile(v[end],90)),2),
            'terminus_luma_mae_black2':round(float(abs(v-target)[end].mean()),2),
            'eye_roi_luma_mae_black2':round(float(abs(v-target)[eye].mean()),2),
            'lid_luma':round(float(v[yy,xx].mean()),2),
            'cheek_below':round(float(np.mean([v[yy+k,xx] for k in range(8,15)])),2)}
side0,side1=map(light,side)
areas['side_eye_mean_absolute_luma_change']=round(float(abs(side1-side0)[283:371,590:735].mean()),2)
(OUT/'selected-shading.json').write_text(json.dumps(areas,indent=2)+'\n')

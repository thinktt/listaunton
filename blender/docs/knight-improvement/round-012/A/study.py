"""Same-camera source, current full-size studio crop, and shape under identical neutral clay."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path.insert(0,str(R/'scripts/knight'))
from audit_mission import registered,black
refs=registered()
imgs={'Original':black(refs['original']).crop((185,392,395,705)),'Black 2':black(refs['selected']).crop((185,392,395,705))}
for n,desc in [('parent','11B'),('knight','12A')]:
    for m in ['wood','clay']:
        imgs[f'{desc} {m}']=black(Image.open(D/f'{n}-{m}-fixed-detail.png').convert('RGBA'))
rows=np.array([(y,x) for y,x,*_ in json.loads((D/'mane-hollow.json').read_bytes())['Black 2']['samples'] if 470<=y<=625])
off=np.arange(-25,64)
report={}
for k,v in imgs.items():
    a=np.asarray(v.filter(ImageFilter.GaussianBlur(2.5)),float)@[.2126,.7152,.0722]
    prof=np.median(a[rows[:,0,None]-392,rows[:,1,None]-185+off],axis=0)
    report[k]={'mane':round(float(np.median(prof[(off>=-25)&(off<=-14)])),1),
               'hollow':round(float(np.median(prof[np.abs(off)<=3])),1),
               'neck':round(float(np.median(prof[(off>=20)&(off<=39)])),1),
               'min':round(float(prof.min()),1),'min_offset':int(off[prof.argmin()])}
sheet=Image.new('RGB',(210*len(imgs),346),'#252925');dr=ImageDraw.Draw(sheet)
for i,(k,v) in enumerate(imgs.items()):
    sheet.paste(v,(i*210,32));dr.text((i*210+6,8),k,fill='#fff8ef',font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15))
sheet.save(D/'fixed-study.png')
imgs={f'{desc} {m}':black(Image.open(D/f'{n}-{m}-side-detail.png').convert('RGBA')) for n,desc in [('parent','11B'),('knight','12A')] for m in ['wood','clay']}
sheet=Image.new('RGB',(257*4,403),'#252925');dr=ImageDraw.Draw(sheet)
for i,(k,v) in enumerate(imgs.items()):
    sheet.paste(v.resize((257,371),Image.Resampling.LANCZOS),(i*257,32));dr.text((i*257+6,8),k,fill='#fff8ef',font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15))
sheet.save(D/'side-study.png')
print(report)
(D/'registered-light.json').write_text(json.dumps(report,indent=2)+'\n')

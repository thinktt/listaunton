"""Plot actual cross sections on a common scale and mark the photographed hollow."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
output=Path(sys.argv[1]);keys=sys.argv[2:]
series={k:json.loads((output/f'mane-depth-{k}.json').read_bytes())['rows'] for k in keys}
colors={'parent':'#b3bfbd','A':'#f1aa6e','B':'#6ccbc9'}
rows=[484,532,580,628]
measure={}
panel=Image.new('RGB',(880,565),'#222625');d=ImageDraw.Draw(panel);font=ImageFont.load_default(size=14)
d.text((18,8),'Physical surface through the photographed mane hollow',font=font,fill='#efefe9')
for i,k in enumerate(keys):
    x=18+126*i;d.line((x,42,x+22,42),fill=colors[k],width=3);d.text((x+29,33),k,font=font,fill='#e1e2db')
for index,rowno in enumerate(rows):
    x0=47+(index%2)*436;y0=80+(index//2)*222;w=366;h=157
    center=series[keys[0]][str(rowno)]['reference_shadow_x']
    d.text((x0,y0-16),f'Image row {rowno}, source hollow x = {center}',font=font,fill='#edede8')
    curves={}
    for key,data in series.items():
        raw=data[str(rowno)]['rays'];byx={xx:z for xx,z,_,_,_ in raw if z is not None}
        xs=np.array([xx for xx in range(center-30,center+66) if xx in byx])
        zs=np.array([byx[xx] for xx in xs])
        base=[center-15,center+30]
        if not all(xx in byx for xx in base):continue
        chord=np.array([byx[t] for t in base]);baseline=chord[0]+(xs-base[0])*(chord[1]-chord[0])/(base[1]-base[0])
        curves[key]=(xs-center,zs-baseline)
        delta=byx[center]-(chord[0]+(chord[1]-chord[0])/3)
        measure.setdefault(key,{})[rowno]=round(delta,5)
    if not curves:continue
    low=min(float(curve[1].min()) for curve in curves.values());high=max(float(curve[1].max()) for curve in curves.values())
    low=min(low,-.03);high=max(high,.03)
    def xy(x,v):return x0+(x+30)*w/95,y0+h-(v-low)*h/(high-low)
    for offset in (-30,0,30,60):
        px,_=xy(offset,0);d.line((px,y0,px,y0+h),fill='#988462' if offset==0 else '#3f4946',width=1)
        d.text((px-9,y0+h+3),str(offset),font=font,fill='#dadbd4')
    _,fy=xy(0,0);d.line((x0,fy,x0+w,fy),fill='#737a73')
    for k,(xx,yy) in curves.items():
        d.line([xy(x,z) for x,z in zip(xx,yy)],fill=colors[k],width=2)
    d.text((x0-38,y0+1),f'{high:.2f}',fill='#d2d4cc',font=font)
    d.text((x0-38,y0+h-16),f'{low:.2f}',fill='#d2d4cc',font=font)
d.text((15,527),'X measures image pixels from the source hollow. Height gives model depth relative to a chord through either flank.',font=font,fill='#e3e4db')
d.text((15,547),'A deeper recess rises in this diagram. The photograph gives its location. Its exact physical depth is unknown.',font=font,fill='#e3e4db')
panel.save(output/'physical-mane-sections.png')
(output/'physical-mane-sections.json').write_text(json.dumps({'depth_at_source_line':measure,'units':'model units relative to a local chord from x-15 to x+30','rows':rows},indent=2)+'\n')

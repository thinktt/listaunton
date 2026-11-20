"""Plot the physical top of the mane and the adjacent carved head at a shared scale."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
directory=Path(sys.argv[1]); keys=sys.argv[2:]
files={k:json.loads((directory/f'crest-{k}.json').read_bytes())['profiles'] for k in keys}
stations=list(files[keys[0]])
colors={'parent':'#eee5d1','A':'#f2ad62','B':'#57c9bf'}
w,h=300,188
canvas=Image.new('RGB',(3*w,2*h+40),'#222626');draw=ImageDraw.Draw(canvas)
font=ImageFont.load_default(size=14)
for i,station in enumerate(stations):
    left=i%3*w;top=i//3*h
    paths={}
    for k in keys:
        rows=files[k][station]
        for part in ('mane','visible'):
            paths[k,part]=np.array([(row['y'],row['surfaces']['mane' if part=='mane' else row['top']]) for row in rows if part=='visible' or 'mane' in row['surfaces']])
    valid=[v for v in paths.values() if len(v)>1]
    if not valid:continue
    allpoints=np.concatenate(valid)
    center=(allpoints.min(0)+allpoints.max(0))/2
    factor=min((w-24)/np.ptp(allpoints[:,0]),(h-45)/max(.02,np.ptp(allpoints[:,1])))
    draw.text((left+8,top+4),'Longitudinal station '+station,fill='#f0eee8',font=font)
    for (k,part),xy in paths.items():
        if len(xy)<2:continue
        pts=(xy-center)*[factor,-factor]+[left+w*.5,top+h*.54]
        if part=='visible':
            continue
        draw.line([tuple(q) for q in pts],fill=colors[k],width=2)
    # Dots track the released top envelope, including the forehead and ears.
    xy=paths[keys[0],'visible']
    pts=(xy-center)*[factor,-factor]+[left+w*.5,top+h*.54]
    for x,y in pts[::3]:draw.ellipse((x-1,y-1,x+1,y+1),fill='#a5a8a7')
for i,k in enumerate(keys):
    x=12+100*i;y=2*h+19
    draw.line((x,y,x+21,y),fill=colors[k],width=2);draw.text((x+25,y-9),k,fill='#f1ede4',font=font)
draw.text((325,2*h+10),'Dots show the parent surface visible from above.',fill='#d8d9d1',font=font)
canvas.save(directory/'top-sections.png')

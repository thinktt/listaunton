"""Compare physical mane sections at identical positions and scale."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
import numpy as np
directory=Path(sys.argv[1])
labels=sys.argv[2:]
data={label:json.loads((directory/f'sections-{label}.json').read_text()) for label in labels}
colors={'parent':'#ded9ca','A':'#f2ae68','B':'#56cfcd'}
w,h=245,220
c=Image.new('RGB',(w*4,h+38),'#202424')
d=ImageDraw.Draw(c)
for j,row in enumerate(next(iter(data.values()))['sections']):
    values={k:np.array(model['sections'][j]['closed_curve_xy']) for k,model in data.items()}
    combined=np.concatenate(list(values.values()))
    center=(combined.min(0)+combined.max(0))*.5
    s=min((w-34)/np.ptp(combined,axis=0)[0],(h-44)/np.ptp(combined,axis=0)[1])
    d.text((w*j+8,5),f"Height {row['plane_z']:.2f} model units",fill='#f5f2e8')
    for label,v in values.items():
        pts=(v-center)*[s,-s]+[w*(j+.5),h*.56]
        d.line([tuple(q) for q in np.vstack([pts,pts[0]])],fill=colors[label],width=2)
x=10
for label in labels:
    d.line((x,h+18,x+22,h+18),fill=colors[label],width=3)
    d.text((x+27,h+12),label,fill='white')
    x+=100
c.save(directory/'cross-sections.png')

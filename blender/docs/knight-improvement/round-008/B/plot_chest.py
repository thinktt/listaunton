"""Plot the front surface at identical physical coordinates for all sculpts."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
out=Path(sys.argv[1]);keys=sys.argv[2:]
data={k:json.loads((out/f'chest-{k}.json').read_bytes()) for k in keys}
colors={'parent':'#f1e9d7','A':'#eeae69','B':'#68ccc2','7B':'#bf8ba6'}
font=ImageFont.load_default(size=15)
W,H=318,190
canvas=Image.new('RGB',(3*W,2*H+34),'#232626')
d=ImageDraw.Draw(canvas)
features=list(next(iter(data.values()))['horizontal'])+['center']
for i,feat in enumerate(features):
    paths={k:np.array(v['center'] if feat=='center' else v['horizontal'][feat]) for k,v in data.items()}
    if feat=='center':
        paths={k:np.column_stack((p[:,1],p[:,0])) for k,p in paths.items()}
    x0,y0=(i%3)*W,(i//3)*H
    d.text((x0+7,y0+2),'Center profile' if feat=='center' else 'Section at height '+feat,font=font,fill='#e7e5d7')
    coords=np.concatenate(list(paths.values()))
    bounds=coords.min(0),coords.max(0)
    span=np.maximum(bounds[1]-bounds[0],1e-2);factor=min((W-22)/span[0],(H-39)/span[1])
    centroid=.5*(bounds[0]+bounds[1])
    for k,xy in paths.items():
        pts=(xy-centroid)*[factor,-factor]+[x0+W*.5,y0+H*.5+11]
        d.line([tuple(pt) for pt in pts],fill=colors[k],width=2)
for i,k in enumerate(keys):
    x=13+125*i;y=2*H+15
    d.line((x,y,x+25,y),fill=colors[k],width=2);d.text((x+30,y-9),k,fill='#e7e5d7',font=font)
canvas.save(out/'breast-sections.png')

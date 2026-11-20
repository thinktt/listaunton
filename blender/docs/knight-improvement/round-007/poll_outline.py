"""Measure the two edges of the head from the earliest stable image rows."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
root=Path(sys.argv[1]).resolve()
dest=Path(sys.argv[2])
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
from probe_reflections import surface_probe
refs=registered()
photos={'Original':refs['original'],'Black 2':refs['selected'],'Accepted':Image.open(root/'assets/knight/render.png')}
for spec in sys.argv[3:]:
    label,folder=spec.split('=',1)
    photos[label]=Image.open(root/'build/knight-mission'/folder/'wood.png')
ys=list(range(295,416,5))
rows={y:{} for y in ys}
box=(184,271,610,431)
canvas=Image.new('RGB',(426*len(photos),183),'#17191a')
d=ImageDraw.Draw(canvas)
for i,(name,img) in enumerate(photos.items()):
    d.text((426*i+4,4),name,fill='white')
    canvas.paste(black(img.convert('RGBA')).crop(box),(426*i,22))
    a=np.asarray(img.convert('RGBA'))
    m=a[:,:,3]>127
    if name in ('Original','Black 2'):m&=a[:,:,:3].max(2)>12
    for y in ys:
        row=m[y]
        inds=np.where(row[: -4]&row[1:-3]&row[2:-2]&row[3:-1]&row[4:])[0]
        if inds.size:
            l,r=int(inds[0]),int(inds[-1])+4
            rows[y][name]={'x':[l,r],'center':(l+r)/2,'width':r-l}
probe,sha=surface_probe(root/'assets/knight')
for y,row in rows.items():
    if 'Accepted' in row:
        l,r=row['Accepted']['x']
        row['model_edges']=[probe(l+3,y),probe(r-3,y)]
dest.mkdir(exist_ok=True,parents=True)
(dest/'poll-outline.json').write_text(json.dumps({'scene':sha,'rows':rows},indent=2)+'\n')
canvas.save(dest/'poll-outline.png')
for y in [315,325,335,345,355,375,400]:
    row=rows[y]
    print(y, [(name,row[name]['x']) for name in photos if name in row])

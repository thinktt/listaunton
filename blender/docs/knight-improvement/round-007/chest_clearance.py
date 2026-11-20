"""Check the open shape immediately beneath the elevated knight muzzle."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
root=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2])
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
from probe_reflections import surface_probe
refs=registered()
imgs={'Original':refs['original'],'Black 2':refs['selected'],'Model':Image.open(root/'assets/knight/render.png')}
for label in sys.argv[3:]:
    name,folder=label.split('=',1)
    imgs[name]=Image.open(root/'build/knight-mission'/folder/'wood.png')
region=(493,434,770,694)
w,h=region[2]-region[0],region[3]-region[1]
canvas=Image.new('RGB',(w*len(imgs),h+22),'#161819')
d=ImageDraw.Draw(canvas)
edges={}
for i,(name,img) in enumerate(imgs.items()):
    d.text((w*i+5,4),name,fill='white')
    canvas.paste(black(img.convert('RGBA')).crop(region),(w*i,22))
    ar=np.asarray(img.convert('RGBA'))
    m=ar[:,:,3]>127
    if name in ('Original','Black 2'):m&=ar[:,:,:3].max(axis=2)>12
    lines={}
    for y in range(535,656):
        line=m[y,500:800]
        index=np.where(line[:-4]&line[1:-3]&line[2:-2]&line[3:-1]&line[4:])[0]
        if index.size:lines[y]=500+int(index[-1])+4
    edges[name]=lines
probe,sha=surface_probe(root/'assets/knight')
rows=[]
for y in sorted(set.intersection(*(set(l) for l in edges.values()))):
    row={name:lines[y] for name,lines in edges.items()}
    hit=probe(row['Model']-3,y)
    rows.append({'y':y,'x':row,'surface':hit})
out.mkdir(exist_ok=True,parents=True)
(out/'throat-and-chest.png').parent.mkdir(exist_ok=True,parents=True)
canvas.save(out/'throat-and-chest.png')
from statistics import mean
mean_errors={}
for name in list(imgs)[2:]:
    mean_errors[name]={}
    for ref in ('Original','Black 2'):
        # At row 535 the tip of the muzzle can still be the rightmost surface.
        mean_errors[name][ref]={f'{low}-{high}':round(mean(abs(r['x'][name]-r['x'][ref]) for r in rows if low<=r['y']<=high),2)
                               for low,high in [(540,580),(581,655)]}
(out/'throat-and-chest.json').write_text(json.dumps({'model':sha,'mean_absolute_error_px':mean_errors,'samples':rows},indent=2)+'\n')
print(mean_errors)
print([(r['y'],r['x'],r['surface'] and [round(z,2) for z in r['surface']['position']]) for r in rows if r['y'] in (545,565,590)])

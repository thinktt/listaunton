"""Trace the visible underside of the elevated muzzle on registered images."""
from pathlib import Path
import argparse,json,sys
import numpy as np
from PIL import Image,ImageDraw
p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('round',type=int);p.add_argument('names',nargs='*')
a=p.parse_args()
root=a.root.resolve()
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
refs=registered()
build=root/'build/knight-mission'
items={'Original':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(root/'assets/knight/render.png')}
for name in a.names:items[name]=Image.open(build/f'improvement-{a.round:03}-{name}'/'wood.png')
trace={}
# A real gap at least six pixels deep separates the muzzle from the chest.
for name,im in items.items():
    u=np.array(im.convert('RGBA'))
    mask=u[:,:,3]>127
    if name in ('Original','Black 2'):mask &= u[:,:,:3].max(2)>12
    rows={}
    for x in range(580,771):
        col=mask[385:625,x]
        starts=np.flatnonzero(col&~np.r_[False,col[:-1]])
        ends=np.flatnonzero(col&~np.r_[col[1:],False])
        for i,(s,e) in enumerate(zip(starts,ends)):
            next_start=starts[i+1] if i+1<len(starts) else len(col)
            if e-s>=9 and 480<=385+e<=560 and next_start-e>=7:
                rows[x]=[int(385+s),int(385+e)]
                break
    trace[name]=rows
common=set.intersection(*(set(y) for y in trace.values()))
common=sorted(x for x in common if 615<=x<=739)
if not common:raise ValueError('Could not isolate the common muzzle edge')
measure={}
for name in list(items)[2:]:
    measure[name]={}
    for ref in ('Original','Black 2'):
        delta=[trace[name][x][1]-trace[ref][x][1] for x in common]
        measure[name][ref]={'mae_px':round(float(np.mean(abs(np.array(delta)))),2),'mean_signed_y_error_px':round(float(np.mean(delta)),2)}
out=build/f'round-{a.round:03}-judge';out.mkdir(exist_ok=True,parents=True)
(out/'muzzle-edge.json').write_text(json.dumps({'common_column_interval':[common[0],common[-1]],'common_columns':len(common),'underside':measure,'source_and_model_envelopes':trace},indent=2)+'\n')
w,h=240,177
panel=Image.new('RGB',(w*len(items),h),'#292b2b')
d=ImageDraw.Draw(panel)
for i,(label,im) in enumerate(items.items()):
    d.text((i*w+6,4),label,fill='#e8e9e5')
    panel.paste(black(im.convert('RGBA')).crop((548,403,788,552)),(i*w,26))
panel.save(out/'muzzle-edge.png')
print(measure)

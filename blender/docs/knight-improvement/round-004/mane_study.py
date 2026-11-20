"""Compare the visible mane sweep and its intersection with the foot at 54 degrees."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw

p=argparse.ArgumentParser()
p.add_argument('root',type=Path)
p.add_argument('round',type=int)
p.add_argument('names',nargs='*')
a=p.parse_args()
root=a.root.resolve()
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import black,registered
refs=registered()
build=root/'build/knight-mission'
out=build/f'round-{a.round:03}-judge'
out.mkdir(exist_ok=True)
panels={'Original':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(root/'assets/knight/render.png')}
for label in a.names:
    panels[label]=Image.open(build/f'improvement-{a.round:03}-{label}'/'wood.png')
xs=np.arange(130,410)
ys=np.arange(535,731)
lines={}
for label,pic in panels.items():
    rgba=np.asarray(pic.convert('RGBA'))[ys[0]:ys[-1]+1,xs[0]:xs[-1]+1]
    opaque=rgba[:,:,3]>127
    if label in ('Original','Black 2'):
        opaque &= rgba[:,:,:3].max(2)>12
    # Require five adjacent piece pixels to exclude isolated dark shadow texture.
    inside=opaque[:,:-4]&opaque[:,1:-3]&opaque[:,2:-2]&opaque[:,3:-1]&opaque[:,4:]
    assert inside.any(axis=1).all()
    lines[label]=xs[inside.argmax(axis=1)]
fixedbox=(162,463,386,779)
w,h=fixedbox[2]-fixedbox[0],fixedbox[3]-fixedbox[1]
canvas=Image.new('RGB',(w*len(panels),2*(h+26)),'#171818')
draw=ImageDraw.Draw(canvas)
for i,(label,pic) in enumerate(panels.items()):
    tile=black(pic.convert('RGBA')).crop(fixedbox)
    for row in range(2):
        x=i*w;y=row*(h+26)
        draw.text((x+5,y+4),label if row==0 else label+' · outline',fill='#e9e5d9')
        canvas.paste(tile,(x,y+25))
        if row:
            for series,color in [('Original','#70e3f2'),('Black 2','#f9c268'),(label,'#e86d8d')]:
                points=[(int(x+v-fixedbox[0]),int(y+25+sy-fixedbox[1])) for sy,v in zip(ys,lines[series])]
                draw.line(points,fill=color,width=1)
metrics={}
for label,line in lines.items():
    relevant=(ys>=580)&(ys<=686)
    # Moving median suppresses the one-pixel jaggies in point of maximum indent.
    smooth=np.median(np.lib.stride_tricks.sliding_window_view(np.pad(line,(2,2),mode='edge'),5),axis=-1)
    largest=smooth[relevant].max()
    apex=ys[relevant&(smooth==largest)]
    scores={f'mean_abs_x_error_to_{ref}':round(float(np.abs(line[relevant]-lines[ref][relevant]).mean()),2) for ref in ('Original','Black 2')}
    metrics[label]={**scores,'deepest_indent_y':float(np.median(apex)),'deepest_indent_x':int(largest),'x_at_640':int(line[640-ys[0]])}
report={'method':'At the registered resolution of 1254px, first sustained run of five foreground pixels in each row. Local errors over y580–686, left contour only. Median-filtered peak x marks the handoff between mane and base silhouettes. Cyan is original, gold is black candidate 2, rose is each panel contour. Both angles must still be judged visually.','observations':metrics}
(out/'mane-profile.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
canvas.save(out/'mane-profile.png')
print(metrics)

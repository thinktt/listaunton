"""Identify the actual carving under the upper-mane reflection and the ear junction."""
from pathlib import Path
import json, sys
import numpy as np
from PIL import Image,ImageDraw
root=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2])
sys.path.insert(0,str(root/'scripts/knight'))
from probe_reflections import surface_probe
from audit_mission import registered,black

probe,source=surface_probe(root/'assets/knight')
images={'Black 2':registered()['selected'],'Parent':Image.open(root/'assets/knight/render.png')}
coords=[(320,321), (375,313), (420,315), (465,318),(320,339),(375,339),(420,341),(465,352),(375,360),(420,365),(465,371),(375,379),(420,387),(465,384),(475,366)]
rect=(260,290,510,424)
w,h=(rect[2]-rect[0])*2,(rect[3]-rect[1])*2
canvas=Image.new('RGB',(len(images)*w,h+54),'#252625')
d=ImageDraw.Draw(canvas)
hits=[]
for i,(name,im) in enumerate(images.items()):
    tile=black(im.convert('RGBA')).crop(rect).resize((w,h),Image.Resampling.LANCZOS)
    canvas.paste(tile,(i*w,20));d.text((i*w+8,2),name,fill='white')
    for j,(x,y) in enumerate(coords):
        s=probe(x,y) if i==0 else hits[j]
        if i==0:hits.append(s)
        part=s['part'].split('| ')[1] if s else 'background'
        color={'swept rounded mane':'#6ed8d5','continuous horse head and neck':'#ff8b75','near swept ear':'#f8ca78','far swept ear':'#be8de9'}.get(part,'white')
        cx=i*w+(x-rect[0])*2;cy=20+(y-rect[1])*2
        d.ellipse((cx-2,cy-2,cx+2,cy+2),outline=color,width=1)
        if i==0:print(x,y,part)
d.text((8,h+26),'Circles mark matching screen locations. Teal: mane. Coral: head. Gold: near ear. Violet: far ear.',fill='white')
(out/'crest-materials.json').write_text(json.dumps({'source_sha256':source,'probes':hits},indent=2)+'\n')
canvas.save(out/'crest-materials.png')

from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/bishop-mission/iteration-030'
d=json.loads((DOC/'style-sources.json').read_text())
im=Image.new('RGB',(1000,950),'white'); draw=ImageDraw.Draw(im)
font=ImageFont.load_default()
for path in ['C:/Windows/Fonts/arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if Path(path).is_file():
        font=ImageFont.truetype(path,20);break
for panel,(z0,z1,title) in enumerate([(0,1.65,'Socket and base'),(2.55,3.45,'Collars')]):
    x0=30+panel*500;y0=80; scale=475
    def xy(r,z):return (x0+scale*r,y0+scale*(z1-z))
    draw.text((x0,15),title,fill='black',font=font)
    for z in np.arange(z0,z1,.1):
        draw.line([xy(.2,z),xy(1.03,z)],fill='#dddddd')
        draw.text(xy(0,z),f'{z:.1f}',fill='gray',font=font)
    for p,col in [('king','#cd9439'),('queen','#9267c2'),('bishop','#258ab7')]:
        a=np.array(d[p]['evaluated_rz'])*2.0130200386/d[p]['foot_diameter']
        a=a[(a[:,1]>=z0)&(a[:,1]<=z1)]
        draw.line([xy(r,z) for r,z in a],fill=col,width=3)
    if (DOC/'proposal-native.json').exists():
        pts=np.array(json.loads((DOC/'proposal-native.json').read_text())['control_rz'])
        import sys
        sys.path.insert(0,str(Path(__file__).parent))
        from fit_side_refit import smooth_meridian
        a=smooth_meridian(pts)
        a=a[(a[:,1]>=z0)&(a[:,1]<=z1)]
        draw.line([xy(r,z) for r,z in a],fill='#ee5522',width=3)
for i,(t,c) in enumerate([('King','#cd9439'),('Queen','#9267c2'),('Bishop before','#258ab7'),('Proposal','#ee5522')]):
    draw.text((40+230*i,905),t,fill=c,font=font)
im.save(DOC/'style-profile-baseline.png')

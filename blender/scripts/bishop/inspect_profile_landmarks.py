"""Plot geometric profile rings over unchanged bishop references for diagnosis.

These are analytical projections of the control rings, not a rendered edge
detector and not evidence of the surface after subdivision. Use them to locate
the controls, then inspect actual saved-mesh neutral renders and ray probes.
"""
from pathlib import Path
import argparse, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--profile', default='scripts/bishop/profile.json')
p.add_argument('--render', default='assets/bishop/render-clay.png')
p.add_argument('--out', default='build/bishop-mission/134-geometry-audit')
a = p.parse_args()
out = ROOT/a.out
out.mkdir(parents=True, exist_ok=True)
cfg = json.loads((ROOT/a.profile).read_text())
al = json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
F = 1254/300/al['scale']
sn = math.sin(math.radians(54))
cx = (cfg['cx']-al['x']*3)*F
font = ImageFont.load_default()
for face in ['DejaVuSansMono.ttf','C:/Windows/Fonts/consola.ttf']:
    try:
        font = ImageFont.truetype(face,14)
        break
    except OSError:
        pass
groups = [
    ('collars', (285,380,700,625), [(62,'upper crest'),(59,'upper valley'),(53,'middle crest'),(49,'middle valley'),(45,'lower crest'),(42,'lower underside')]),
    ('socket', (270,610,710,885), [(31,'stem root'),(28,'lip crest'),(24,'wall root'),(22,'flare join')]),
    ('base', (180,775,800,1135), [(7,'foot top'),(10,'groove'),(14,'flare roll'),(18,'flare shoulder')]),
]
colours = ['#52e3ff','#ff6fd6','#a7ff72','#ffc65e','#aba4ff','#ff8375']
rows = []
for name,box,rings in groups:
    sheet = Image.new('RGB', ((box[2]-box[0])*2, box[3]-box[1]+90), '#14181c')
    for column,(title,path) in enumerate([('Selected white 3','assets/bishop/reference.png'),('Neutral saved model',a.render)]):
        im = Image.open(ROOT/path).convert('RGB')
        draw = ImageDraw.Draw(im)
        for idx,(ring,label) in enumerate(rings):
            r,yy = cfg['profile'][ring]
            theta = np.linspace(-math.pi+.15,-.15,200)
            points = [(cx+F*r*math.cos(t),F*(yy-al['y']*3-r*sn*math.sin(t))) for t in theta]
            draw.line(points, fill=colours[idx], width=1)
            if column == 0:
                rows.append({'region':name,'feature':label,'ring':ring,'radius':r,'axis_y':yy,'front_center_y':F*(yy-al['y']*3+r*sn)})
        sheet.paste(im.crop(box), (column*(box[2]-box[0]),30))
        d=ImageDraw.Draw(sheet)
        d.text((column*(box[2]-box[0])+10,6),title,font=font,fill='white')
    d=ImageDraw.Draw(sheet)
    for idx,(ring,label) in enumerate(rings):
        d.text((10+(idx%3)*270,box[3]-box[1]+36+22*(idx//3)),f'{ring}: {label}',font=font,fill=colours[idx])
    sheet.save(out/(name+'-control-arcs.png'))
(out/'control-landmarks.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))

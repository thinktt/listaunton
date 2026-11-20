"""Compare the photographed hollow with the visible native mane boundary."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(sys.argv[1]).resolve()
n=int(sys.argv[2]);labels=sys.argv[3:]
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
trace=json.loads((build/'round-011-judge/mane-hollow.json').read_bytes())
guide=np.array([r[:2] for r in trace['Black 2']['samples']])
refs=registered()
images={'Original black':refs['original'],'Black 2':refs['selected']}
for label in labels:
    path=root/'assets/knight/render.png' if label=='parent' else build/f'improvement-{n:03}-{label}/wood.png'
    images[label]=Image.open(path)
box=(160,399,370,688);w=212;h=289
sheet=Image.new('RGB',(w*len(images),h*2+68),'#252826')
draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=13)
data={}
for i,(name,img) in enumerate(images.items()):
    left=i*w
    pic=black(img.convert('RGBA')).crop(box)
    draw.text((left+4,3),name,fill='#eeeee5',font=font)
    for yy in (22,30+h):sheet.paste(pic,(left,yy))
    def curve(rows,color):
        pts=[(left+x-box[0],30+h+y-box[1]) for y,x in rows if box[1]<=y<box[3]]
        draw.line(pts,fill=color,width=1)
    curve(guide,'#ffb96d')
    if name not in labels:continue
    edge=np.array(json.loads((out/f'mane-edge-{name}.json').read_bytes())['rows'])[:,[0,2]]
    curve(edge,'#73d9d2')
    data[name]={}
    for lo,hi in [(460,490),(490,576),(576,626),(626,655)]:
        ys,xx=guide[(guide[:,0]>=lo)&(guide[:,0]<hi)].T
        dist=np.interp(ys,edge[:,0],edge[:,1])-xx
        data[name][f'{lo}-{hi-1}']={'mean_signed_px':round(float(np.mean(dist)),2),'mean_abs_px':round(float(np.mean(np.abs(dist))),2)}
draw.text((4,2*h+38),'Gold follows the source shadow. Cyan marks the visible inside edge of the separate mane mesh.',fill='#ece9dd',font=font)
sheet.save(out/'mane-boundaries.png')
(out/'mane-boundaries.json').write_text(json.dumps({'bands':data,'method':'Distances are measured horizontally in registered pixels. A shadow can fall off the part that casts it. For recessed cuts the depth sections and walnut views show the shape within the surface.'},indent=2)+'\n')
print(data)

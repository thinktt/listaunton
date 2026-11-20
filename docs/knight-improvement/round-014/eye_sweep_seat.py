"""Compare the real eye opening with the separately visible carved lid in the photograph."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont

root=Path(sys.argv[1]).resolve();n=int(sys.argv[2])
build=root/'build/knight-mission';j=build/f'round-{n:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
target=registered()
study=json.loads((j/'upper-eye-sweep.json').read_bytes())['results']
footprint=json.loads((j/'fixed-eye-parent.json').read_bytes())
top=np.array(footprint['columns'])
reference=np.array(study['Black 2']['trace'])
actual=np.array(study['Parent']['trace'])
photo=np.interp(top[:,0], reference[:,0], reference[:,1])
seen=np.interp(top[:,0],actual[:,0],actual[:,1])
output={}
for tag,lo,hi in [('ear side',478,490),('middle',491,521),('nose side',522,546)]:
    mask=(top[:,0]>=lo)&(top[:,0]<=hi)
    output[tag]={'median_visible_insert_below_source_crease_px':round(float(np.median(top[mask,1]-photo[mask])),1),
                 'median_visible_insert_below_rendered_crease_px':round(float(np.median(top[mask,1]-seen[mask])),1),
                 'median_visible_insert_height':round(float(np.median(top[mask,2]-top[mask,1]+1)),1)}
box=(460,455,560,503);w,h=340,168;f=ImageFont.load_default(size=14)
sheet=Image.new('RGB',(w*2,h*2+69),'#222724');draw=ImageDraw.Draw(sheet)
for i,(name,pic,trace) in enumerate([('Black candidate 2',target['selected'],reference),('Accepted knight',Image.open(root/'assets/knight/render.png'),actual)]):
    x=i*w
    im=black(pic.convert('RGBA')).crop(box).resize((w-3,h),Image.Resampling.LANCZOS)
    draw.text((x+5,5),name,font=f,fill='#f0f2e6')
    sheet.paste(im,(x,26));sheet.paste(im,(x,h+32))
    def pts(path):
        return [(x+(u+.5-box[0])*(w-3)/(box[2]-box[0]),h+32+(v+.5-box[1])*h/(box[3]-box[1])) for u,v in path]
    draw.line(pts(trace),fill='#e2ac66',width=1)
    insert=top[:,[0,1]].tolist()+top[::-1,[0,2]].tolist()
    draw.line(pts(insert+insert[:1]),fill='#66bbaf',width=1)
draw.text((6,h*2+42),'Green is the actual exposed insert on both images. Gold traces the visible upper crease.',font=f,fill='#e2e5d8')
sheet.save(j/'eye-opening-and-lid.png')
(j/'eye-opening-and-lid.json').write_text(json.dumps({'model':footprint['source_sha256'],'method':'The outer dark crease and exposed eye insert are different features. This comparison places the native fixed-camera raycast of the current insert on both registered images. It shows how much room the photographed crease leaves for carved lids; it cannot recover hidden reference geometry.','sections':output},indent=2)+'\n')
print(output)

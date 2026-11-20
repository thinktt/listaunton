"""Overlay the registered boundary between the modeled mane and the neck on both references."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
root=Path(sys.argv[1]).resolve();out=Path(sys.argv[2])
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import black,registered
refs=registered()
models=json.loads((out/'back-mane-parent.json').read_bytes())['rows']
sources={'Original black':refs['original'],'Black 2':refs['selected'],'Accepted knight':Image.open(root/'assets/knight/render.png')}
box=(158,394,374,703);w=216;h=309
can=Image.new('RGB',(3*(w+6),2*h+55),'#252725');draw=ImageDraw.Draw(can);font=ImageFont.load_default(size=13)
results={}
for i,(name,image) in enumerate(sources.items()):
    x=i*(w+6)
    draw.text((x+7,5),name,fill='white',font=font)
    rgb=black(image.convert('RGBA'))
    crop=rgb.crop(box)
    can.paste(crop,(x,26));can.paste(crop,(x,34+h))
    for j in [1,2]:
        pts=[(x+col[j]-box[0],34+h+col[0]-box[1]) for col in models]
        draw.line(pts,fill='#63c9a9',width=1)
    a=np.asarray(rgb.filter(ImageFilter.GaussianBlur(2)),float)@[.2126,.7152,.0722]
    # Trace along the inside boundary only. Summarize separately before and after its bend.
    for lo,hi in [(478,550),(550,623),(623,656)]:
        rows=np.array([c for c in models if lo<=c[0]<hi]);offset=np.arange(-25,26)
        prof=np.median(a[rows[:,0,None],rows[:,2,None]+offset],axis=0)
        results.setdefault(name,{})[str(lo)+'-'+str(hi)]={'offset_to_darkest_px':int(offset[np.argmin(prof)]),
                                                      'luma_at_boundary':round(float(prof[25]),2),'luma_trace':np.round(prof,2).tolist()}
can.save(out/'back-mane.png')
(out/'back-mane-light.json').write_text(json.dumps({'offsets':list(range(-25,26)),'regions':results},indent=2)+'\n')

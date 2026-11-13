from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
r=Path(__file__).resolve().parents[2];ref=np.array(Image.open(r/'assets/rook/ref.png').convert('RGBA'),dtype=float);ims={'accepted':np.array(Image.open(r/'assets/rook/render.png').convert('RGBA'),dtype=float)}
for n in [70,71]:ims[str(n)]=np.array(Image.open(r/f'build/rook-mission/{n:03d}-neck-wood/render.png').convert('RGBA'),dtype=float)
box=(330,595,650,800);x0,y0,x1,y1=box;mask=(ref[y0:y1,x0:x1,3]>127)&(ref[y0:y1,x0:x1,:3].max(2)>12);report={k:float(abs(a[y0:y1,x0:x1,:3]-ref[y0:y1,x0:x1,:3]).mean(2)[mask].mean()) for k,a in ims.items()};(r/'build/rook-mission/070-neck-wood/regional-error.json').write_text(json.dumps(report,indent=2)+'\n');sheet=Image.new('RGB',(1280,245),(20,20,20));d=ImageDraw.Draw(sheet)
for i,(name,a) in enumerate([('Reference',ref),*ims.items()]):sheet.paste(Image.fromarray(a.astype(np.uint8)).convert('RGB').crop(box),(320*i,40));d.text((320*i+5,10),name,fill='white')
sheet.save(r/'build/rook-mission/070-neck-wood/neck-comparison.png');print(report)

from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
r=Path(__file__).resolve().parents[2];ref=Image.open(r/'assets/rook/ref.png').convert('RGBA');reg=json.loads((r/'assets/rook/original-alignment.json').read_text());s,x,y=(reg[k] for k in ['scale','x','y']);W=ref.width;original=Image.open(r/'assets/rook/original.png').convert('RGBA').transform(ref.size,Image.Transform.AFFINE,(s*300/W,0,x*3,0,s*300/W,y*3),Image.Resampling.BILINEAR);ims={'Original':original,'Selected':ref,'Accepted':Image.open(r/'history/rook-mission-066/assets/rook/render.png').convert('RGBA'),'Trial 072':Image.open(r/'build/rook-mission/072-neck-wood/render.png').convert('RGBA')};box=(330,595,650,800);sheet=Image.new('RGB',(1280,245),(20,20,20));d=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(ims.items()):sheet.paste(im.convert('RGB').crop(box),(i*320,40));d.text((i*320+5,10),name,fill='white')
sheet.save(r/'build/rook-mission/072-neck-wood/neck-source-comparison.png');report={};x0,y0,x1,y1=box
for label in ['Original','Selected']:
 target=np.array(ims[label],float)[y0:y1,x0:x1];mask=(target[:,:,3]>127)&(target[:,:,:3].max(2)>12);report[label]={k:float(abs(np.array(ims[k],float)[y0:y1,x0:x1,:3]-target[:,:,:3]).mean(2)[mask].mean()) for k in ['Accepted','Trial 072']}
(r/'build/rook-mission/072-neck-wood/regional-error.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

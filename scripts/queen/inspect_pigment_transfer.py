"""Compare high-pass material data at fixed coordinates; no reference edits."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from image_math import blur
ROOT=Path(__file__).resolve().parents[2];build=ROOT/'build/queen-mission'
ref=np.load(build/'pigment-fit-039/reference-linear.npy')
old=np.load(build/'pigment-fit-039/pigment.npy')[:,:,:3]
expected=np.load(build/'057-opaque-pigment/expected-pigment.npy')[:,:,:3] if (build/'057-opaque-pigment/expected-pigment.npy').exists() else None
if expected is None:
 paths=list(build.glob('057*/expected-pigment.npy'));assert len(paths)==1;expected=np.load(paths[0])[:,:,:3]
a=np.array(Image.open(build/'067-no-relief/diagnostic-pigment.png').convert('RGB'),dtype=np.float32)/255
actual=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
inputs={'Reference luminance':ref,'Old pigment':old,'Expected projection':expected,'Actual baked pigment':actual}
regions={'bowl':(350,165,420,255),'body':(410,365,565,420),'stem':(425,610,550,720),'base':(330,850,610,985)}
details={}
for name,a in inputs.items():
 x=np.log(.003+a@np.array([.2126,.7152,.0722]));details[name]=x-blur(x,r=3,passes=3)
records={}
for name,(x0,y0,x1,y1) in regions.items():
 d={n:a[y0:y1,x0:x1] for n,a in details.items()};r=d['Reference luminance']
 records[name]={n:{'correlation_to_reference':float(np.corrcoef(r.ravel(),v.ravel())[0,1]),'std':float(v.std()),'correlation_to_expected':float(np.corrcoef(d['Expected projection'].ravel(),v.ravel())[0,1])} for n,v in d.items()}
out=build/'067-no-relief';(out/'pigment-transfer.json').write_text(json.dumps(records,indent=2)+'\n')
canvas=Image.new('RGB',(1200,620),(23,24,26));draw=ImageDraw.Draw(canvas)
for i,(name,a) in enumerate(details.items()):
 draw.text((i*300+8,5),name,fill='white')
 for j,(region,box) in enumerate([('Crown',(330,100,640,300)),('Base',(330,850,610,985))]):
  x0,y0,x1,y1=box;v=a[y0:y1,x0:x1];im=Image.fromarray(np.uint8(np.clip(.5+v,0,1)*255)).convert('RGB');im.thumbnail((292,270));canvas.paste(im,(i*300+4,35+j*290));draw.text((i*300+8,310+j*290),region,fill='white')
canvas.save(out/'diagnostic-grain-transfer.png');print(json.dumps(records,indent=2))

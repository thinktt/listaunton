from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
r=Path(__file__).resolve().parents[2];o=r/'build/rook-mission/088-foot-finish'
paths={'Reference':r/'assets/rook/ref.png','Accepted078':r/'assets/rook/render.png','082 lights':r/'build/rook-mission/082-foot-flanks/wood.png'}
for n in [86,87,88]:paths[str(n)]=r/f'build/rook-mission/{n:03d}-foot-finish/wood.png'
sheet=Image.new('RGB',(3600,200));d=ImageDraw.Draw(sheet);report={}
for i,(label,p) in enumerate(paths.items()):
 im=Image.open(p).convert('RGBA');sheet.paste(im.convert('RGB').crop((200,940,800,1100)),(600*i,40));d.text((600*i+10,10),label,fill='white');a=np.array(im);report[label]={}
 for x in [400,483,560,600]:
  v=a[990:1080,x,:3].mean(1);report[label][str(x)]={'peak_y':int(v.argmax())+990,'peak':float(v.max()),'pixels_above_160':int((v>160).sum())}
sheet.save(o/'comparison.png');(o/'profiles.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

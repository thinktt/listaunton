from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
r=Path(__file__).resolve().parents[2];o=r/'build/rook-mission/080-foot-flanks';o.mkdir(exist_ok=True);ims={'Reference':Image.open(r/'assets/rook/ref.png').convert('RGBA'),'Accepted':Image.open(r/'assets/rook/render.png').convert('RGBA')}
for n in [80,81,82]:ims[str(n)]=Image.open(r/f'build/rook-mission/{n:03d}-foot-flanks/wood.png').convert('RGBA')
sheet=Image.new('RGB',(3000,200),(20,20,20));d=ImageDraw.Draw(sheet);report={}
for i,(name,im) in enumerate(ims.items()):
 sheet.paste(im.convert('RGB').crop((200,940,800,1100)),(600*i,40));d.text((600*i+10,10),name,fill='white');a=np.array(im,float);rows={}
 for x in [300,350,400,450,483,520,560,600,650]:
  y0,y1=(950,1060) if x in [300,650] else (990,1080);v=a[y0:y1,x,:3].mean(1);peak=int(v.argmax());rows[str(x)]={'peak_y':int(y0+peak),'mean_rgb_peak':float(v[peak])}
 report[name]=rows
sheet.save(o/'foot-comparison.png');(o/'profiles.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

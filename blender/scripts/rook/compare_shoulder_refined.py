from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'build/rook-mission/078-shoulder-flanks';ims={'Reference':Image.open(ROOT/'assets/rook/ref.png').convert('RGBA'),'Accepted':Image.open(ROOT/'history/rook-mission-072/assets/rook/render.png').convert('RGBA')}
for n in [77,78]:ims[str(n)]=Image.open(ROOT/f'build/rook-mission/{n:03d}-shoulder-flanks/wood.png').convert('RGBA')
report={};sheet=Image.new('RGB',(1880,200),(20,20,20));d=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(ims.items()):
 sheet.paste(im.convert('RGB').crop((250,800,720,950)),(470*i,40));d.text((470*i+5,10),name,fill='white');a=np.array(im,dtype=float);stats={}
 for x in [400,483,560]:
  v=a[850:930,x,:3].mean(1);peak=int(v.argmax());base=float(np.median(v));threshold=base+.5*(v[peak]-base);lo=hi=peak
  while lo>0 and v[lo-1]>threshold:lo-=1
  while hi<len(v)-1 and v[hi+1]>threshold:hi+=1
  stats[str(x)]={'peak_y':peak+850,'peak_mean_rgb':float(v[peak]),'local_baseline':base,'half_height_width_pixels':hi-lo+1}
 report[name]=stats
sheet.save(out/'strip-comparison.png');(out/'highlight-profiles.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))



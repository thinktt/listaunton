from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'build/rook-mission/070-neck-wood';base=np.asarray(Image.open(ROOT/'assets/rook/render.png').convert('RGBA'),dtype=float);report={}
for n in [70,71]:
 b=ROOT/f'build/rook-mission/{n:03d}-neck-wood';a=np.asarray(Image.open(b/'render.png').convert('RGBA'),dtype=float);delta=np.abs(a-base);mask=base[:,:,3]>127;report[str(n)]={'fixed_foreground_mean_rgb_delta':float(delta[:,:,:3][mask].mean()),'fixed_max_delta':float(delta.max()),'fixed_alpha_identical':bool(np.array_equal(a[:,:,3],base[:,:,3]))}
for view in ['profile','rear']:
 sheet=Image.new('RGB',(1200,640),(20,20,20));d=ImageDraw.Draw(sheet)
 for i,(label,p) in enumerate([('Accepted',ROOT/f'assets/rook/{view}.png'),('Trial 070',ROOT/f'build/rook-mission/070-neck-wood/{view}.png'),('Trial 071',ROOT/f'build/rook-mission/071-neck-wood/{view}.png')]):
  im=Image.open(p).convert('RGB').resize((400,600));sheet.paste(im,(400*i,40));d.text((400*i+10,10),label,fill='white')
 sheet.save(out/f'{view}-comparison.png')
(out/'fixed-difference.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


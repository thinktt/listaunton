from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts/king'))
from audit_mission import audit,black
variant=sys.argv[1];out=R/'build/king-mission'/variant;H=R/'history/king-mission-005'
audit(out/'wood.png',H/'render.png',out,out/'king.blend')
a=np.array(Image.open(H/'render.png').convert('RGBA')).astype(np.int16);b=np.array(Image.open(out/'wood.png').convert('RGBA')).astype(np.int16);m=(a[:,:,3]>127)&(b[:,:,3]>127);d=abs(a-b)
y,x=np.unravel_index(d[:,:,:3].max(2).argmax(),d.shape[:2])
report={'mean_foreground_rgb_difference_255':float(d[:,:,:3][m].mean()),'max_rgb_difference_255':int(d[:,:,:3].max()),'foreground_pixels_over_4':int((d[:,:,:3].max(2)[m]>4).sum()),'foreground_pixels_over_12':int((d[:,:,:3].max(2)[m]>12).sum()),'max_error_pixel_xy':[int(x),int(y)]}
(out/'front-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
sheet=Image.new('RGB',(1200,470),(22,24,28));draw=ImageDraw.Draw(sheet);box=(max(0,x-90),max(0,y-90),min(1254,x+90),min(1254,y+90))
diff=Image.fromarray(np.uint8(np.clip(d[:,:,:3]*4,0,255))).convert('RGBA')
for i,(title,im) in enumerate([('Accepted 005',Image.open(H/'render.png')),('Trial',Image.open(out/'wood.png')),('Difference x4',diff)]):
 draw.text((i*400+10,8),title,fill='white');sheet.paste(black(im.convert('RGBA')).crop(box).resize((390,390)),(i*400+5,45))
sheet.save(out/'front-max-difference.png')

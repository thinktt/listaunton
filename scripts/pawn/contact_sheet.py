from pathlib import Path
from PIL import Image,ImageDraw
import json,shutil
p=Path(__file__).resolve().parents[2];a=p/'assets/pawn';W=1254
s=json.loads((a/'original-alignment.json').read_text());wa=next(q for q in json.loads((p/'assets/candidates/alignment.json').read_text())['pieces']['pawn'] if q['id']=='white')
b=Image.open(a/'original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(s['scale']*300/W,0,s['x']*3,0,s['scale']*300/W,s['y']*3),Image.Resampling.BILINEAR)
w=Image.open(a/'white-original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(s['scale']/wa['scale']*300/W,0,(s['x']-wa['x'])*3/wa['scale'],0,s['scale']/wa['scale']*300/W,(s['y']-wa['y'])*3/wa['scale']),Image.Resampling.BILINEAR)
frames=[b,w,Image.open(a/'reference.png').convert('RGBA'),Image.open(a/'render.png').convert('RGBA')]
canvas=Image.new('RGB',(1280,510),'#181b20');d=ImageDraw.Draw(canvas)
for i,(im,title) in enumerate(zip(frames,['Original black','Original white (registered)','Selected Black 2','Final neutral model / 54 deg'])):
 im=im.crop((225,310,735,1040)).resize((320,458));bg=Image.new('RGB',im.size,'#101317');bg.paste(im,mask=im.getchannel('A'));canvas.paste(bg,(i*320,30));d.text((i*320+10,8),title,fill='#eeeeee')
d.text((10,493),'Four geometric passes. Sources are unchanged. Original sprites govern geometry; candidate is a secondary detail guide.',fill='#bbbbbb')
canvas.save(a/'comparison-contact-sheet.png')

from pathlib import Path
from PIL import Image,ImageDraw
import json
root=Path(__file__).resolve().parents[2];reg=json.loads((root/'assets/rook/original-alignment.json').read_text());s,x,y=[reg[k] for k in ['scale','x','y']]
orig=Image.open(root/'assets/rook/original.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(s*300/1254,0,x*3,0,s*300/1254,y*3),Image.Resampling.BILINEAR)
ims=[orig,Image.open(root/'assets/rook/ref.png').convert('RGBA'),Image.open(root/'assets/rook/render.png').convert('RGBA')]
out=Image.new('RGB',(1500,440),(20,20,20));d=ImageDraw.Draw(out)
for i,(name,im) in enumerate(zip(['Original (registered)','Selected high-res','Accepted model'],ims)):
 bg=Image.alpha_composite(Image.new('RGBA',im.size,(0,0,0,255)),im).convert('RGB');out.paste(bg.crop((290,260,680,580)).resize((490,400)),(500*i,35));d.text((500*i+5,10),name,fill='white')
out.save(root/'build/rook-mission/038-floor-probe/sources.png')

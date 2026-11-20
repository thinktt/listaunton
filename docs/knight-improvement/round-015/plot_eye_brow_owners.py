"""Color the actual ear, lid, and exposed eye over the matched board photographs."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);codes=['parent',*sys.argv[3:]]
build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
ref=json.loads((build/'round-014-judge/upper-eye-sweep.json').read_bytes())['results']['Black 2']['trace']
w,h=282,147;font=ImageFont.load_default(size=13)
canvas=Image.new('RGB',(w*(1+len(codes)),2*h+66),'#242923');d=ImageDraw.Draw(canvas)
sources=[('Black 2 / parent geometry below','parent',root/'assets/knight/ref.png')]+[(k,k,root/'assets/knight/render.png' if k=='parent' else build/f'improvement-{n:03}-{k}/wood.png') for k in codes]
for i,(label,key,file) in enumerate(sources):
    m=np.load(out/f'brow-owners-{key}.npz');xs,ys=m['xs'],m['ys']
    box=(int(xs[0]),int(ys[0]),int(xs[-1])+1,int(ys[-1])+1)
    src=Image.open(file).convert('RGB').crop(box)
    pic=np.array(src,dtype=float)
    palette=np.array([[0,0,0],[140,91,45],[76,145,226],[36,194,151],[110,110,110]])
    colored=np.uint8(np.clip(.47*pic+.53*palette[m['owners']],0,255))
    x=i*w
    d.text((x+5,4),label,font=font,fill='#f0f1e9')
    canvas.paste(src.resize((w,h),Image.Resampling.LANCZOS),(x,25))
    canvas.paste(Image.fromarray(colored).resize((w,h),Image.Resampling.NEAREST),(x,h+32))
    pts=[(x+(xx+.5-box[0])*w/(box[2]-box[0]),h+32+(yy+.5-box[1])*h/(box[3]-box[1])) for xx,yy in ref]
    d.line(pts,fill='#ffdd95',width=2)
d.text((5,2*h+40),'Blue = ear, green = eye, brown = head. Gold follows the photographed upper crease.',font=font,fill='#f0eee2')
canvas.save(out/'upper-eye-surfaces.png')

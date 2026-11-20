"""Compare the photographed eye with each projected inner-eye opening at identical scale."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);keys=sys.argv[3:]
build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import black,registered
refs=registered();crop=(427,428,577,521);w,h=315,195
canvas=Image.new('RGB',(3*w,len(keys)*(2*h+24)),'#212522');draw=ImageDraw.Draw(canvas)
font=ImageFont.load_default(size=14)
for i,k in enumerate(keys):
    report=json.loads((out/f'fixed-eye-{k}.json').read_bytes())
    fixed=root/'assets/knight/render.png' if k=='parent' else build/f'improvement-{n:03}-{k}/wood.png'
    panels=[('Original',refs['original']),('Black 2',refs['selected']),(k,Image.open(fixed))]
    for j,(title,im) in enumerate(panels):
        x=j*w;y=i*(h*2+24)
        draw.text((x+7,y+2),title+' with '+k+' opening',font=font,fill='#eee9df')
        tile=black(im.convert('RGBA')).crop(crop).resize((w,h),Image.Resampling.LANCZOS)
        canvas.paste(tile,(x,y+24));canvas.paste(tile,(x,y+h+24))
        upper=[(x+(xx+.5-crop[0])*w/(crop[2]-crop[0]),y+h+24+(lo+.5-crop[1])*h/(crop[3]-crop[1])) for xx,lo,_ in report['columns']]
        lower=[(x+(xx+.5-crop[0])*w/(crop[2]-crop[0]),y+h+24+(hi+.5-crop[1])*h/(crop[3]-crop[1])) for xx,_,hi in report['columns']]
        draw.line(upper+lower[::-1]+upper[:1],fill='#80eac5',width=1)
canvas.save(out/'fixed-eye-openings.png')

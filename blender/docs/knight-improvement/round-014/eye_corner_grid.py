"""Print a registered grid for reading the two corners of the eye on the references."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont

root=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2])
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
refs=registered()
box=(458,455,563,506)
scale=4
w,h=(box[2]-box[0])*scale,(box[3]-box[1])*scale
sheet=Image.new('RGB',(w*2+2,h*2+78),'#202223')
draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=11)
for i,(name,im) in enumerate([('Black 2',refs['selected']),('Accepted walnut',Image.open(root/'assets/knight/render.png')),('Original black',refs['original']),('Neutral polish',Image.open(root/'build/knight-mission/round-013-judge/passes-A/polish.png'))]):
    l=(i%2)*(w+2);top=(i//2)*(h+39)
    crop=black(im.convert('RGBA')).crop(box).resize((w,h),Image.Resampling.BICUBIC)
    sheet.paste(crop,(l,top+24))
    draw.text((l+4,top),name,font=font,fill='white')
    for x in range(460,563,10):
        u=l+(x-box[0])*scale
        draw.text((u-7,top+12),str(x),font=font,fill='#a9c8bb')
        for y in range(460,506,10):
            v=top+24+(y-box[1])*scale
            draw.point((u,v),fill='#8dbaad')
    for y in range(460,506,10):
        draw.text((l+2,top+24+(y-box[1])*scale-4),str(y),font=font,fill='#a9c8bb')
sheet.save(out)

"""Place registered source details next to pigment, neutral-lit finish, and walnut."""
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);keys=sys.argv[3:]
build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
ref=registered()
w,h=237,104
panel=Image.new('RGB',(5*w,2*len(keys)*(h+22)+24),'#232524')
draw=ImageDraw.Draw(panel)
font=ImageFont.load_default(size=14)
regions={'Upper mane':(260,290,497,394),'Eye and cheek':(389,423,583,522)}
for i,k in enumerate(keys):
    fixed=root/'assets/knight/render.png' if k=='parent' else build/f'improvement-{n:03}-{k}/wood.png'
    pictures=[('Original',ref['original']),('Black 2',ref['selected']),(k+' · walnut',Image.open(fixed)),(k+' · pigment',Image.open(out/f'passes-{k}/pigment.png')),(k+' · neutral finish',Image.open(out/f'passes-{k}/polish.png'))]
    for col,(title,img) in enumerate(pictures):
        for j,(name,box) in enumerate(regions.items()):
            x=col*w; y=(i*2+j)*(h+22)
            im=black(img.convert('RGBA')).crop(box)
            im=im.resize((round(im.width*h/im.height),h),Image.Resampling.LANCZOS)
            panel.paste(im,(x+(w-im.width)//2,y+22))
            draw.text((x+6,y+1),title+' / '+name,font=font,fill='#efebe2')
draw.text((6,panel.height-20),'Pigment uses the existing diffuse colour without studio light. Neutral finish keeps the actual light, wood normals and polish on a grey base.',font=font,fill='#dedbd1')
panel.save(out/'surface-comparison.png')

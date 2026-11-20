"""Annotate the existing geometry with the image-to-sculpt correspondences."""
from pathlib import Path
import sys,json
from PIL import Image,ImageDraw,ImageFont
r=Path(sys.argv[1]).resolve();j=Path(sys.argv[2]);labels=sys.argv[3:] or ['parent']
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import registered,black
font=ImageFont.load_default(size=13)
ref=registered()['selected']
w,h=300,177
step=2*h+32
sheet=Image.new('RGB',(w*3,step*len(labels)+20),'#242825');d=ImageDraw.Draw(sheet)
parent=json.loads((j/'brow-native-parent.json').read_bytes())['samples']
for index,label in enumerate(labels):
    data=json.loads((j/f'brow-native-{label}.json').read_bytes())['samples']
    if label=='parent':
        fixed,side=[r/'assets/knight'/name for name in ['render.png','guide-render.png']]
    else:
        tag=j.name.split('-')[1];trial=j.parent/f'improvement-{tag}-{label}'
        fixed,side=[trial/name for name in ['wood.png','wood-side.png']]
    base=index*step
    photos=[('Black 2',ref,'fixed'),(label+' / 54°',Image.open(fixed),'fixed'),(label+' / 7° side',Image.open(side),'side')]
    for i,(name,image,view) in enumerate(photos):
        anchor=[point[view] for point in parent]
        x0=round((anchor[0][0]+anchor[-1][0])/2-75);y0=round((anchor[0][1]+anchor[-1][1])/2-44)
        box=(x0,y0,x0+w//2,y0+88)
        crop=black(image.convert('RGBA')).crop(box).resize((w,h),Image.Resampling.LANCZOS)
        l=i*w;d.text((l+5,base+4),name,fill='#eeeee4',font=font);sheet.paste(crop,(l,base+23));sheet.paste(crop,(l,base+h+28))
        for row in data:
            px,py=row[view];x=l+(px-x0)*2;y=base+h+28+(py-y0)*h/88
            if x<l or x>=l+w or y<base+h+28 or y>=base+2*h+28:continue
            if view=='side' and not row['visible_in_side']:
                d.ellipse((x-2,y-2,x+2,y+2),outline='#e7be7f')
            else:
                d.ellipse((x-2,y-2,x+2,y+2),fill='#86cebc')
d.text((5,step*len(labels)),'Dots locate the photographed fold on each model. Open circles mark points hidden from the side.',font=font,fill='#e7e8dd')
sheet.save(j/'brow-side.png')

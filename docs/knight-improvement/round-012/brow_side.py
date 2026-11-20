"""Annotate the existing geometry with the image-to-sculpt correspondences."""
from pathlib import Path
import sys,json
from PIL import Image,ImageDraw,ImageFont
r=Path(sys.argv[1]).resolve();j=Path(sys.argv[2])
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import registered,black
data=json.loads((j/'brow-native-parent.json').read_bytes())['samples']
font=ImageFont.load_default(size=13)
photos=[('Black 2',registered()['selected'],'fixed'),('Parent / 54°',Image.open(r/'assets/knight/render.png'),'fixed'),('Parent / 7° side',Image.open(r/'assets/knight/guide-render.png'),'side')]
w,h=300,177
sheet=Image.new('RGB',(w*3,2*h+49),'#242825');d=ImageDraw.Draw(sheet)
for i,(name,image,view) in enumerate(photos):
    points=[row[view] for row in data];x0=round((points[0][0]+points[-1][0])/2-75);y0=round((points[0][1]+points[-1][1])/2-44)
    box=(x0,y0,x0+w//2,y0+88)
    crop=black(image.convert('RGBA')).crop(box).resize((w,h),Image.Resampling.LANCZOS)
    l=i*w;d.text((l+5,4),name,fill='#eeeee4',font=font);sheet.paste(crop,(l,23));sheet.paste(crop,(l,h+28))
    for row,(px,py) in zip(data,points):
        x=l+(px-x0)*2;y=h+28+(py-y0)*h/88
        if x<l or x>=l+w or y<h+28 or y>=2*h+28:continue
        if view=='side' and not row['visible_in_side']:
            d.ellipse((x-2,y-2,x+2,y+2),outline='#e7be7f')
        else:
            d.ellipse((x-2,y-2,x+2,y+2),fill='#86cebc')
d.text((5,2*h+32),'Dots locate the photographed fold on the current model. Open circles mark points hidden from the side.',font=font,fill='#e7e8dd')
sheet.save(j/'brow-side.png')

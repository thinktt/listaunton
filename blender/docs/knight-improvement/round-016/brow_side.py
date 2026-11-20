"""Annotate the existing geometry with the image-to-sculpt correspondences."""
from pathlib import Path
import sys,json
from PIL import Image,ImageDraw,ImageFont
r=Path(sys.argv[1]).resolve();j=Path(sys.argv[2]);labels=sys.argv[3:] or ['parent']
crest='--crest' in labels
if crest:labels.remove('--crest')
muzzle='--muzzle' in labels
if muzzle:labels.remove('--muzzle')
prefix='poll-trace' if crest else 'muzzle-trace' if muzzle else 'brow-native'
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import registered,black
font=ImageFont.load_default(size=13)
ref=registered()['selected']
w,h=300,177
step=2*h+32
sheet=Image.new('RGB',(w*3,step*len(labels)+20),'#242825');d=ImageDraw.Draw(sheet)
parent=json.loads((j/f'{prefix}-parent.json').read_bytes())['samples']
for index,label in enumerate(labels):
    data=json.loads((j/f'{prefix}-{label}.json').read_bytes())['samples']
    if label=='parent':
        fixed,side=[r/'assets/knight'/name for name in ['render.png','guide-render.png']]
    else:
        tag=j.name.split('-')[1];trial=j.parent/f'improvement-{tag}-{label}'
        fixed,side=[trial/name for name in ['wood.png','wood-side.png']]
    base=index*step
    photos=[('Black 2',ref,'fixed'),(label+' / 54°',Image.open(fixed),'fixed'),(label+' / 7° side',Image.open(side),'side')]
    for i,(name,image,view) in enumerate(photos):
        anchor=[point[view] for point in parent]
        width=w//2
        if crest or muzzle:width=max(170,round(max(p[0] for p in anchor)-min(p[0] for p in anchor)+75))
        height=round(width*h/w)
        x0=round((min(p[0] for p in anchor)+max(p[0] for p in anchor)-width)/2)
        y0=round((min(p[1] for p in anchor)+max(p[1] for p in anchor)-height)/2)
        box=(x0,y0,x0+width,y0+height)
        crop=black(image.convert('RGBA')).crop(box).resize((w,h),Image.Resampling.LANCZOS)
        l=i*w;d.text((l+5,base+4),name,fill='#eeeee4',font=font);sheet.paste(crop,(l,base+23));sheet.paste(crop,(l,base+h+28))
        for row in data:
            px,py=row[view];x=l+(px-x0)*w/width;y=base+h+28+(py-y0)*h/height
            if x<l or x>=l+w or y<base+h+28 or y>=base+2*h+28:continue
            if view=='side' and not row['visible_in_side']:
                d.ellipse((x-2,y-2,x+2,y+2),outline='#e7be7f')
            else:
                color='#e2aa73' if crest and row['source_hit'].endswith('horse head and neck') else '#86cebc'
                d.ellipse((x-2,y-2,x+2,y+2),fill=color)
caption='Green points fall on the mane. Amber points fall on the forehead. Open circles are hidden from the side.' if crest else 'Dots locate the photographed fold on each model. Open circles mark points hidden from the side.'
d.text((5,step*len(labels)),caption,font=font,fill='#e7e8dd')
sheet.save(j/('upper-mane-side.png' if crest else 'muzzle-side.png' if muzzle else 'brow-side.png'))

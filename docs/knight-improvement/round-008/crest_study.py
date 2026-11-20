"""Locate the broad upper-mane reflection and the valley underneath in the reference view."""
from pathlib import Path
import argparse, json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

p=argparse.ArgumentParser()
p.add_argument('root', type=Path)
p.add_argument('round', type=int)
p.add_argument('codes', nargs='*')
a=p.parse_args()
root=a.root.resolve()
build=root/'build/knight-mission'
out=build/f'round-{a.round:03}-judge'
sys.path.insert(0, str(root/'scripts/knight'))
from audit_mission import black, registered

refs=registered()
images={'Original':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(root/'assets/knight/render.png')}
for code in a.codes:
    images[code]=Image.open(build/f'improvement-{a.round:03}-{code}'/'wood.png')
# A smoothed intensity cross-section finds the central crest highlight. The
# white and original references have different light, so each uses its own
# threshold between this highlight and the hollow immediately below it.
anchors_x=[300,320,340,360,380,400,420,440,460,470]
anchors_y=[345,341,338,338,338,339,340,342,351,357]
xs=range(312,457,4)
crop_box=(258,287,493,401)
w,h=crop_box[2]-crop_box[0],crop_box[3]-crop_box[1]
sheet=Image.new('RGB',(w*len(images),2*h+44),'#282a29')
draw=ImageDraw.Draw(sheet)
data={}
for i,(key,raw) in enumerate(images.items()):
    rgb=black(raw.convert('RGBA'))
    luminance=np.asarray(rgb.filter(ImageFilter.GaussianBlur(2.7)),dtype=float)@[.2126,.7152,.0722]
    rows=[]
    for x in xs:
        guide=round(float(np.interp(x,anchors_x,anchors_y)))
        l=luminance[:,x-2:x+3].mean(axis=1)
        crest=guide-14+int(l[guide-14:guide+15].argmax())
        valley=crest+6+int(l[crest+6:crest+29].argmin())
        cut=(l[crest]+l[valley])/2
        top=bottom=crest
        while top>crest-22 and l[top-1]>cut: top-=1
        while bottom<valley and l[bottom+1]>cut: bottom+=1
        rows.append({'x':x,'crest_y':crest,'valley_y':valley,'highlight_top':top,'highlight_bottom':bottom,'crest_luma':round(float(l[crest]),2),'valley_luma':round(float(l[valley]),2)})
    data[key]=rows
    tile=rgb.crop(crop_box)
    draw.text((i*w+4,3),key,fill='white')
    for row in range(2):
        y=22+row*h
        sheet.paste(tile,(i*w,y))
        if row:
            for name,color in [('crest_y','#8ce3f6'),('valley_y','#feaa67')]:
                draw.line([(i*w+r['x']-crop_box[0],y+r[name]-crop_box[1]) for r in rows],fill=color)
    print(key, {n:round(float(np.median([r[n] for r in rows])),1) for n in ('crest_y','valley_y','crest_luma','valley_luma')},'median_band',np.median([r['highlight_bottom']+1-r['highlight_top'] for r in rows]))
draw.text((4,2*h+25),'Cyan follows the reflection. Amber follows the darker facet immediately below.',fill='#f5ead9')
out.mkdir(parents=True,exist_ok=True)
sheet.save(out/'crest-highlight.png')
(out/'crest-highlight.json').write_text(json.dumps({'method':'Registered vertical luminance profiles, 2.7px blur and 5px lateral average, peak within 14px of the visible black-2 crest, local minimum 6-28px lower. Highlight width at half of their contrast. The lit band and wood tone are affected by both surface angle and finish.','traces':data},indent=2)+'\n')

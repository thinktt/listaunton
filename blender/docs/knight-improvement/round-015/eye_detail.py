"""Compare the eye, its lower lip and brow at their fixed source registration."""
from pathlib import Path
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

stage=Path(sys.argv[1]).resolve()
n=int(sys.argv[2])
build=stage/'build/knight-mission'
out=build/f'round-{n:03}-judge'
out.mkdir(exist_ok=True)
sys.path.insert(0,str(stage/'scripts/knight'))
from audit_mission import registered,black
refs=registered()
views={'Original black':refs['original'],'Black 2':refs['selected'],'Original white (mirrored)':refs['white_mirrored'],
       'Parent':Image.open(stage/'assets/knight/render.png')}
for code in sys.argv[3:]:
    views[code]=Image.open(build/f'improvement-{n:03}-{code}/wood.png')
crop=(442,440,574,519)
boxes={'Eye and its carving':(466,461,553,489),'Lower lid and cheek':(463,488,548,512)}
one=272
tile_h=224
font=ImageFont.load_default(size=14)
cols=3
panel=Image.new('RGB',(cols*one,((len(views)+cols-1)//cols)*tile_h),'#222522')
draw=ImageDraw.Draw(panel)
planes={}
for index,(label,photo) in enumerate(views.items()):
    pic=black(photo.convert('RGBA'))
    x=index%cols*one
    y=index//cols*tile_h
    draw.text((x+8,y+4),label,font=font,fill='#eee9df')
    thumb=pic.crop(crop).resize((264,158),Image.Resampling.LANCZOS)
    panel.paste(thumb,(x+4,y+28))
    if label in ['Original black','Original white (mirrored)']:
        draw.text((x+8,y+194),'Sprite enlarged at the same registration',font=font,fill='#b8b8af')
    a=np.asarray(pic.filter(ImageFilter.GaussianBlur(1.2)),float)
    planes[label]=a @ [.2126,.7152,.0722]
panel.save(out/'eye-detail.png')
def normalized(a):
    return (a-a.mean()) / max(float(a.std()),1e-7)
result={}
for label,a in planes.items():
    result[label]={}
    for region,(l,t,r,b) in boxes.items():
        patch=a[t:b,l:r]
        target=planes['Black 2'][t:b,l:r]
        dims=normalized(patch)*normalized(target)
        result[label][region]={'luminance_mae':round(float(np.mean(np.abs(target-patch))),3),
                               'pattern_correlation':round(float(dims.mean()),4)}
report={'method':'1.2 pixel Gaussian and Rec.709 luminance on registered sRGB crops. Normalized correlation describes placement of light and dark detail, independent of mean and contrast. Shape, native-scale readability and sculpture also require visual inspection.','boxes':boxes,'scores':result}
(out/'eye-detail.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
for name,value in result.items(): print(name,value)

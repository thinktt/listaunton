"""Inspect walnut, unlit pigment and neutral polish at the same upper-mane crop."""
import hashlib, json, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

root=Path(sys.argv[1]).resolve()
number=int(sys.argv[2]);names=['parent',*sys.argv[3:]]
build=root/'build/knight-mission';judge=build/f'round-{number:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black

refs=registered();target=black(refs['selected'])
anchors=np.array(json.loads((judge/'crest-anchors.json').read_bytes())['anchor_points'])
xs=np.arange(320,449);ys=np.interp(xs,anchors[:,0],anchors[:,1]).round().astype(int)
offsets=np.arange(-17,30)
def profiles(image):
    rgb=np.asarray(image.filter(ImageFilter.GaussianBlur(1.6)),float)
    gray=rgb@[.2126,.7152,.0722]
    region=gray[ys[None,:]+offsets[:,None],xs[None,:]]
    return np.median(region,axis=1)
def describe(profile):
    peak=int(np.argmax(np.where((offsets>=-8)&(offsets<=8),profile,-np.inf)))
    # Record any continuous rise below the main edge. The near ear is outside this band.
    start=peak+5
    end=np.flatnonzero(offsets<=24)[-1]+1
    rises=[(profile[last]-min(profile[start:last]),last) for last in range(start+1,end)]
    strength,secondary=max(rises)
    trough=start+int(np.argmin(profile[start:secondary]))
    return {'main_offset':int(offsets[peak]),'primary_luma':round(float(profile[peak]),2),
            'underface_trough_offset':int(offsets[trough]),'underface_crest_offset':int(offsets[secondary]),
            'strongest_underface_rise_luma':round(float(max(0,strength)),2),
            'profile':np.round(profile,2).tolist()}
w,h=239,116;f=ImageFont.load_default(size=13)
sheet=Image.new('RGB',(3*w,len(names)*(h+25)+h+37),'#242924');d=ImageDraw.Draw(sheet)
box=(253,288,497,406)
def place(pic,title,x,y):
    tile=pic.crop(box).resize((w-2,h),Image.Resampling.LANCZOS)
    d.text((x+4,y+3),title,font=f,fill='#efeedf');sheet.paste(tile,(x,y+21))
place(black(refs['original']),'Original black',0,0);place(target,'Black candidate 2',w,0)
data={'Black 2':describe(profiles(target)), 'Original black':describe(profiles(black(refs['original'])))}
for row,name in enumerate(names):
    folder=judge/f'passes-{name}';record=json.loads((folder/'source.json').read_bytes())
    fixed=root/'assets/knight/render.png' if name=='parent' else build/f'improvement-{number:03}-{name}/wood.png'
    mat={'Walnut':fixed,'Pigment':folder/'pigment.png','Neutral polish':folder/'polish.png'}
    data[name]={}
    for col,(label,file) in enumerate(mat.items()):
        if label!='Walnut':assert hashlib.sha256(file.read_bytes()).hexdigest()==record['views'][file.stem]
        image=black(Image.open(file).convert('RGBA'))
        place(image,name+' / '+label,col*w,(row+1)*(h+25))
        data[name][label]=describe(profiles(image))
sheet.save(judge/'crest-finish.png')
(judge/'crest-finish.json').write_text(json.dumps({'sections':data,'offsets':offsets.tolist(),
    'method':'Aligned crest crops with pigment-only emission and constant-grey base under the actual varnish and studio. Median vertical luminance profiles follow the photographed edge over columns 320–448. The secondary rise measures the strongest increase below the primary bevel through offset +24; a broad return and a narrow second line must be distinguished visually.'},indent=2)+'\n')

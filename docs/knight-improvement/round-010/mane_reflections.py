"""Compare light across the wood at two elevations of the registered mane."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image, ImageFilter, ImageDraw,ImageFont
r=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);keys=sys.argv[3:]
build=r/'build/knight-mission';out=build/f'round-{n:03}-judge'
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import black,registered
refs=registered()
pics={'Original':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(r/'assets/knight/render.png')}
for k in keys:pics[k]=Image.open(build/f'improvement-{n:03}-{k}/wood.png')
anchors_x=[300,320,340,360,380,400,420,440,460,470]
anchors_y=[345,341,338,338,338,339,340,342,351,357]
methods={'secondary_y':[294,314],'secondary_x':[320,374],'main_x':[312,456],'main_offsets':[-28,28]}
data={}
for k,pic in pics.items():
    rgb=black(pic.convert('RGBA'))
    luma=np.asarray(rgb.filter(ImageFilter.GaussianBlur(2.0)),dtype=float)@[.2126,.7152,.0722]
    xs=np.arange(312,457,2)
    center=np.rint(np.interp(xs,anchors_x,anchors_y)).astype(int)
    offsets=np.arange(-28,29)
    strip=luma[center[None,:]+offsets[:,None],xs[None,:]]
    # The lengthwise median limits the influence of individual highlights in the grain.
    line=np.median(strip,axis=1)
    i=15+int(line[15:42].argmax())
    # Subtract the sloping baseline separately on the two sides of the ridge.
    # The upper face is lighter than the underneath on the actual carved wood.
    low=np.interp(offsets,[-23.,20.],[np.median(line[:10]),np.median(line[-14:])])
    signal=line-low
    lo=hi=i
    while lo>0 and signal[lo-1]>=.5*signal[i]:lo-=1
    while hi+1<len(line) and signal[hi+1]>=.5*signal[i]:hi+=1
    upper=luma[294:314,320:374]
    data[k]={'main_median_profile':np.round(line,2).tolist(),'main_baseline':np.round(low,2).tolist(),'main_highlight_offset':int(offsets[i]),'main_half_contrast_width':int(hi-lo+1),'main_peak_luma':round(float(line[i]),2),'upper_band_luma':round(float(np.median(upper.max(0))),2)}
palette={'Original':'#a6a7a0','Black 2':'#e5c285','Parent':'#f0eee9','A':'#66c0d6','B':'#ce8cbc'}
w,h=700,280
sheet=Image.new('RGB',(w,h),'#252727');d=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=14)
x0,x1=52,465;y0,y1=224,28
for level in (0,50,100,150,200):
    y=y0+level*(y1-y0)/200
    d.line([(x0,y),(x1,y)],fill='#434846');d.text((9,y-8),str(level),font=font,fill='#d4d7ce')
for i in (-20,-10,0,10,20):
    x=x0+(i+28)*(x1-x0)/56;d.text((x-9,y0+3),str(i),font=font,fill='#d4d7ce')
for j,(name,entry) in enumerate(data.items()):
    line=entry['main_median_profile'];points=[(x0+i*(x1-x0)/56,y0+val*(y1-y0)/200) for i,val in enumerate(line)]
    d.line(points,fill=palette[name],width=2)
    y=36+j*36;d.line((482,y+7,501,y+7),fill=palette[name],width=2)
    d.text((509,y-1),name+'  ·  '+str(entry['main_half_contrast_width'])+' px',font=font,fill='#ebe8dd')
d.text((105,253),'Vertical offset from the black 2 edge (px)',font=font,fill='#e1dfd5')
d.text((483,222),'Width at half contrast',font=font,fill='#ddd9ce')
sheet.save(out/'mane-light-profiles.png')
(out/'mane-light-profiles.json').write_text(json.dumps({'method':'At registered native resolution, 2 px Gaussian blur and median of Rec.709 display luma along a fixed curved transect. The width at half contrast is measured above a sloping baseline joining the two unlit flanks. The second band is the median peak in columns 320–373 for y294–313. Values measure visible light rather than physical bevel thickness.','axes':methods,'samples':data},indent=2)+'\n')
for k,row in data.items():print(k,{f:v for f,v in row.items() if 'profile' not in f and 'baseline' not in f})

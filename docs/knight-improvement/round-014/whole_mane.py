"""Measure the broad wooden face from the back silhouette to the mane's inside cut."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
r=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);args=sys.argv[3:]
b=r/'build/knight-mission';j=b/f'round-{n:03}-judge'
sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import registered,black,silhouette
trace=json.loads((b/'round-011-judge/mane-hollow.json').read_bytes())['Black 2']['samples']
refs=registered();mask=silhouette(refs['selected'],True)
rows=np.array([(y,np.flatnonzero(mask[y])[0],x) for y,x,*unused in trace if 488<=y<=581])
percent=np.arange(3,165,2)
xx=np.rint(rows[:,1,None]+(rows[:,2]-rows[:,1])[:,None]*percent/100).astype(int)
panels={'Original black':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(r/'assets/knight/render.png')}
for k in args:panels[k]=Image.open(b/f'improvement-{n:03}-{k}/wood.png')
font=ImageFont.load_default(size=14)
chart=Image.new('RGB',(740,318),'#252927');d=ImageDraw.Draw(chart)
d.text((16,8),'Brightness across the full mane face',font=font,fill='#f2f0e4')
colors=['#b7c4b6','#ffbf79','#a3bfcd','#bd92da','#55d4ad']
stats={};geometries=[]
for (name,im),color in zip(panels.items(),colors):
    light=np.asarray(black(im.convert('RGBA')).filter(ImageFilter.GaussianBlur(3.0)),float)@[.2126,.7152,.0722]
    v=np.median(light[rows[:,0,None],xx],axis=0)
    stats[name]={'brightness_profile':v.round(2).tolist(),
                 'rear_face':round(float(np.median(v[(percent>=21)&(percent<=39)])),2),
                 'inside_face':round(float(np.median(v[(percent>=65)&(percent<=83)])),2),
                 'face_brightest_percent':int(percent[(percent>=15)&(percent<=89)][np.argmax(v[(percent>=15)&(percent<=89)])])}
    geometries.append((name,color,v))
limit=max(60,10*np.ceil(max(v.max() for _,_,v in geometries)/10.))
X=lambda t:45+650*t/165.
Y=lambda t:237-155*t/limit
for i in np.arange(0,limit+1,20):
    y=Y(i);d.line((X(0),y,X(165),y),fill='#404740');d.text((15,y-5),str(int(i)),font=font,fill='#c8c9c2')
for i in [0,25,50,75,100,125,150]:
    x=X(i);d.line((x,Y(0),x,Y(limit)),fill='#a49174' if i==100 else '#404740')
    d.text((x-9,243),str(i)+'%',font=font,fill='#d3d5cc')
for k,(name,color,v) in enumerate(geometries):
    x=18+k*140;d.line((x,53,x+18,53),fill=color,width=3);d.text((x+22,46),name,font=font,fill='#e8eadf')
    d.line([(X(perc),Y(val)) for perc,val in zip(percent,v)],fill=color,width=2)
d.text((16,278),'0% is the back silhouette. 100% is the hollow in black candidate 2. The neck lies to its right.',font=font,fill='#e8eadf')
chart.save(j/'whole-mane.png')
(j/'whole-mane.json').write_text(json.dumps({'method':'Identical samples on registered pixels at horizontal fractions from the Black 2 outside edge to its hollow. The median profile covers image rows 488 to 581, blurred 3 px to suppress small wood pores.','width_range_px':[int(min(rows[:,2]-rows[:,1])),int(max(rows[:,2]-rows[:,1]))],'percent':percent.tolist(),'results':stats},indent=2)+'\n')
print({k:{a:b for a,b in info.items() if a!='brightness_profile'} for k,info in stats.items()})

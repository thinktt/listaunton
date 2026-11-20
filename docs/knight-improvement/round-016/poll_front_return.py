"""Locate the front-shoulder glint in both references and intersect its rays with the knight."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont

r=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);j=r/f'build/knight-mission/round-{n:03}-judge'
sys.path.insert(0,str(r/'scripts/knight'))
from probe_reflections import surface_probe
from audit_mission import registered,black
refs=registered()
probes,model=surface_probe(r/'assets/knight')
pictures={'Original black':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(r/'assets/knight/render.png')}
for code in sys.argv[3:]:
    pictures[code]=Image.open(r/f'build/knight-mission/improvement-{n:03}-{code}/wood.png')
axis=np.arange(298,472)
yline=np.rint(np.interp(axis,[298,320,340,360,380,400,420,440,452,462,471],[347,341,338,338,338,339,340,342,345,350,355])).astype(int)
X=np.broadcast_to(axis[:,None],(len(axis),19));Y=yline[:,None]+np.arange(-23,-4)
palette={'Original black':'#c7cebd','Black 2':'#e4ac66','Parent':'#81b9cc','A':'#ad9ad3','B':'#85c99c'}
record={};w,h=270,138
sheet=Image.new('RGB',(len(pictures)*w,2*h+57),'#252925');d=ImageDraw.Draw(sheet);f=ImageFont.load_default(size=13)
for i,(name,image) in enumerate(pictures.items()):
    im=black(image.convert('RGBA'))
    rgb=np.asarray(im.filter(ImageFilter.GaussianBlur(3)),float)
    vals=rgb[Y,X]@[.2126,.7152,.0722]
    threshold=np.percentile(vals,90);weights=np.maximum(vals-threshold,0)
    xy=[float((values*weights).sum()/weights.sum()) for values in (X,Y)]
    peak=X.ravel()[vals.argmax()],Y.ravel()[vals.argmax()]
    roi=im.crop((252,282,500,409)).resize((w-2,h),Image.Resampling.LANCZOS)
    l=i*w;d.text((l+5,4),name,font=f,fill='#e6ebe0')
    sheet.paste(roi,(l,24));sheet.paste(roi,(l,h+30))
    def coord(x,y):return (l+(x+.5-252)*(w-2)/248,h+30+(y+.5-282)*h/127)
    poly=[coord(x,y-23) for x,y in zip(axis,yline)]+[coord(x,y-5) for x,y in zip(axis[::-1],yline[::-1])]
    d.line(poly+poly[:1],fill='#6d9d92',width=1)
    px,py=coord(*xy);d.ellipse((px-4,py-4,px+4,py+4),outline=palette[name],width=2)
    record[name]={'centroid_xy':np.round(xy,2).tolist(),'brightest_xy':[int(v) for v in peak],
                  'median_luma':round(float(np.median(vals)),2),'p90_luma':round(float(threshold),2),
                  'forward_share_of_excess_light':round(float(weights[axis>=410].sum()/weights.sum()),3)}
positions={}
for key,dval in record.items():
    for where in ('centroid_xy','brightest_xy'):
        xy=[round(v) for v in dval[where]]
        positions[key+' '+where]=probes(*xy)
d.text((5,2*h+38),'Circles locate the brightest tenth of the wood above the crest. All models use the same registration.',font=f,fill='#e3e8dd')
sheet.save(j/'front-cap-glint.png')
(j/'front-cap-glint.json').write_text(json.dumps({'model':model,'samples':record,'native_intersections':positions,
    'method':'Within a common strip above the edge, blur at 3px then locate the weighted center of positive contrast above each image’s 90th percentile. Cast these source positions onto the actual exported parent and record the smooth world normal and outgoing mirror direction.'},indent=2)+'\n')
print(record)

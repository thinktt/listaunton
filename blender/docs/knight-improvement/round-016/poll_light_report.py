"""Compare identical crest samples after changing individual studio lights."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
r=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);out=r/f'build/knight-mission/round-{n:03}-judge'
sys.path.insert(0,str(r/'scripts/knight'));from audit_mission import registered,black
series=out/'poll-lights-parent';source=json.loads((series/'source.json').read_bytes());refs=registered()
pics={'Original black':refs['original'],'Black 2':refs['selected']}
for name,hsh in source['shots'].items():
    path=series/(name+'.png')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==hsh
    pics[name]=Image.open(path)
gray=np.array([.2126,.7152,.0722]);axis=np.arange(295,477)
guide=np.rint(np.interp(axis,[282,300,320,340,360,380,400,420,440,452,462,470,478],[353,346,341,338,338,338,339,340,342,345,350,354,360])).astype(int)
def sections(im):
    sm=np.asarray(black(im.convert('RGBA')).filter(ImageFilter.GaussianBlur(1.5)),float)
    return sm,sm@gray
def trace(lum):
    d=np.arange(-9,10);return guide+d[np.argmax(lum[guide[:,None]+d,axis[:,None]],axis=1)]
_,saved=sections(pics['studio']);ys=trace(saved)
res={}
for label,im in pics.items():
    rgb,lum=sections(im)
    # The control lamps get the exact same points as the full studio, while
    # the two references get the ridge of their own photographed bevel.
    loc=trace(lum) if label in ('Original black','Black 2') else ys
    result={}
    for band,l,u in [('rear',298,340),('middle',341,409),('front',410,450),('tip',451,476)]:
        m=(axis>=l)&(axis<=u);x=axis[m];y=loc[m];color=rgb[y,x]
        cap=lum[guide[m,None]+np.arange(-22,-6),x[:,None]]
        result[band]={'median_luma':round(float(np.median(color@gray)),1),'median_R_minus_B':round(float(np.median(color[:,0]-color[:,2])),1),
                      'top_plane_q90':round(float(np.percentile(cap,90)),1)}
    res[label]=result
w,h=244,123;font=ImageFont.load_default(size=12)
sheet=Image.new('RGB',(w*3,3*(h+23)),'#252922');d=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate(pics.items()):
    left=(i%3)*w;top=(i//3)*(h+23)
    d.text((left+5,top+3),name.replace('-',' '),font=font,fill='#e9ece2')
    sheet.paste(black(im.convert('RGBA')).crop((250,285,499,410)).resize((w-2,h),Image.Resampling.LANCZOS),(left,top+21))
sheet.save(out/'poll-light-comparison.png')
(out/'poll-light-comparison.json').write_text(json.dumps({'source':source['model'],'results':res,'method':'For each studio control sample precisely the bevel positions from the saved scene. Reference measurements follow the crest in each source. The upper-plane value is the 90th percentile over the cap 6–22px above the reference edge.'},indent=2)+'\n')
for k,v in res.items():print(k,v['middle'],v['front'])

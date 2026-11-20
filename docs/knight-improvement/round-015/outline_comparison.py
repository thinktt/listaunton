"""Show the three real silhouettes against both registered black references."""
from pathlib import Path
import argparse,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser()
p.add_argument('root',type=Path);p.add_argument('number',type=int);p.add_argument('candidates',nargs='*')
args=p.parse_args()
root=args.root.resolve();build=root/'build/knight-mission'
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
refs=registered();assets=root/'assets/knight'
photos={'Original':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(assets/'render.png')}
for name in args.candidates:
    photos[name]=Image.open(build/f'improvement-{args.number:03}-{name}'/'wood.png')
# Ignore isolated one-pixel splashes along the edge of the generated reference.
def edge(im,source):
    px=np.asarray(im.convert('RGBA'))
    mask=px[:,:,3]>127
    if source:mask&=px[:,:,:3].max(2)>12
    run=mask[:,:-4]&mask[:,1:-3]&mask[:,2:-2]&mask[:,3:-1]&mask[:,4:]
    rows={}
    for y in range(run.shape[0]):
        idx=np.flatnonzero(run[y])
        if idx.size:rows[y]=(int(idx[0]),int(idx[-1])+4)
    return rows
contours={k:edge(v,k in ('Original','Black 2')) for k,v in photos.items()}
models=list(photos)[2:]
boxes=[('Upper head',(192,281,608,381),range(310,356),[0,1]),('Space below muzzle',(530,487,746,665),range(540,656),[1])]
try:font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
except OSError:font=ImageFont.load_default()
cw=400
heights=(164,248)
canvas=Image.new('RGB',(cw*len(models),sum(heights)+38),'#232625')
draw=ImageDraw.Draw(canvas)
colors={'Original':'#68dabe','Black 2':'#e1ac59','Model':'#ececf4'}
stats={}
for col,key in enumerate(models):
    stats[key]={}
    for row,(label,box,ys,sides) in enumerate(boxes):
        x0,y0,x1,y1=box
        top=sum(heights[:row])
        factor=min((cw-10)/(x1-x0),(heights[row]-64)/(y1-y0))
        tw,th=round((x1-x0)*factor),round((y1-y0)*factor)
        ox=cw*col+(cw-tw)//2;oy=top+32
        tile=black(photos[key].convert('RGBA')).crop(box).resize((tw,th),Image.Resampling.LANCZOS)
        canvas.paste(tile,(ox,oy))
        draw.text((cw*col+8,top+4),f'{key} · {label}',font=font,fill='#eeece0')
        rr=list(ys)
        for name in ('Original','Black 2',key):
            line=contours[name]
            for side in sides:
                poly=[(ox+factor*(line[y][side]-x0),oy+factor*(y-y0)) for y in rr if y in line]
                draw.line(poly,fill=colors.get(name,colors['Model']),width=1)
        stats[key][label]={}
        for name in ('Original','Black 2'):
            diff=[abs(contours[key][y][side]-contours[name][y][side]) for y in rr for side in sides]
            stats[key][label][name]=round(float(np.mean(diff)),3)
        msg=stats[key][label]
        draw.text((cw*col+8,top+heights[row]-29),f"Mean error   original {msg['Original']:.1f} px   black 2 {msg['Black 2']:.1f} px",font=font,fill='#e8e5d9')
for i,(name,c) in enumerate(colors.items()):
    x=8+i*130;draw.line((x,sum(heights)+18,x+24,sum(heights)+18),fill=c,width=2)
    draw.text((x+30,sum(heights)+4),name,font=font,fill='#eae7de')
out=build/f'round-{args.number:03}-judge';out.mkdir(exist_ok=True,parents=True)
canvas.save(out/'registered-edge-detail.png')
(out/'registered-edge-detail.json').write_text(json.dumps({'regions':{'Upper head':'both outside edges, rows 310 to 355 inclusive','Space below muzzle':'chest outside edge, rows 540 to 655 inclusive'},'mean_absolute_horizontal_error_px':stats},indent=2)+'\n')
print(stats)

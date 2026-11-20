"""Compare the wood from actual, equally lit relief variants at the same registration."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(ROOT/'scripts/knight')]
from audit_mission import black, registered

refs=registered()
box=(290,530,725,765)
pictures={key:black(img).crop(box) for key,img in [
    ('Original',refs['original']),('Black 2',refs['selected']),('Parent',Image.open(OUT/'parent-wood.png').convert('RGBA'))]}
for i,tag in enumerate(('Initial','Partial','Full','Anterior blend')):
    pictures[tag]=black(Image.open(OUT/f'accents-{i}.png').convert('RGBA'))
target=pictures['Black 2']
paths=json.loads((OUT.parent/'chest-carving-study/paths-fit.json').read_text())['curves']
y,x=np.indices((235,435))
x+=290
y+=530
trace={}
for at in ['shoulder','crest','trough']:
    co=np.array([item['pixel'] for item in paths[at]])
    trace[at]=np.interp(y,co[:,1],co[:,0])
def stats(img):
    ar=np.array(img.convert('RGB').filter(ImageFilter.GaussianBlur(2.4)))@np.array([.2126,.7152,.0722])
    ref=np.array(target.convert('RGB').filter(ImageFilter.GaussianBlur(2.4)))@np.array([.2126,.7152,.0722])
    result={}
    for label,center in trace.items():
        rows=(y>=580)&(y<=728)
        region=rows&(abs(x-center)<=12)
        band=rows&(abs(x-center)<=3)
        result[label+'_luma']=round(float(ar[band].mean()),1)
        result[label+'_luma_error_mae_24px']=round(float(abs(ar[region]-ref[region]).mean()),2)
        # Find centered bright feature within 14px of the source trace.
        differences=[]
        for j in range(580,729):
            yy=j-530
            idx=np.flatnonzero(abs(x[yy]-center[yy])<=14)
            x1=idx[np.argmax(ar[yy,idx])]
            x2=idx[np.argmax(ref[yy,idx])]
            differences.append(abs(x1-x2))
        result[label+'_ridge_peak_abserror']=round(float(np.mean(differences)),2)
    return result
metrics={name:stats(im) for name,im in pictures.items()}
(OUT/'accent-comparison.json').write_text(json.dumps(metrics,indent=2)+'\n')
sheet=Image.new('RGB',(435*3,(235+20)*3),'#1a1c1c')
d=ImageDraw.Draw(sheet)
for idx,(name,img) in enumerate(pictures.items()):
    x0=(idx%3)*435
    y0=(idx//3)*255
    d.text((x0+8,y0+4),name,fill='white')
    sheet.paste(img,(x0,y0+20))
sheet.save(OUT/'accent-comparison.png')
print(metrics)

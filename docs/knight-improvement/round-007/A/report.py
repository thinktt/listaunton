"""Report registered outer contours and show the affected carving at board and sculpture scale."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from fit import shapes,limits
from review import put,load
A=D.parents[2]/'assets/knight'
def name_box(im,rect,title):
    box=im.crop(rect).convert('RGBA')
    bg=Image.new('RGBA',box.size,'#282a2b');bg.alpha_composite(box)
    return bg.convert('RGB')
def stats():
    src=shapes()
    ims=dict(zip(['Original','Black 2','Parent'],src));ims['7A']=load(D/'wood.png')
    rows=np.arange(295,416);edges={k:limits(v,rows,k in ('Original','Black 2')) for k,v in ims.items()}
    out={'bands':{},'row_325':{k:e[30].tolist() for k,e in edges.items()}}
    for band in [(295,389),(305,375),(295,415),(395,415)]:
        data={}
        for name in ['Parent','7A']:
            data[name]={}
            for target in ['Original','Black 2']:
                valid=np.isfinite(edges[target][:,0])&(rows>=band[0])&(rows<=band[1])
                delta=abs(edges[name][valid]-edges[target][valid]);data[name][target]={
                'left_mae':float(delta[:,0].mean()),'right_mae':float(delta[:,1].mean()),'pooled_mae':float(delta.mean())}
        out['bands'][str(band)]=data
    gaps={}
    for name in ['Parent','7A']:
        a=np.asarray(ims[name])[:,:,3]>128;cuts=[]
        # A line down from the sky into the crown may cross the true outline
        # once. A second stretch of sky would show an exposed ear tang.
        for x in range(208,507):
            row=a[270:380,x];e=np.flatnonzero(np.diff(row.astype(int)))
            for j in range(1,len(e)-1,2):cuts.append([x,int(e[j]+271),int(e[j+1]-e[j])])
        gaps[name]=cuts
    out['upper_alpha_gaps']=gaps
    (D/'contour.json').write_text(json.dumps(out,indent=2)+'\n')
    rect=(153,274,681,430)
    sheet=Image.new('RGB',(542*2,212*2),'#232527')
    for i,name in enumerate(ims):
        x=i%2*542;y=i//2*212;panel=name_box(ims[name],rect,name);w,h=panel.size
        draw=ImageDraw.Draw(panel)
        ids=np.flatnonzero((rows>=300)&(rows<=380))
        if name in ('Parent','7A'):
            for ref,c in [('Original','#72d8e4'),('Black 2','#e9b153')]:
                for side in [0,1]:
                    line=[(float(edges[ref][j,side]-rect[0]),rows[j]-rect[1]) for j in ids if np.isfinite(edges[ref][j,side])]
                    draw.line(line,fill=c,width=1)
        sheet.paste(panel,(x+5,y+25))
        ImageDraw.Draw(sheet).text((x+6,y+5),name,fill='white')
    ImageDraw.Draw(sheet).text((9,396),'Cyan and gold trace the registered original and Black 2.',fill='white')
    sheet.save(D/'poll-contour.png')
    return out

def gallery():
    sheet=Image.new('RGB',(1400,958),'#262728')
    src=shapes()
    for i,(name,f) in enumerate(zip(['Original','Black 2','Parent','7A'],[*src,load(D/'wood.png')])):
        put(sheet,f,(153,272,642,561),(i*350,0),(348,227),name+' / upper head')
        put(sheet,f,(168,256,780,1065),(i*350,229),(348,302),name+' / 54 degrees')
        icon=f.resize((100,100),Image.Resampling.LANCZOS);sheet.paste(icon,(i*350+124,527),icon)
    for i,(name,f) in enumerate([('Parent side clay',D/'parent-side-clay.png'),('7A side clay',D/'candidate-side-clay.png'),
                              ('Parent side wood',A/'guide-render.png'),('7A side wood',D/'wood-side.png')]):
        put(sheet,f,(250,82,958,545),(i*350,645),(348,278),name)
    sheet.save(D/'poll-carving.png')
if __name__=='__main__':
    print(json.dumps(stats()))
    if (D/'candidate-side-clay.png').exists():gallery()

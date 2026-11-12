"""Compare source/relief ablations and vertical profiles at the pawn foot."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from audit_mission import ROOT,rgba,sheet
from derive_wood import blur

REGIONS={'worst':(545,930,577,962),'groove':(520,935,565,951),
         'right-line':(530,947,582,969),'front-line':(458,968,504,986),
         'left-line':(380,942,432,968),'flare':(370,882,445,913)}

def run(folder):
    out=ROOT/'build/pawn-mission'/folder
    rec=json.loads((out/'measurement.json').read_text(encoding='utf8'))
    images={'selected':rgba(ROOT/'assets/pawn/reference.png')}
    for label,value in rec['renders'].items():
        filename=value['file'] if isinstance(value,dict) else label+'.png'
        images[label]=rgba(out/filename)
    target=np.asarray(images['selected'])[:,:,:3].astype(float);stats={}
    for label,im in images.items():
        a=np.asarray(im)[:,:,:3].astype(float);rows={}
        for region,(x0,y0,x1,y1) in REGIONS.items():
            q=a[y0:y1,x0:x1];ref=target[y0:y1,x0:x1]
            lum=q@np.array([.24,.53,.23]);want=ref@np.array([.24,.53,.23])
            hp=lum-blur(lum,r=2,passes=1);th=want-blur(want,r=2,passes=1)
            rows[region]={'rgb_mae_255':float(abs(q-ref).mean()),'mean_luma':float(lum.mean()),
                          'p95_luma':float(np.quantile(lum,.95)),'fine_correlation':float(np.corrcoef(hp.ravel(),th.ravel())[0,1])}
        lum=a@np.array([.24,.53,.23]);rows['profile_x_555_565']=lum[922:984,555:565].mean(1).tolist()
        stats[label]=rows
    (out/'analysis.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf8')
    keys=list(images)
    if 'all' in images:keys=['selected','all','without-base','without-other','without-world','direct-gloss-only']
    keys=[k for k in keys if k in images]
    sheet([(k,images[k]) for k in keys],(511,916,598,989),250,out/'comparison.png')
    plot=Image.new('RGB',(720,350),(22,24,27));d=ImageDraw.Draw(plot)
    colors=['#eeb95e','#f4f0e8','#e36e5b','#7ec3e4','#a8c981','#c494dc']
    for i,key in enumerate(keys):
        vals=stats[key]['profile_x_555_565'];points=[(40+j*10,310-v*1.0) for j,v in enumerate(vals)]
        d.line(points,fill=colors[i],width=2);d.text((45+(i%3)*220,10+(i//3)*18),key,fill=colors[i])
    for j in range(0,62,10):d.text((40+j*10,325),str(922+j),fill='#cccccc')
    d.text((15,65),'luma (0-255)',fill='#cccccc');d.text((600,325),'image y',fill='#cccccc')
    plot.save(out/'profiles.png')
    print(json.dumps({k:v['worst'] for k,v in stats.items()},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder');a=p.parse_args();run(a.folder)

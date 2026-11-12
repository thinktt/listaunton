"""Compare actual cropped source/relief ablations at the fixed collar view."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from audit_mission import ROOT,rgba,sheet
from derive_wood import blur

def run(folder,kind):
    out=ROOT/'build/pawn-mission'/folder
    rec=json.loads((out/'measurement.json').read_text(encoding='utf8'))
    images={'selected':rgba(ROOT/'assets/pawn/reference.png')}
    for label,value in rec['renders'].items():
        filename=value['file'] if isinstance(value,dict) else label+'.png'
        images[label]=rgba(out/filename)
    regions={'left':(405,588,481,630),'right':(516,578,569,617),
             'front':(495,616,558,642),'worst':(437,606,469,638),'head-line':(425,570,509,594)}
    target=np.asarray(images['selected'])[:,:,:3].astype(float);stats={}
    for label,im in images.items():
        a=np.asarray(im)[:,:,:3].astype(float);rows={}
        for region,(x0,y0,x1,y1) in regions.items():
            q=a[y0:y1,x0:x1];ref=target[y0:y1,x0:x1]
            lum=q@np.array([.24,.53,.23]);want=ref@np.array([.24,.53,.23])
            hp=lum-blur(lum,r=2,passes=1);th=want-blur(want,r=2,passes=1)
            rows[region]={'rgb_mae_255':float(abs(q-ref).mean()),'mean_luma':float(lum.mean()),
                          'p95_luma':float(np.quantile(lum,.95)),'fine_correlation':float(np.corrcoef(hp.ravel(),th.ravel())[0,1])}
        stats[label]=rows
    (out/'analysis.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf8')
    if kind=='lights':
        keys=['selected','all','without-collar','without-diffuse','without-other','direct-gloss-only']
        if not all(key in images for key in keys):keys=['selected','all']+[key for key in images if key.startswith('without-')]
    else:keys=list(images)
    sheet([(k,images[k]) for k in keys],(412,584,489,641),260,out/'comparison.png')
    print(json.dumps({k:v['worst'] for k,v in stats.items()},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('kind',choices=['lights','relief'])
    a=p.parse_args();run(a.folder,a.kind)

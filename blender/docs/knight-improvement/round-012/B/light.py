from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageFilter
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from reference_images import registered,black
ROW=np.array([(y,x) for y,x,*_ in json.loads((D/'source-trace.json').read_text())['Black 2']['samples'] if 470<=y<=625])
OFF=np.arange(-25,64)
def get(im):
    rgb=black(im)
    l=np.asarray(rgb.filter(ImageFilter.GaussianBlur(2.5)),float)@[.2126,.7152,.0722]
    if rgb.width==1254:x,y=0,0
    else:x,y=175,374
    return l[ROW[:,0,None]-y,ROW[:,1,None]-x+OFF]
def run():
    refs=registered();imgs={'Original':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(D/'parent-wood.png')}
    if '--final' in sys.argv:imgs['12B']=Image.open(D/'wood.png')
    else:
        for f in sorted(D.glob('study-*-walnut.png')):
            idx=int(f.name.split('study-')[1].split('-walnut')[0])
            if idx>=0:imgs[str(idx)]=Image.open(f)
    output={};qref=get(imgs['Black 2'])
    for name,im in imgs.items():
        q=get(im);v=np.median(q,axis=0);center=np.median(v[abs(OFF)<=3])
        left=np.median(v[(OFF>=-25)&(OFF<=-14)]);right=np.median(v[(OFF>=20)&(OFF<=39)])
        row={'mane':round(float(left),2),'hollow':round(float(center),2),'neck':round(float(right),2),
             'mane_above_hollow':round(float(left-center),2),'neck_above_hollow':round(float(right-center),2),
             'trough_offset':int(OFF[v.argmin()]),'corr':round(float(np.corrcoef(q.ravel(),qref.ravel())[0,1]),3),
             'mae':round(float(abs(q-qref).mean()),2)}
        print(name,row);row['profile']=np.round(v,2).tolist();output[name]=row
    (D/('light-final.json' if '--final' in sys.argv else 'light-studies.json')).write_text(json.dumps(output,indent=2)+'\n')
if __name__=='__main__':run()

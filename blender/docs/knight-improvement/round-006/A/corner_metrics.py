"""Report changes in the eye corner and the continuous alpha contour of the crown."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;ASSETS=D.parents[2]/'assets/knight'
def metrics():
    result={}
    datasets={k:np.load(D/f'eyes-{k}.npz') for k in ('parent','A')}
    u,v=datasets['A']['u'],datasets['A']['v']
    for name,data in datasets.items():
        stats={}
        for side in ('near','far'):
            h=data[side]
            # Evaluate the cheek immediately beyond the exposed eye, across
            # its vertical end ridge. Exclude both eye-floor masks symmetrically.
            mask=(u>.215)&(u<.292)&(abs(v+.105*u)<.044)
            mask&=~(datasets['parent'][side+'_insert']|datasets['A'][side+'_insert'])
            dv,du=np.gradient(h,-.005,.005)
            normal=np.stack([-du,-dv,np.ones_like(du)],axis=-1)
            normal/=np.linalg.norm(normal,axis=2,keepdims=True)
            ang=[]
            for dy,dx in ((0,1),(1,0)):
                shifted=np.roll(normal,(-dy,-dx),axis=(0,1))
                good=mask&np.roll(mask,(-dy,-dx),axis=(0,1))
                ang.extend(np.degrees(np.arccos(np.clip(np.sum(normal*shifted,axis=2)[good],-1,1))))
            stats[side]={'samples':len(ang),'p95_adjacent_normal_turn_degrees':float(np.percentile(ang,95)),
                         'median_adjacent_normal_turn_degrees':float(np.median(ang))}
        path=ASSETS/'render.png' if name=='parent' else D/'wood.png'
        if path.exists():
            foreground=np.asarray(Image.open(path))[:,:,3]>128
            gaps=[]
            for x in range(254,480):
                column=foreground[273:373,x]
                crossings=np.flatnonzero(np.diff(column.astype(int)))
                for i in range(1,len(crossings)-1,2):
                    gaps.append({'x':x,'start_y':int(crossings[i]+274),'length':int(crossings[i+1]-crossings[i])})
            stats['crown_alpha_gaps']=gaps
        result[name]=stats
    (D/'corner-and-crown.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':metrics()

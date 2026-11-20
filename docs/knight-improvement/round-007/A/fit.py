"""Fit a bounded 3D crown displacement to the original and selected contours."""
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;ROOT=D.parents[2];A=ROOT/'assets/knight'
sys.dont_write_bytecode=True
sys.path.insert(0,str(D));sys.path.insert(0,str(ROOT/'scripts/knight'))
from shape import offsets
from mission_pose import posed

def shapes():
    ref=Image.open(A/'ref.png').convert('RGBA')
    q=json.loads((A/'original-alignment.json').read_text());k=q['scale']*300/1254
    sprite=Image.open(A/'original.png').convert('RGBA').transform(ref.size,Image.Transform.AFFINE,
        (k,0,q['x']*3,0,k,q['y']*3),Image.Resampling.BILINEAR)
    return [sprite,ref,Image.open(A/'render.png').convert('RGBA')]

def limits(im,yy,reference=False):
    a=np.asarray(im);fg=a[:,:,3]>127
    if reference:fg&=a[:,:,:3].max(2)>12
    values=[]
    for y in yy:
        r=fg[y];runs=np.flatnonzero(r[:-4]&r[1:-3]&r[2:-2]&r[3:-1]&r[4:])
        values.append([runs.min(),runs.max()+4] if len(runs) else [np.nan,np.nan])
    return np.array(values)

def setup():
    data=np.load(D/'surface.npz')
    v=data['points'];edges=data['edges'];mat=data['matrix'];pose=data['pose']
    rows=np.arange(295,390,2)
    target=np.array([limits(im,rows,i<2) for i,im in enumerate(shapes())])
    with np.errstate(invalid='ignore'):
        goal=np.nanmean(np.stack([target[0],target[1],target[1],target[0],target[1]]),axis=0)
    def project(steps):
        pts=posed(v+steps,*pose)
        return (pts@mat[:2,:3].T+mat[:2,3]+np.array([1.,-1.]))*np.array([627.,-627.])
    base=project(np.zeros_like(v));a,b=base[edges[:,0]],base[edges[:,1]]
    groups=[]
    for row,limits0 in zip(rows,target[2]):
        window=(np.minimum(a[:,1],b[:,1])<row+14)&(np.maximum(a[:,1],b[:,1])>row-14)
        sides=[e for e in (np.minimum(a[:,0],b[:,0])<limits0[0]+52,
                            np.maximum(a[:,0],b[:,0])>limits0[1]-52)]
        groups.append([edges[window&k] for k in sides])
    def trace(pixels):
        pred=[]
        for row,(left,right) in zip(rows,groups):
            side=[]
            for e,func in [(left,np.min),(right,np.max)]:
                a,b=pixels[e[:,0]],pixels[e[:,1]];y=row+.5
                take=(a[:,1]<y)!=(b[:,1]<y)
                if not take.any():
                    side.append(np.nan);continue
                a=a[take];b=b[take];hit=a[:,0]+(b[:,0]-a[:,0])*(y-a[:,1])/(b[:,1]-a[:,1])
                side.append(func(hit))
            pred.append(side)
        return np.asarray(pred)
    base_trace=trace(base)
    def model(q):
        trial=trace(project(offsets(v,q)))
        return trial+(target[2]-base_trace)
    return rows,goal,target,model

def main():
    rows,goal,target,predict=setup()
    start=np.array([.178,.118,4.17,4.35,.012,.046])
    bound=np.array([[.11,.235],[.06,.17],[4.07,4.28],[4.24,4.48],[0,.044],[.009,.085]])
    def score(q):
        pred=predict(q)
        delta=abs(pred-goal)
        delta=np.where(np.isnan(delta),18,delta)
        # Retain the registered lower transition. The two rasters diverge
        # strongly just under their uppermost pixel, so those rows weigh less.
        w=np.where(rows<303,.4,1.)[:,None]
        error=np.mean(w*np.where(delta<5,delta**2/8,1.25*delta-3.125))
        prior=.07*np.mean(((q-start)/np.array([.04,.04,.065,.065,.022,.03]))**2)
        return float(error+prior)
    q=start.copy();cost=score(q)
    for step in [np.array([.02,.012,.042,.04,.009,.012]),np.array([.008,.005,.016,.016,.0035,.005]),np.array([.003,.002,.006,.006,.0015,.002])]:
        for _ in range(7):
            last=cost
            for i in range(len(q)):
                options=[q.copy()]
                for sign in [-1,1]:
                    test=q.copy();test[i]=np.clip(test[i]+sign*step[i],*bound[i]);options.append(test)
                scores=[cost]+[score(z) for z in options[1:]]
                i0=int(np.argmin(scores));q,cost=options[i0],scores[i0]
            if abs(cost-last)<.005:break
    result={'parent_sha256':'1837b02f0c472044a8e86ffd112d15dbe007eb70d9a4330d86f8f073b7440208',
            'parameter_names':['rear_reach','forehead_reach','rear_onset_height','forehead_onset_height','ear_settle','forehead_settle'],
            'q':q.tolist(),'reference_rows':rows.tolist(),'original':target[0].tolist(),'black_2':target[1].tolist(),
            'parent':target[2].tolist(),'predicted':predict(q).tolist(),'bounded_score':cost}
    def finite(x):return [finite(z) for z in x] if isinstance(x,list) else (None if isinstance(x,float) and not np.isfinite(x) else x)
    (D/'fit.json').write_text(json.dumps({k:finite(v) for k,v in result.items()},indent=2)+'\n')
    print(q,cost,'pred',predict(q)[[0,5,10,15,20,25,30]])
if __name__=='__main__':main()

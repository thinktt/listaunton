"""Refine vertical registration with lower-body detail, preserving scale and image pixels."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
data=json.loads((root/'assets/candidates/alignment.json').read_text(encoding='utf-8'))
def read(item):
    a=np.array(Image.open(root/item['file']).convert('RGBA').resize((600,600),Image.Resampling.BILINEAR),dtype=float)/255
    if item['flip']:a=a[:,::-1]
    return a
def sample(g,item,x,y):
    sx=(x-item['x']*3)/item['scale']*2;sy=(y-item['y']*3)/item['scale']*2
    sx=np.clip(sx,0,598.999);sy=np.clip(sy,0,598.999)
    ix=sx.astype(int);iy=sy.astype(int);fx=sx-ix;fy=sy-iy
    top=g[iy[:,None],ix]*(1-fx)+g[iy[:,None],ix+1]*fx
    bot=g[iy[:,None]+1,ix]*(1-fx)+g[iy[:,None]+1,ix+1]*fx
    return (top*(1-fy[:,None])+bot*fy[:,None]).mean(1)
def smooth(p):
    k=np.exp(-np.arange(-12,13)**2/(2*4**2));k/=k.sum()
    return np.convolve(np.pad(p,(12,12),mode='edge'),k,mode='valid')
report=[]
for piece,items in data['pieces'].items():
    originals={i['id']:i for i in items if i['id'] in ['black','white']}
    for item in items:
        if 'candidate' not in item['id']:continue
        # Repeated runs recompute from the saved silhouette placement, not the prior correction.
        item['y']=item.get('silhouette_y',item['y']);item['silhouette_y']=item['y']
        original=originals['white' if item['id'].startswith('white') else 'black']
        target=read(original);source=read(item)
        target_gray=target[:,:,:3].mean(2)*target[:,:,3]
        source_gray=source[:,:,:3].mean(2)*source[:,:,3]
        m=(target[:,:,:3].max(2)>12/255)&(target[:,:,3]>.5);yy,xx=np.where(m)
        left,right=xx.min()/2,xx.max()/2;top,bottom=yy.min()/2,yy.max()/2
        xs=np.linspace(left+(right-left)*.28,left+(right-left)*.72,41)*original['scale']+original['x']*3
        ys=np.arange(top+(bottom-top)*.62,bottom+2,.125)*original['scale']+original['y']*3
        # Smooth gradients tolerate differing exposure while emphasizing ring positions.
        target_g=np.gradient(smooth(sample(target_gray,original,xs,ys)))
        def score(shift):
            g=np.gradient(smooth(sample(source_gray,item,xs,ys-shift)))
            return float(np.dot(g,target_g)/(np.linalg.norm(g)*np.linalg.norm(target_g)+1e-12))
        shifts=np.arange(-4,4.001,.05);scores=np.array([score(d) for d in shifts]);best=int(scores.argmax());dy=float(shifts[best]);before=score(0);after=float(scores[best])
        # Do not move weakly matching or essentially tied candidates.
        applied=dy if after>.65 and after-before>.006 and abs(dy)>=.15 and abs(dy)<3.95 else 0
        item['y']+=applied/3
        item['foot_refinement']={'dy_original_px':round(applied,3),'correlation_before':round(before,5),'correlation_after':round(after if applied else before,5),'reference':original['id']}
        report.append({'piece':piece,'candidate':item['id'],'proposed_px':round(dy,2),**item['foot_refinement']})
        print(piece,item['id'],'shift',round(applied,2),'proposal',round(dy,2),'correlation',round(before,3),'->',round(after,3))
data['method']='Whole-outline uniform scale/translation, followed by bounded vertical refinement against same-color original lower-body ring details. No image warping. White knights mirrored only in aligned view.'
(root/'assets/candidates/alignment.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
(root/'assets/candidates/foot-alignment-report.json').write_text(json.dumps({'method':'Smoothed vertical brightness gradients over the central lower 38% of the piece, fitted to its same-color original; maximum 4 original pixels; weak/tied/boundary fits unchanged.','candidates':report},indent=2),encoding='utf-8')

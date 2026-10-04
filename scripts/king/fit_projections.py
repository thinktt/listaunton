"""Refit copies of the existing king profile at alternative camera elevations.

Original silhouette has the larger source weight. Existing fitted front-ring
arcs preserve internal carving, while the selected reference stabilizes blurred
edges. Feature groups keep flat caps and the small molding cross-sections.
"""
from pathlib import Path
import argparse,copy,json,math
import numpy as np
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args=ap.parse_args()
root=args.root;out=root/'assets/king-projections';out.mkdir(parents=True,exist_ok=True)
base=json.loads((root/'scripts/king/profile.json').read_text());P=np.array(base['profile']);q0=math.sin(math.radians(base['elevation']));n=len(P)
names=['foot','flare','socket','lower collar','middle collar','upper collar','saucer','lower pedestal','upper pedestal','center seat']
representative=np.array([290,287,156,185,167.25,140,171,98,88,0.])
weights=np.zeros((n,len(names)))
def hold(lo,hi,g):weights[lo:hi+1,g]=1
def bridge(lo,hi,a,b):
 for i in range(lo,hi+1):
  t=(i-lo+1)/(hi-lo+2);weights[i,a]=1-t;weights[i,b]=t
hold(0,8,0);hold(9,15,1);bridge(16,20,1,2);hold(21,27,2);bridge(28,34,2,3)
hold(35,44,3);hold(45,52,4);hold(53,60,5);bridge(61,65,5,6);hold(66,70,6)
bridge(71,76,6,7);hold(77,79,7);hold(80,84,8);bridge(85,85,8,9);hold(86,87,9)
assert np.allclose(weights.sum(1),1)
ys=np.arange(112,1101,4,dtype=float)
def smooth_profile(p):
 # One subdivision step in the longitudinal direction, then dense interpolation.
 vertex=(np.roll(p,1,0)+6*p+np.roll(p,-1,0))/8
 vertex[0]=p[0];vertex[-1]=p[-1]
 rows=[]
 for i in range(n-1):rows.extend([vertex[i],(p[i]+p[i+1])/2])
 rows.append(vertex[-1]);rows=np.asarray(rows)
 dense=np.stack([np.interp(np.linspace(0,len(rows)-1,600),np.arange(len(rows)),rows[:,k]) for k in [0,1]],1)
 dense[:,0]*=.99945
 return dense
def envelope(p,q):
 rings=smooth_profile(p);v=rings[:,0,None]**2-((ys[None,:]-rings[:,1,None])/q)**2
 return np.sqrt(np.maximum(v.max(0),0))
def widths(image,threshold=12,alphaonly=False):
 a=np.array(image.convert('RGBA'));mask=a[:,:,3]>128
 if not alphaonly:mask&=a[:,:,:3].max(2)>threshold
 left=mask.argmax(1);right=mask.shape[1]-1-mask[:,::-1].argmax(1);w=(right-left)/2;w[~mask.any(1)]=0
 w=np.convolve(np.pad(w,(3,3),mode='edge'),np.ones(7)/7,'valid')
 return np.interp(ys,np.arange(len(w)),w)
ref=Image.open(root/'assets/king/reference.png');original=Image.open(root/'assets/king/original.png').convert('RGBA')
placement=json.loads((root/'assets/king/original-alignment.json').read_text());s,x,y=[placement[k] for k in ['scale','x','y']]
original=original.transform((1254,1254),Image.Transform.AFFINE,(s*300/1254,0,x*3,0,s*300/1254,y*3),Image.Resampling.BILINEAR)
ow=widths(original);rw=widths(ref);bw=widths(Image.open(root/'assets/king/render.png'),alphaonly=True)
calibration=bw-envelope(P,q0)
features=[8,24,39,49,57,69,77,82]
arc_x=[P[i,0]*np.linspace(-.75,.75,9) for i in features]
arc_y=[P[i,1]+q0*np.sqrt(P[i,0]**2-xs**2) for i,xs in zip(features,arc_x)]

def profile(params,q):
 dy=params[:10];rad=params[10:];p=P.copy()
 p[:,1]+=weights@((q0-q)*representative+dy)
 p[:,0]*=1+weights@rad
 return p
def loss(params,q,details=False):
 p=profile(params,q);pred=envelope(p,q)+calibration
 def huber(v):
  a=np.abs(v);return np.where(a<2,.5*a*a,2*a-2)
 silhouette=.8*np.mean(huber((pred-ow)/4.3))+.2*np.mean(huber((pred-rw)/4.3))
 arc=[]
 for i,xs,target in zip(features,arc_x,arc_y):
  curve=p[i,1]+q*np.sqrt(np.maximum(0,p[i,0]**2-xs**2));arc.extend((curve-target)/4.3)
 internal=np.mean(np.asarray(arc)**2)
 regular=.025*np.mean((params[:10]/12)**2)+.025*np.mean((params[10:]/.05)**2)
 total=silhouette+.9*internal+regular
 if details:return {'loss':float(total),'silhouette_term':float(silhouette),'internal_arc_term':float(internal),'regularization':float(regular)}
 return total

rad_bound=np.array([0,.005,.06,.05,.07,.07,.04,.06,.06,0.])
dy_bound=np.array([10,14,18,14,14,14,14,12,12,0.])
params_bound=np.r_[dy_bound,rad_bound]
results=[]
for angle in [48,52,56,60,64]:
 q=math.sin(math.radians(angle));params=np.zeros(20)
 start=loss(params,q)
 if angle!=52:
  for dy_step,rad_step in [(4,.02),(2,.01),(1,.005),(.5,.0025)]:
   for sweep in range(8):
    improved=False
    for j in range(20):
     if not params_bound[j]:continue
     step=dy_step if j<10 else rad_step;v=loss(params,q);best=params.copy()
     for direction in [-1,1]:
      trial=params.copy();trial[j]=np.clip(trial[j]+direction*step,-params_bound[j],params_bound[j]);score=loss(trial,q)
      if score<v-1e-7:best=trial;v=score;improved=True
     params=best
    if not improved:break
 p=P.copy() if angle==52 else profile(params,q)
 cfg=copy.deepcopy(base);cfg['elevation']=angle;cfg['profile']=p.tolist();cfg['y0']=float(p[0,1])
 cfg['cross']['depth']=base['cross']['depth']*q0/q
 cfg['variant']={'baseline_elevation':52,'method':'Feature-group geometry refit; base width fixed. Original silhouette prioritized; existing fitted front-ring arcs retain details.','parameters':dict(zip(names,[{'dy':float(params[i]),'radius_scale':float(1+params[10+i])} for i in range(10)]))}
 dest=out/f'angle-{angle}';dest.mkdir(exist_ok=True);(dest/'profile.json').write_text(json.dumps(cfg,indent=2)+'\n')
 item={'id':f'angle-{angle}','label':f'{angle}°'+(' · current shape' if angle==52 else ''),'elevation':angle,'assetDir':f'assets/king-projections/angle-{angle}','model':f'models/king-projections/king-{angle}.blend','fit':{'initial_loss':float(start),**loss(params,q,True)}}
 results.append(item);print(angle,item['fit'],flush=True)
(out/'variants.json').write_text(json.dumps({'baseline':'angle-52','description':'Existing king reconstructed under five assumed camera elevations. Original and selected references unchanged. Compare all profiles at identical base width.','variants':results},indent=2)+'\n')

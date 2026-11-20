"""Refit rook feature groups for six camera elevations without changing the original.

The body profile and turret heights change physically. Base diameter, four equal
merlons, slot count, and visible wall-thickness ratio are constrained. The original
sprite drives 80% of outline fitting; the selected reference drives 20%.
"""
from pathlib import Path
import argparse, copy, json, math
import numpy as np
from PIL import Image

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args=ap.parse_args()
root=args.root;out=root/'assets/rook-projections';out.mkdir(parents=True,exist_ok=True)
base=json.loads((root/'scripts/rook/profile.json').read_text(encoding='utf-8'));P=np.array(base['profile']);n=len(P);q0=math.sin(math.radians(54))
names=['foot','base shoulder','collar','neck','lower bowl','notch floor','cavity floor','merlon top']
weights=np.zeros((n,7))
def hold(lo,hi,g):weights[lo:hi+1,g]=1
def bridge(lo,hi,a,b):
 for i in range(lo,hi+1):
  t=(i-lo+1)/(hi-lo+2);weights[i,a]=1-t;weights[i,b]=t
hold(0,12,0);hold(13,16,1);bridge(17,18,1,2);hold(19,30,2);bridge(31,35,2,3);hold(36,40,3);bridge(41,43,3,4);hold(44,46,4);bridge(47,47,4,5);hold(48,53,5);hold(54,58,6)
assert np.allclose(weights.sum(1),1)
representative=np.array([248,250,198,126,177,0,-149.])
ys=np.arange(260,1085,4,dtype=float)
angles=np.concatenate([np.linspace(math.radians(10+k*90),math.radians(80+k*90),72) for k in range(4)])

def smooth_profile(p):
 v=(np.roll(p,1,0)+6*p+np.roll(p,-1,0))/8;v[0]=p[0];v[-1]=p[-1]
 rows=[]
 for i in range(n-1):rows.extend([v[i],(p[i]+p[i+1])/2])
 rows.append(v[-1]);rows=np.asarray(rows)
 dense=np.stack([np.interp(np.linspace(0,len(rows)-1,400),np.arange(len(rows)),rows[:,k]) for k in [0,1]],1);dense[:,0]*=.99965
 return dense

def envelope(p,top,notch,ro,q):
 rings=smooth_profile(p);v=rings[:,0,None]**2-((ys[None,:]-rings[:,1,None])/q)**2
 body=np.sqrt(np.maximum(v.max(0),0))
 dy=-q*ro*np.sin(angles);xx=np.abs(ro*np.cos(angles))
 valid=(ys[:,None]>=top+dy)&(ys[:,None]<=notch+25+dy)
 crown=np.max(np.where(valid,xx,0),axis=1)
 return np.maximum(body,crown)

def widths(image,threshold=8,alphaonly=False):
 a=np.array(image.convert('RGBA'));m=a[:,:,3]>128
 if not alphaonly:m&=a[:,:,:3].max(2)>threshold
 w=(m.shape[1]-1-m[:,::-1].argmax(1)-m.argmax(1))/2;w[~m.any(1)]=0
 w=np.convolve(np.pad(w,(3,3),mode='edge'),np.ones(7)/7,'valid')
 return np.interp(ys,np.arange(len(w)),w)

placement=json.loads((root/'assets/rook/original-alignment.json').read_text(encoding='utf-8'));s,x,y=[placement[k] for k in ['scale','x','y']]
original=Image.open(root/'assets/rook/original.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(s*300/1254,0,x*3,0,s*300/1254,y*3),Image.Resampling.BILINEAR)
ow=widths(original);rw=widths(Image.open(root/'assets/rook/ref.png'))
bw=widths(Image.open(root/'assets/rook/render.png'),alphaonly=True)
calibration=bw-envelope(P,base['turret']['top_y'],base['turret']['notch_y'],177,q0)
features=[8,13,24,30,44]
arc_x=[P[i,0]*np.linspace(-.75,.75,9) for i in features]
arc_y=[P[i,1]+q0*np.sqrt(P[i,0]**2-xs**2) for i,xs in zip(features,arc_x)]

def geometry(params,q):
 p=P.copy();p[:,1]+=weights@((q0-q)*representative+params[:7])
 # Collar and neck radius changes blend through the same connected feature groups.
 p[:,0]*=1+weights[:,2]*params[8]+weights[:,3]*params[9]
 crown=1+params[10];p[44:,0]*=crown
 # Blend crown radius into the neck; do not introduce a shoulder discontinuity.
 p[41:44,0]*=1+np.array([.25,.5,.75])*params[10]
 return p,base['turret']['top_y']+params[7],base['turret']['notch_y']+params[5],177*crown,154*crown

def loss(params,q,details=False):
 p,top,notch,ro,ri=geometry(params,q);pred=envelope(p,top,notch,ro,q)+calibration
 def huber(v):
  a=np.abs(v);return np.where(a<2,.5*a*a,2*a-2)
 silhouette=.8*np.mean(huber((pred-ow)/4.3))+.2*np.mean(huber((pred-rw)/4.3))
 arc=[]
 for i,xs,target in zip(features,arc_x,arc_y):arc.extend((p[i,1]+q*np.sqrt(np.maximum(0,p[i,0]**2-xs**2))-target)/4.3)
 # Both sides of the turret matter: a single ellipse cannot preserve all source
 # arcs when its assumed camera tilt changes. Penalize, rather than conceal, it.
 for frac in [-1,-.7,0,.7,1]:
  arc.append((top+q*ro*frac-(409+q0*177*frac))/5.0)
  arc.append((notch+q*((ro+ri)/2)*frac-(439+q0*165.5*frac))/5.0)
 arc.append((p[56,1]-q*p[56,0]-(462-q0*149))/3.5)
 internal=float(np.mean(np.asarray(arc)**2))
 regular=.035*np.mean((params[:8]/16)**2)+.035*np.mean((params[8:]/.04)**2)
 penalty=max(0,top+14-notch)**2+max(0,notch+8-p[56,1])**2
 total=silhouette+.8*internal+regular+penalty
 if details:return {'loss':float(total),'silhouette_term':float(silhouette),'internal_arc_term':internal,'regularization':float(regular),'structural_penalty':float(penalty)}
 return total

bounds=np.array([18,18,18,20,20,18,18,24,.045,.055,.025]);results=[]
for angle in [48,52,54,56,60,64]:
 q=math.sin(math.radians(angle));params=np.zeros(11);start=loss(params,q)
 if angle!=54:
  for step,rad in [(4,.015),(2,.0075),(1,.003),(0.5,.0015)]:
   for sweep in range(8):
    improved=False
    for j in range(11):
     stride=step if j<8 else rad;score=loss(params,q);best=params.copy()
     for direction in [-1,1]:
      trial=params.copy();trial[j]=np.clip(trial[j]+direction*stride,-bounds[j],bounds[j]);v=loss(trial,q)
      if v<score-1e-7:best=trial;score=v;improved=True
     params=best
    if not improved:break
 p,top,notch,ro,ri=geometry(params,q)
 cfg=copy.deepcopy(base);cfg['elevation']=angle;cfg['profile']=p.tolist();cfg['y0']=float(p[0,1]);cfg['turret'].update(top_y=top,notch_y=notch,outer_radius=ro,inner_radius=ri)
 cfg['variant']={'baseline_elevation':54,'method':'Physical feature-group refit; common base diameter and ground; equal thin merlons. Original dark-wood mask RGB > 8, source weighting 80/20. Existing internal arcs constrain details.','offsets':dict(zip(names,params[:8].tolist())),'radius_adjustments':dict(zip(['collar','neck','crown'],params[8:].tolist()))}
 dest=out/f'angle-{angle}';dest.mkdir(exist_ok=True);(dest/'profile.json').write_text(json.dumps(cfg,indent=2)+'\n')
 item={'id':f'angle-{angle}','label':f'{angle}°'+(' · current shape' if angle==54 else ''),'elevation':angle,'assetDir':f'assets/rook-projections/angle-{angle}','model':f'models/rook-projections/rook-{angle}.blend','fit':{'initial_loss':float(start),**loss(params,q,True)}}
 results.append(item);print(angle,item['fit'],flush=True)
(out/'variants.json').write_text(json.dumps({'baseline':'angle-54','description':'Six actual rook geometry refits at equal base width and floor level. Original sprites remain authoritative; selected black candidate 8 supports details.','variants':results},indent=2)+'\n')

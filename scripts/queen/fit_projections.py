"""Bounded queen geometry refits: original outline first, accepted carving retained."""
from pathlib import Path
import sys,json,math,shutil
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent));from projection_geometry import deform,ring_weights,GROUPS
root=Path(__file__).resolve().parents[2];out=root/'assets/queen-projections';info=json.loads((out/'baseline-info.json').read_text(encoding="utf-8"));points=np.load(out/'baseline-controls.npz')['points'];n=info['ringCount'];N=info['ringSegments'];S=info['scale'];W=1254
registration=json.loads((root/'assets/queen/original-reference-alignment.json').read_text(encoding="utf-8"));t=registration['scale'];dx=registration['offset_x'];dy=registration['offset_y']
alignment={'scale':W/(300*t),'x':-dx/(3*t),'y':-dy/(3*t),'method':'Exact inverse of the preserved original-queen-to-selected uniform registration.'}
(out/'original-alignment.json').write_text(json.dumps(alignment,indent=2)+'\n');shutil.copy2(root/'assets/queen/reference.png',out/'reference.png')
original=Image.open(out/'original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(1/t,0,-dx/t,0,1/t,-dy/t),Image.Resampling.BILINEAR)
ys=np.arange(20,1120,4,dtype=float)
def widths(im,alpha=False):
 a=np.asarray(im.convert('RGBA'));m=a[:,:,3]>128
 if not alpha:m&=a[:,:,:3].max(2)>12
 l=m.argmax(1);r=m.shape[1]-1-m[:,::-1].argmax(1);v=(r-l)/2;v[~m.any(1)]=0
 v=np.convolve(np.pad(v,(3,3),mode='edge'),np.ones(7)/7,'valid');return np.interp(ys,np.arange(len(v)),v)
ow=widths(original);rw=widths(Image.open(out/'reference.png'));bw=widths(Image.open(root/'history/queen-before-54-finish/assets/queen/queen-matched.png'),True)
def rings(p):
 a=p.reshape((n,N,3));r=np.linalg.norm(a[:,:,:2],axis=2).mean(1)*S;z=a[:,:,2].mean(1);return np.c_[r,z]
def envelope(p,yfloor,angle):
 a=rings(p);a[:,1]=yfloor-S*math.cos(math.radians(angle))*a[:,1]
 smooth=(np.roll(a,1,axis=0)+6*a+np.roll(a,-1,axis=0))/8;smooth[0]=a[0];smooth[-1]=a[-1]
 dense=np.c_[np.interp(np.linspace(0,n-1,650),np.arange(n),smooth[:,0]),np.interp(np.linspace(0,n-1,650),np.arange(n),smooth[:,1])]
 v=dense[:,0,None]**2-((ys[None,:]-dense[:,1,None])/math.sin(math.radians(angle)))**2
 return np.sqrt(np.maximum(v.max(0),0))
baseline,ybase=deform(points,info,51.5,np.zeros(10));calibration=bw-envelope(baseline,ybase,51.5)
features=[11,16,32,55,69,80,info['finialFirstRing']];br=rings(baseline);xs=[br[i,0]*np.linspace(-.65,.65,7) for i in features]
arc=[ybase-S*math.cos(math.radians(51.5))*br[i,1]+math.sin(math.radians(51.5))*np.sqrt(br[i,0]**2-x**2) for i,x in zip(features,xs)]
def loss(params,angle,detail=False):
 p,yfloor=deform(points,info,angle,params);pred=envelope(p,yfloor,angle)+calibration
 def huber(x):a=np.abs(x);return np.where(a<2,.5*a*a,2*a-2)
 silhouette=.8*np.mean(huber((pred-ow)/4.2182))+.2*np.mean(huber((pred-rw)/4.2182));pr=rings(p);err=[]
 for i,x,target in zip(features,xs,arc):
  current=yfloor-S*math.cos(math.radians(angle))*pr[i,1]+math.sin(math.radians(angle))*np.sqrt(np.maximum(0,pr[i,0]**2-x*x));err.extend((current-target)/4.2182)
 internal=float(np.mean(np.asarray(err)**2));regular=.12*np.mean((params[:5]/10)**2)+.12*np.mean((params[5:]/.025)**2);total=silhouette+1.2*internal+regular
 return {'loss':float(total),'silhouette':float(silhouette),'preserved_arc_term':internal,'regularization':float(regular)} if detail else total
bound=np.array([0,15,13,12,10,0,.025,.03,.015,.02]);rows=[]
for angle in [48,51.5,52,54,56,60,64]:
 params=np.zeros(10);initial=loss(params,angle)
 if angle!=51.5:
  for ds,rs in [(4,.01),(2,.005),(1,.0025),(.5,.00125)]:
   for sweep in range(5):
    improved=False
    for j in range(10):
     if bound[j]==0:continue
     value=loss(params,angle);best=params.copy();step=ds if j<5 else rs
     for sign in [-1,1]:
      trial=params.copy();trial[j]=np.clip(trial[j]+sign*step,-bound[j],bound[j]);score=loss(trial,angle)
      if score<value-1e-7:value=score;best=trial;improved=True
     params=best
    if not improved:break
 ident='angle-'+str(angle).replace('.','-');folder=out/ident;folder.mkdir(exist_ok=True);p,yfloor=deform(points,info,angle,params)
 cfg={'elevation':angle,'parameters':params.tolist(),'sourceSha256':info['sourceSha256'],'yfloor':float(yfloor),'scale':S,'cx':info['cx'],'subdivision':1,'method':'Feature-group physical geometry refit. Fixed base radius and floor; bounded radius adjustments preserve accepted chunky carving. Original outline weight 0.8, selected outline 0.2; baseline front-ring arcs constrain internal details.'}
 (folder/'fit.json').write_text(json.dumps(cfg,indent=2)+'\n')
 row={'id':ident,'label':str(angle)+'°'+(' · current shape' if angle==51.5 else ''),'elevation':angle,'assetDir':'assets/queen-projections/'+ident,'model':'models/queen-projections/queen-'+str(angle).replace('.','-')+'.blend','fit':{'initial_loss':float(initial),**loss(params,angle,True)}};rows.append(row);print(angle,row['fit'],flush=True)
(out/'variants.json').write_text(json.dumps({'baseline':'angle-51-5','description':'Physical queen geometry refits at seven assumed camera elevations; 51.5-degree accepted shape retained as baseline. Same base width, floor, profile camera and orbit frame.','variants':rows,'sharedView':{'center':[0,0,2.9],'orthoHeight':6.2,'distance':16}},indent=2)+'\n')

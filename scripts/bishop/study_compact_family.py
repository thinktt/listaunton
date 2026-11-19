"""Measure fixed-camera outline effects of lower-turning compression."""
from pathlib import Path
import json,math,sys
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent))
from fit_side_refit import smooth_meridian
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/bishop-mission/iteration-031';DOC.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'history/bishop-mission-030'
p=json.loads((BASE/'profile.json').read_text())
al=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
f=1254/300/al['scale']/p['scale'];c=math.cos(math.radians(54))
def decode(a):
    a=np.array(a);return np.column_stack((a[:,0]*f,(p['y0']-a[:,1])*f/c))
body=decode(p['profile']);cap=decode(p['finial']['profile'])
camera=json.loads((BASE/'camera.json').read_text())
m=np.array(camera['projectionMatrix']).reshape(4,4)@np.array(camera['worldToCamera']).reshape(4,4)
oy=(1-m[1,3])*627; xr=m[0,0]*627; yd=m[1,1]*627; yz=m[1,2]*627
s=al['scale']*300/1254
im=Image.open(ROOT/'assets/bishop/original.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(s,0,al['x']*3,0,s,al['y']*3),Image.Resampling.BILINEAR)
a=np.array(im);ref=(a[:,:,3]>127)&(a[:,:,:3].max(2)>12)
refwidth=(np.argmax(ref[:,::-1],axis=1)*-1+1254-np.argmax(ref,axis=1))/2
refwidth[~ref.any(1)]=0
actual=np.asarray(Image.open(BASE/'render.png').convert('RGBA'))[:,:,3]>127
aw=(1254-np.argmax(actual,axis=1)-np.argmax(actual[:,::-1],axis=1))/2
aw[~actual.any(1)]=0
ys=np.arange(145,1118,3)
def widths(b,k):
    pts=np.vstack((smooth_meridian(b),smooth_meridian(k)))
    r,z=pts.T
    q=(ys[:,None]+.5-oy+yz*z)/np.maximum(r*yd,1e-8)
    return np.sqrt(np.maximum(1-q*q,0.)*(r*xr)**2).max(1)
bias=aw[ys]-widths(body,cap)
def changed(v):
    compress,bulge,collar_drop,collar_radius,head_drop,button_radius,button_flat=v
    b=body.copy();k=cap.copy()
    low=body[:,1]<1.49
    t=np.clip((body[low,1]-.35)/1.13,0,1)
    b[low,1]-=compress*1.13*t
    # Width lives mainly in the inner flare, leaving the foot diameter exact.
    b[low,0]+=bulge*np.exp(-((body[low,1]-.78)/.30)**2)*np.clip((body[low,1]-.34)/.15,0,1)
    # Join the shorter socket to the collar stack with a smooth stem taper.
    stem=(body[:,1]>=1.49)&(np.arange(len(body))<40)
    t=np.clip((body[stem,1]-1.49)/(2.79-1.49),0,1)
    b[stem,1]-=compress*1.13*(1-t)
    upper=np.arange(59,66)
    b[upper,1]-=collar_drop;b[upper,0]*=collar_radius
    # Blend the lower mitre into its lowered collar; keep the saw in place.
    blend=np.arange(66,76)
    w=np.linspace(1,0,len(blend))
    b[blend,1]-=head_drop+(collar_drop-head_drop)*w
    b[76:,1]-=head_drop
    k[:,1]-=head_drop;k[:,0]*=button_radius
    # Small cap shaping is permitted by the original bright button contour.
    t=np.clip((cap[:,1]-4.51)/.082,0,1)
    k[:,1]-=button_flat*t
    return b,k
for y in [150,159,165,175,185,195,205,215,225,235,245,255,265]:
    print('button row',y,'original half width',refwidth[y],'model',aw[y])
cases={'current':[0,0,0,1,0,1,0],
 'compress':[.10,.022,.035,.96,.113,1,0],
 'hold_head':[.10,.022,.035,.96,0,1,0],
 'moderate':[.10,.022,.035,.96,.035,1.03,.02]}
report={}
for key,v in cases.items():
    b,k=changed(v);w=widths(b,k)+bias
    report[key]={'parameters':v,'predicted_height':float(max(b[:,1].max(),k[:,1].max())),
                 'regions':{name:float(np.mean(abs(w[(ys>=lo)&(ys<hi)]-refwidth[ys[(ys>=lo)&(ys<hi)]])))
                            for name,lo,hi in [('button',150,245),('head',245,480),('collars',480,615),('stem',615,705),('base',705,1118)]}}
(DOC/'initial-projection-study.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
print('projection',oy,xr,yd,yz);print(json.dumps(report,indent=2))

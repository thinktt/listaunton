"""Bounded 52-degree refit; fixed images, independent physical radius groups."""
from pathlib import Path
import json, math
import numpy as np
from PIL import Image
from scipy.optimize import least_squares
R=Path(__file__).resolve().parent;A=R/'assets/queen'
info=json.loads((R/'build/queen-mission/control-profile.json').read_text());base=np.array([[x['r'],x['z']] for x in info]);n=len(base)
fit=json.loads((A/'finish-fit.json').read_text());S=fit['camera_scale'];y0=fit['camera_floor'];angle=52;el=math.radians(angle);old=math.radians(54)
reg=json.loads((A/'original-reference-alignment.json').read_text());t,x,y=reg['scale'],reg['offset_x'],reg['offset_y']
original=Image.open(R/'references/lichess-staunton-3d/Black-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/t,0,-x/t,0,1/t,-y/t),Image.Resampling.BILINEAR)
ys=np.arange(45,1080,3)
def widths(im,ref=False):
    a=np.asarray(im.convert('RGBA'));m=a[:,:,3]>127
    if ref:m&=a[:,:,:3].max(2)>12
    v=(m.shape[1]-1-m[:,::-1].argmax(1)-m.argmax(1))/2;v[~m.any(1)]=0
    return np.interp(ys,np.arange(1254),v)
target=widths(original,True);hi=widths(Image.open(A/'reference.png'),True);trial=widths(Image.open(R/'build/queen-mission/186-angle-52/wood.png'))
# Smooth overlapping radius groups, leaving the tiny pole/caps and finial alone.
anchors=[0,17,29,45,55,67,78,88,94,106,116]
weights=np.array([np.interp(np.arange(n),anchors,np.eye(len(anchors))[j]) for j in range(1,9)]).T
tt=np.linspace(0,1,10,endpoint=False);B=np.stack([(1-tt)**3,3*tt**3-6*tt*tt+4,-3*tt**3+3*tt*tt+3*tt+1,tt**3],axis=1)/6
def parameters(p):return base[:,0]+weights@p[2:],base[:,1]*(.954721+p[1]),y0+(math.sin(old)-math.sin(el))*1.03671*S+p[0]
def envelope(p):
    rr,zz,yy=parameters(p);dense=np.concatenate([B@np.c_[rr,zz][i:i+4] for i in range(n-3)])
    rad=dense[:,0,None]*S;cy=yy-S*math.cos(el)*dense[:,1,None]
    return np.sqrt(np.maximum((rad*rad-((ys[None,:]-cy)/math.sin(el))**2).max(0),0))
zero=np.zeros(10);cal=trial-envelope(zero)
features=[11,32,38,55,67,78,94,110]
front=y0-S*math.cos(old)*base[features,1]+S*math.sin(old)*base[features,0]
def residual(p):
    rr,zz,yy=parameters(p);pred=envelope(p)+cal
    now=yy-S*math.cos(el)*zz[features]+S*math.sin(el)*rr[features]
    return np.r_[.9*(pred-target)/3,.3*(pred-hi)/3,.7*(now-front)/4,p[0]/15,p[1]/.04,p[2:]/.03]
bound=np.r_[12,.035,.012,.035,.025,.015,.015,.015,.02,.012]
opt=least_squares(residual,zero,bounds=(-bound,bound),diff_step=1e-3,max_nfev=160)
p=opt.x;rr,zz,yy=parameters(p)
cfg={'variant':'187-refitted-52','hypothesis':'52-degree camera with bounded physical radius groups and axial-height refit, constrained to original silhouette and accepted front-ring arcs. Original weight exceeds generated detail reference.','elevation':52,'axial_scale':float(.954721+p[1]),'camera_floor_offset':float(p[0]),'radii':{str(i):float(v) for i,v in enumerate(rr) if abs(v-base[i,0])>1e-7},'fit':{'initial_residual':float(np.mean(residual(zero)**2)),'fitted_residual':float(np.mean(residual(p)**2)),'parameters':p.tolist(),'success':bool(opt.success),'note':'Calibrated ring approximation; actual rendered comparisons decide acceptance.'}}
(R/'187-refitted-52.json').write_text(json.dumps(cfg,indent=2)+'\n');print(json.dumps(cfg['fit'],indent=2))

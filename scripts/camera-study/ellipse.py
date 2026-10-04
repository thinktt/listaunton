"""Ellipse fits and shared-angle residual profiles; distances in source pixels."""
import numpy as np,math

def residual(points,v,q=None):
 p=np.asarray(points);cx,cy,rx=v[:3];ry=v[3] if q is None else q*rx
 dx=p[:,0]-cx;dy=p[:,1]-cy
 f=dx*dx/rx**2+dy*dy/ry**2-1
 n=np.sqrt((2*dx/rx**2)**2+(2*dy/ry**2)**2)
 return f/np.maximum(n,1e-8)

def fit(points,theta=None,initial=None):
 p=np.asarray(points,dtype=float);q=None if theta is None else math.sin(math.radians(theta))
 if initial is None:
  origin=p.mean(0);d=p-origin
  a,b,c,e=np.linalg.lstsq(np.c_[d[:,0]**2,d[:,1]**2,d[:,0],d[:,1]],np.ones(len(d)),rcond=None)[0]
  if a<=0 or b<=0:raise ValueError('Not ellipse')
  h=-c/(2*a);k=-e/(2*b);norm=1+a*h*h+b*k*k
  initial=[origin[0]+h,origin[1]+k,math.sqrt(norm/a),math.sqrt(norm/b)]
 v=np.asarray(initial[:4] if q is None else initial[:3],float).copy()
 for _ in range(35):
  r=residual(p,v,q);jac=np.column_stack([(residual(p,v+np.eye(len(v))[i]*.001,q)-r)/.001 for i in range(len(v))])
  step=np.linalg.lstsq(jac,-r,rcond=None)[0]
  if np.linalg.norm(step)<1e-7:break
  fraction=1.
  while fraction>1e-4:
   n=v+step*fraction
   if n[2]>0 and (q is not None or n[3]>0) and np.mean(residual(p,n,q)**2)<np.mean(r*r):v=n;break
   fraction*=.5
  else:break
 cx,cy,rx=v[:3];ry=v[3] if q is None else q*rx;ratio=ry/rx
 if not 0<ratio<1:raise ValueError('Ratio outside circular interpretation')
 return dict(cx=float(cx),cy=float(cy),rx=float(rx),ry=float(ry),q=float(ratio),elevation_degrees=math.degrees(math.asin(ratio)),rms_px=float(np.sqrt(np.mean(residual(p,v,q)**2))))

def sensitivity(points,trials=1000,sigma=.75):
 rng=np.random.default_rng(4102026);angles=[]
 for _ in range(trials):
  try:angles.append(fit(np.asarray(points)+rng.normal(0,sigma,np.asarray(points).shape))['elevation_degrees'])
  except (ValueError,np.linalg.LinAlgError):pass
 return dict(trials=trials,valid=len(angles),sigma_px=sigma,p05_median_p95=np.percentile(angles,[5,50,95]).tolist())

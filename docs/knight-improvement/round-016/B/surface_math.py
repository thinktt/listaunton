import numpy as np
def raster(t,w,h):
    lo=np.maximum(np.floor(t.min(0)).astype(int),0);hi=np.minimum(np.ceil(t.max(0)).astype(int),[w-1,h-1])
    if (hi<lo).any():return
    a,b=t[1]-t[0],t[2]-t[0];det=a[0]*b[1]-a[1]*b[0]
    if abs(det)<1.e-9:return
    y,x=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];qx=x+.5-t[0,0];qy=y+.5-t[0,1]
    u=(qx*b[1]-qy*b[0])/det;v=(a[0]*qy-a[1]*qx)/det
    valid=(u>=-1.e-6)&(v>=-1.e-6)&(u+v<=1.000001)
    if valid.any():return y[valid],x[valid],np.stack([1-u[valid]-v[valid],u[valid],v[valid]],1)

def sample(a,x,y,wrap=False):
    x=np.mod(x,a.shape[1]) if wrap else np.clip(x,0,a.shape[1]-1.0001)
    y=np.clip(y,0,a.shape[0]-1.0001);i=x.astype(int);j=y.astype(int)
    k=(i+1)%a.shape[1];s=(x-i)[...,None];t=(y-j)[...,None]
    return (1-t)*((1-s)*a[j,i]+s*a[j,k])+t*((1-s)*a[j+1,i]+s*a[j+1,k])

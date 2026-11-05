"""Small NumPy image helpers shared by ordinary Python and Blender."""
import numpy as np

def blur(a,r=3,passes=3):
    a=a.astype(np.float64)
    for _ in range(passes):
        for axis in (0,1):
            pad=[(0,0)]*a.ndim;pad[axis]=(r,r);b=np.pad(a,pad,mode='edge')
            zero_shape=list(b.shape);zero_shape[axis]=1
            c=np.concatenate([np.zeros(zero_shape),np.cumsum(b,axis=axis)],axis=axis)
            hi=[slice(None)]*a.ndim;lo=hi.copy();hi[axis]=slice(2*r+1,None);lo[axis]=slice(None,-(2*r+1))
            a=(c[tuple(hi)]-c[tuple(lo)])/(2*r+1)
    return a.astype(np.float32)

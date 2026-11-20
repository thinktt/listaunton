"""Small NumPy filters used by material diagnostics, independent of SciPy."""
import numpy as np

def blur(a, radius=2, passes=1):
    result=np.asarray(a,dtype=np.float32)
    for _ in range(passes):
        for axis in (0,1):
            pad=[(0,0)]*result.ndim;pad[axis]=(radius,radius)
            padded=np.pad(result,pad,mode='edge')
            zero_shape=list(padded.shape);zero_shape[axis]=1
            sums=np.concatenate([np.zeros(zero_shape),np.cumsum(padded,axis=axis,dtype=np.float64)],axis=axis)
            hi=[slice(None)]*result.ndim;lo=hi.copy()
            hi[axis]=slice(2*radius+1,None);lo[axis]=slice(None,-2*radius-1)
            result=((sums[tuple(hi)]-sums[tuple(lo)])/(2*radius+1)).astype(np.float32)
    return result

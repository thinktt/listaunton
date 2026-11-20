from pathlib import Path
import numpy as np
D=Path(__file__).resolve().parent
d=np.load(D/'eyes-parent.npz')
for u in np.arange(-.22,.30,.025):
    j=np.argmin(abs(d['u'][0]-u))
    e=d['near_insert'][:,j]
    if e.any():
        v=d['v'][e,j];y=d['near'][e,j]
        print('u',round(u,3),'limits',np.round([v.min(),v.max()],3),'peak',round(v[y.argmax()],3),'center',round(y.mean(),3))

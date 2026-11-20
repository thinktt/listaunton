from pathlib import Path
import json,sys
import numpy as np
D=Path(__file__).resolve().parent
ax=np.array([1.,-.76])/np.hypot(1.,.76);up=np.array([-ax[1],ax[0]])
f=np.array(json.loads((D/'aperture-curve.json').read_text())['curve'])
t=np.deg2rad(10.3);basis=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]])
for name,rows in json.loads((D/f'card-rays-{sys.argv[1]}.json').read_text()).items():
    for x,y,pt,dr in rows:
        xy=(np.array(pt[:2])-[-.313,-.045])@basis
        z=np.array([xy[0],pt[2]])-[.412,4.158]
        u,v=z@ax,z@up
        hi=np.interp(u,f[:,0],f[:,2]);lo=np.interp(u,f[:,0],f[:,1])
        print(name,x,y,round(u,3),round(v,3),'native h',round((v-lo)/(hi-lo),2))

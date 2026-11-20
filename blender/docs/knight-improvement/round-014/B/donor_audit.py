"""Measure donor coverage and the physical extent of the actual alteration."""
from pathlib import Path
import json,sys
import numpy as np
from surface import W,H,Z0,Z1
from restore import PARAMS,ease
D=Path(__file__).resolve().parent
def audit(i):
    a=dict(np.load(D/'surface-field.npz'));d=dict(np.load(D/'neck-donor.npz'))
    radius=a['depth'];y,x=np.indices((H,W));t=(x+.5-W/2)/(W/2)*np.pi;z=Z1-(y+.5)*(Z1-Z0)/H
    sigma=abs(t);gate=ease((sigma-.37)/.71)*(1-ease((sigma-2.13)/.74))*ease((z-1.93)/.53)*(1-ease((z-4.35)/.36))
    scale,k,_=PARAMS[i][6:9];lat=abs(np.sin(t))*radius;fore=-np.cos(t)*radius
    bx=-.408+scale*(fore+.09)+.052*np.sin(3.4*z+2*fore)+np.where(t<0,0.,.08)
    bz=3.09+.76*(z-3.30)-k*(lat-.30)+.18*fore+np.where(t<0,0.,.13)
    uv=d['uv'][1];valid=np.isfinite(uv[:,:,0]);spacing=d['spacing']
    rows=[]
    coords=[(bx,bz)]
    if len(PARAMS[i])>9:coords.append((bx+.084+.20*(lat-.30)+.062*(z-3.26),bz+.104+.12*fore+.035*np.sin(2.7*z)))
    for px,pz in coords:
        xx=np.rint((px-d['x_min'])/spacing).astype(int);yy=np.rint((pz-d['z_min'])/spacing).astype(int)
        inside=(xx>=0)&(xx<valid.shape[1])&(yy>=0)&(yy<valid.shape[0])
        measured=inside&valid[np.clip(yy,0,valid.shape[0]-1),np.clip(xx,0,valid.shape[1]-1)]
        rows.append({'fraction_at_gate_above_point_two':round(float(measured[gate>.2].mean()),6),
                     'fraction_at_gate_above_point_five':round(float(measured[gate>.5].mean()),6)})
    return rows
if __name__=='__main__':
    for k in sys.argv[1:]:print(k,audit(int(k)))

"""Form smooth rest-frame lid coordinates from actual side-ray intersections."""
from pathlib import Path
import json
import numpy as np
D=Path(__file__).resolve().parent
def main():
    d=np.load(D/'eyes-parent.npz')
    u=d['u'][0];v=d['v'][:,0];mask=d['near_insert']&d['far_insert']
    raw=[]
    for i,x in enumerate(u):
        if mask[:,i].any():
            ys=v[mask[:,i]];raw.append([x,ys.min(),ys.max()])
    raw=np.array(raw)
    fits=[]
    for x in np.arange(-.212,.293,.009):
        w=np.exp(-((raw[:,0]-x)/.016)**2);w/=w.sum()
        fits.append([round(float(x),6),*list(w@raw[:,1:])])
    (D/'aperture-curve.json').write_text(json.dumps({'curve':fits,'note':'Blur of the physical lower/upper boundaries from paired, unposed side rays; coordinates in model units.'},indent=2)+'\n')
if __name__=='__main__':main()

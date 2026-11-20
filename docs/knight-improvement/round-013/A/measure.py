"""Brow, inner-eye and lower reflection profiles in the inherited registration."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageFilter
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parents[2]/'scripts/knight'))
from audit_mission import registered,black
def measure():
    refs=registered();full='--full' in sys.argv
    inputs={'Original':(refs['original'],0,0),'Black 2':(refs['selected'],0,0)}
    for face,name in [('12B','parent'),('13A','knight')]:
        p='parent-wood.png' if name=='parent' else 'wood.png'
        inputs[face]=(Image.open(D/p),0,0) if full else (Image.open(D/('detail-'+name+'-wood-fixed.png')),416,418)
    brow=np.array(json.loads((D/'source-anchors.json').read_bytes())['anchor_points']);out={}
    cheval=np.array([(457,481),(466,485),(477,491),(487,496),(497,499),(509,500),(519,501),(529,500),(540,499),(549,497)])
    def profile(a,points,rad,dx,dy,x):
        ctr=np.rint(np.interp(x,points[:,0],points[:,1])).astype(int)
        return a[ctr[None,:]-dy+rad[:,None],x[None,:]-dx]
    for face,(im,dx,dy) in inputs.items():
        photo=black(im.convert('RGBA'))
        def blur(k):return np.asarray(photo.filter(ImageFilter.GaussianBlur(k)),float)@[.2126,.7152,.0722]
        x=np.arange(459,548);rad=np.arange(-11,14);v=profile(blur(1.8),cheval,rad,dx,dy,x)
        peak=np.max(v[(rad>=-5)&(rad<=6)],axis=0);bg=np.median(v[(rad>=9)&(rad<=13)],axis=0)
        prominence=np.maximum(0.,peak-bg);s=np.convolve(np.pad(prominence,(2,2),mode='edge'),np.ones(5)/5,'valid');weights=s/max(1e-8,s.sum());actual=x[np.minimum(len(x)-1,np.searchsorted(np.cumsum(weights),[.1,.5,.9]))]
        bm={};xr=np.arange(459,581);z=np.arange(-12,13);b=profile(blur(1.4),brow,z,dx,dy,xr)
        for label,lo,hi in [('rear',467,492),('mid',493,521),('corner',530,547),('bridge',550,576)]:
            prof=np.median(b[:,(xr>=lo)&(xr<=hi)],axis=1);bm[label]={'minimum_offset':int(z[prof.argmin()]),'on_fold':round(float(prof[12]),1),'upper_minus_fold':round(float(prof[4:8].mean()-prof[12]),1),'lower_minus_fold':round(float(prof[17:21].mean()-prof[12]),1)}
        out[face]={'lower_glint_percentiles':actual.tolist(),'lower_glint_length':int(actual[2]-actual[0]),'lower_glint_peak_contrast':round(float(s.max()),1),'brow':bm}
    (D/('fixed-measures.json' if full else 'preview-measures.json')).write_text(json.dumps(out,indent=2)+'\n')
    print({k:(v['lower_glint_percentiles'],v['lower_glint_peak_contrast'],v['brow']['bridge']) for k,v in out.items()})
if __name__=='__main__':measure()

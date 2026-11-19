"""Fit modest turning adjustments on 024 with fixed floor, widest foot, camera and slit."""
import json

import numpy as np
from PIL import Image

from compare_shared_turning import sprite
from fit_short_reference import BASE,DOC,OUT,ROOT,Projection,read
from fit_side_refit import half_widths,smooth_meridian

# Each displacement is zero at both ends. These bands exclude the widest
# sole wall, direct head/button contact and lower socket receiver boundary.
BANDS=[('groove',7,10,13),('rear_base',10,15,23),('shoulder',15,20,24),
       ('stem',32,35,39),('lower_collar',39,45,49),('middle_collar',49,53,58),
       ('upper_collar',58,62,65),('mitre_flank',65,77,96),('upper_mitre',78,90,101)]


def bump(lo,peak,hi,n):
    i=np.arange(n)
    t=np.clip((i-lo)/(peak-lo),0,1)*np.clip((hi-i)/(hi-peak),0,1)
    return t*t*(3-2*t)


class TurningFit:
    def __init__(self):
        self.f=Projection()
        p=self.f.s
        ary=np.array(p['profile'])
        self.old=np.stack((ary[:,0]*self.f.fac,(p['y0']-ary[:,1])*self.f.fac/self.f.cos),axis=1)
        self.basis=np.array([bump(lo,pk,hi,len(ary)) for _,lo,pk,hi in BANDS]).T
        self.yy=np.arange(213,1114,5)
        self.src=read(ROOT/'docs/bishop-mission/iteration-025/measurements.json')['bishop']
        self.target=[]
        for im in (sprite(),Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA')):
            a=np.asarray(im);mask=(a[:,:,3]>127)&(a[:,:,:3].max(2)>12)
            self.target.append(half_widths(mask)[self.yy])
        full=np.asarray(Image.open(BASE/'render-clay.png').convert('RGBA'))[:,:,3]>127
        self.baseline=half_widths(full)[self.yy]
        raw,rims,groove=self.project(self.old)
        self.bias=self.baseline-raw
        self.rim_bias=np.array(list(self.src['front_collar_rim_rows'].values()))-rims
        self.groove_bias=self.src['front_groove_row']-groove
        self.desired=np.array([515.,567.,611.,1053.])
        self.start=np.zeros(2*len(BANDS))

    def project(self,controls):
        b=smooth_meridian(controls);r,z=b.T
        normalized=(self.yy[None,:]+.5-self.f.cy+self.f.zy*z[:,None])/np.maximum(self.f.yr*r[:,None],1e-7)
        half=self.f.xr*np.sqrt(np.max(np.maximum(1-normalized**2,0)*(r[:,None]**2),axis=0))
        front=self.f.cy-self.f.zy*z+self.f.yr*r
        rims=np.array([front[a*6:b*6].max() for a,b in [(59,65),(50,57),(41,48)]])
        band=b[9*6:12*6];gr,gz=band[band[:,0].argmin()]
        return half,rims,self.f.cy-self.f.zy*gz+self.f.yr*gr

    def predict(self,v):
        controls=self.old+self.basis@v.reshape(-1,2)
        width,rims,groove=self.project(controls)
        ww=width+self.bias
        errors=tuple(np.abs(ww-q) for q in self.target)
        marks=np.r_[rims+self.rim_bias,groove+self.groove_bias]
        return controls,errors,marks

    def loss(self,v):
        controls,errors,marks=self.predict(v)
        if controls[11:23,0].max()>=self.old[:,0].max()-.003:return 1e3
        # Balance anatomy across bands, rather than letting the numerous
        # nearly identical pixels at the base pay for a displaced head.
        intervals=[(214,400),(400,593),(593,630),(630,790),(790,1060),(1060,1114)]
        geom=np.mean([np.mean(e[(self.yy>=lo)&(self.yy<hi)])*weight for e,weight in zip(errors,[1.5,.5]) for lo,hi in intervals])
        delta=np.abs(marks-self.desired)
        return geom+.32*delta[:3].mean()+.1*delta[3]+3.8*np.mean(np.abs(v))

    def solve(self):
        v=self.start.copy();cost=self.loss(v)
        limits=np.array([[.024,.036],[.024,.028],[.028,.03],[.012,.016],
                         [.018,.029],[.017,.029],[.017,.032],[.016,.020],[.014,.017]]).ravel()
        for step in [.4,.2,.1,.05,.025]:
            for _ in range(5):
                changed=False
                for j in range(len(v)):
                    for s in (-1,1):
                        w=v.copy();w[j]=np.clip(w[j]+s*step*limits[j],-limits[j],limits[j])
                        new=self.loss(w)
                        if new<cost-1e-6:v,cost,changed=w,new,True
                if not changed:break
        controls,_,marks=self.predict(v)
        return v,controls,marks


def main():
    t=TurningFit();v,rz,marks=t.solve()
    s=t.f.s
    body={str(i):[float(r/t.f.fac),float(s['y0']-z*t.f.cos/t.f.fac)] for i,(r,z) in enumerate(rz) if np.any(abs(rz[i]-t.old[i])>1e-9)}
    for base,name in [('medium','turned-medium'),('low','turned-low')]:
        config=read(OUT/(base+'.json'))
        config.update(variant='185-'+name,body_rings=body)
        (OUT/(name+'.json')).write_text(json.dumps(config,indent=2)+'\n')
    (DOC/'turning-proposals.json').write_text(json.dumps({'control_order':[x[0] for x in BANDS],
        'radial_and_axial_offsets':v.reshape(-1,2).tolist(),'original_optical_rows':t.desired.tolist(),
        'restored_024_real_rims_and_groove':list(t.src['front_collar_rim_rows'].values())+[t.src['front_groove_row']],
        'predicted_trial_rims_and_groove':marks.tolist(),'body_rings':body,
        'fixed_controls':'foot through row 7, button join and the physically open saw'},indent=2)+'\n')
    print('Predicted collar and groove rows',marks,'changed rings',len(body),flush=True)


if __name__=='__main__':main()

"""Fit a lower, round, centered finial to both original button arcs at the saved camera."""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from compare_shared_turning import sprite
from fit_side_refit import smooth_meridian

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'history/bishop-mission-024'
DOC=ROOT/'docs/bishop-mission/iteration-029'
OUT=ROOT/'build/bishop-mission/185-reference-first'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
source=BASE/'bishop-rebuilt.blend'
SOURCE_SHA='2ac4f898f5c5a8b6f69edec478e8d380d23c4c3021122697b0a2973878a2b425'


def first_row(mask,columns):
    return np.where(mask[:,columns].any(0),mask[:,columns].argmax(0),np.nan)


class Projection:
    def __init__(self):
        assert sha(source)==SOURCE_SHA
        s=read(BASE/'profile.json')
        camera=read(BASE/'camera.json')
        m=np.array(camera['projectionMatrix']).reshape(4,4)@np.array(camera['worldToCamera']).reshape(4,4)
        self.cx=(1+m[0,3])*627;self.cy=(1-m[1,3])*627
        self.xr=627*m[0,0];self.yr=627*m[1,1];self.zy=627*m[1,2]
        self.fac=1254/300/read(ROOT/'assets/bishop/original-alignment.json')['scale']/s['scale']
        self.cos=math.cos(math.radians(camera['elevationDegrees']))
        self.s=s
        rz=np.array(s['finial']['profile'])
        self.rz=np.stack((rz[:,0]*self.fac,(s['y0']-rz[:,1])*self.fac/self.cos),axis=1)
        self.x=np.arange(433,552,2)
        self.r=(self.x+.5-self.cx)/self.xr
        orig=np.asarray(sprite());hi=np.asarray(Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA'))
        mask=lambda a:(a[:,:,3]>127)&(a[:,:,:3].max(2)>12)
        self.target=first_row(mask(orig),self.x)
        self.selected=first_row(mask(hi),self.x)
        measured=read(ROOT/'docs/bishop-mission/iteration-020/button-surface-evidence.json')
        previous={p['x']:p for p in measured['boundaries']['after']['column_boundaries']}
        top,bottom=self.actual(self.rz)
        self.top_bias=np.array([previous[x]['top'] for x in self.x])-top
        self.front=np.array([previous[x]['bottom'] for x in self.x])
        self.front_bias=self.front-bottom

    def actual(self,rz):
        dense=smooth_meridian(rz)
        r,z=dense.T
        d=r[:,None]**2-self.r[None,:]**2
        valid=d>=0
        d=self.yr*np.sqrt(np.maximum(d,0))
        axis=self.cy-self.zy*z[:,None]
        return np.min(np.where(valid,axis-d,1e5),axis=0),np.max(np.where(valid,axis+d,-1e5),axis=0)

    def shape(self,height,v):
        radius,edge,wall,power,shoulder=v
        rz=self.rz.copy()
        # Leave the broad contact and underside controls 0–3 in their
        # original positions. Fair the outer wall and dome into that seat.
        rz[4:,0]*=radius
        rz[4,1]+=wall*.22
        rz[5,1]+=wall
        rz[6,1]=rz[5,1]+edge
        rr=rz[7:,0]/rz[6,0]
        rz[7:,1]=height-(height-rz[6,1])*rr**power
        rz[7:10,0]*=1+shoulder*np.array([.52,1.,.48])
        return rz

    def scores(self,rz):
        top,front=self.actual(rz);top+=self.top_bias;front+=self.front_bias
        # Actual photographic edges are antialiased. Compare the absolute
        # envelope over the whole arc and the stable photographic tip.
        original=float(np.mean(abs(top-self.target)))
        selected=float(np.mean(abs(top-self.selected)))
        front_error=float(np.mean(abs(front-self.front)))
        center=abs(np.min(top)-self.target.min())
        dense=smooth_meridian(rz)
        half_width=dense[:,0].max()*self.xr
        return {'original_back_mae':original,'selected_back_mae':selected,'front_drift_mae':front_error,
                'back_tip':float(np.min(top)),'tip_residual':float(center),'half_width_px':float(half_width)}

    def fit(self,height,max_power=5.0):
        lo=np.array([.981,.005,-.008,1.65,-.03])
        hi=np.array([1.023,.022,.031,max_power,.03])
        v=np.array([1.,.010,.008,min(2.4,max_power),0.])
        def loss(v):
            rz=self.shape(height,v)
            if np.any(np.diff(rz[4:,1])<-.00003) or rz[6,1]>height-.013:return 1e5
            o=self.scores(rz)
            width=(o['half_width_px']-66.9)
            return o['original_back_mae']+.29*o['selected_back_mae']+.4*o['front_drift_mae']+.13*o['tip_residual']+.16*abs(width)
        best=loss(v)
        for step in [.25,.13,.065,.03,.012,.005,.0015]:
            for _ in range(16):
                changed=False
                for i in range(len(v)):
                    for sign in (-1.,1.):
                        u=v.copy();u[i]=np.clip(v[i]+sign*step*(hi[i]-lo[i]),lo[i],hi[i])
                        score=loss(u)
                        if score<best-1e-8:v,best,changed=u,score,True
                if not changed:break
        return self.shape(height,v),v,self.scores(self.shape(height,v))


def main():
    f=Projection();OUT.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
    result={'camera':read(BASE/'camera.json'),'baseline':f.scores(f.rz),'source_sha256':SOURCE_SHA,'cases':{}}
    for name,height in [('light',4.566),('medium',4.550),('low',4.536)]:
        rz,v,metric=f.fit(height)
        rings={str(i):[float(r/f.fac),float(f.s['y0']-z*f.cos/f.fac)] for i,(r,z) in enumerate(rz) if i>=4}
        cfg={'variant':'185-'+name,'source':source.relative_to(ROOT).as_posix(),'source_sha256':SOURCE_SHA,
             'profile':'history/bishop-mission-024/profile.json','samples':64,'body_rings':{},'finial_rings':rings,
             'interpretation':'Original-view-first height trial. Seated round button with a lower convex dome; existing body, sharp slit, foot and silhouette registration held.'}
        (OUT/(name+'.json')).write_text(json.dumps(cfg,indent=2)+'\n')
        result['cases'][name]={'control_height':height,'parameters':v.tolist(),**metric}
    # For a centered circular button the back edge cannot exceed this
    # bound even if its entire top reaches the greatest physical height.
    # The original measured button is roughly 134 px across.
    h=4.135986328125; x=(f.cy-f.zy*h-f.target.min())/f.yr
    result['full_target_bound']={'requested_height':h,'reference_top':float(f.target.min()),
        'required_minimum_rear_radius':float(x),'024_button_max_radius':float(smooth_meridian(f.rz)[:,0].max()),
        'required_diameter_pixels_at_least':float(2*x*f.xr),'existing_button_diameter_px':2*result['baseline']['half_width_px']}
    (DOC/'button-proposals.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='camera'},indent=2))


if __name__=='__main__':main()

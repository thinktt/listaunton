"""Fit revolved sections and visible collar arcs at the saved camera with a locked finial height."""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from compare_shared_turning import sprite
from compare_side_refit import read, screenshot_mask
from fit_side_refit import half_widths, smooth_meridian
from side_refit_profile import shape, MITRE

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/bishop-mission/iteration-027'
PREVIOUS=ROOT/'docs/bishop-mission/iteration-026'
BASE=ROOT/'history/bishop-mission-026'
ASSETS=ROOT/'assets/bishop'
NAMES=('base_factor','stem_radius','waist_height','collar_radius','collar_height','head_radius',
       'head_height','lower_rim','middle_rim','upper_rim','mitre_lower','mitre_upper')
LIMITS=np.array([(1.025,1.085),(.95,1.13),(-.075,.1),(1.01,1.105),(.95,1.24),(.990,1.045),
                 (.69,.89),(-.023,.027),(-.023,.025),(-.024,.022),(-.015,.065),(0,.085)])
XY_BANDS={'button':(156,214),'mitre':(214,400),'collars':(400,593),'stem':(593,620),
          'rear_flare':(620,790),'foot':(790,1114)}


def gray(im):
    return np.asarray(im)[:,:,:3]@np.array([.2126,.7152,.0722])


def landmarks(im):
    g=gray(im)
    center=np.mean(g[:,486:499],axis=1)
    def choice(lo,hi,light=False):
        data=center[lo:hi+1]
        return int(lo+(np.argmax(data) if light else np.argmin(data)))
    slit=[]
    for y in range(250,411,10):
        strip=g[y-2:y+3].mean(axis=0)
        lo,hi=493,577
        x=int(lo+strip[lo:hi+1].argmin())
        slit.append([x,y])
    return {'collar_trough_rows':[choice(508,520),choice(563,574),choice(607,616)],
            'socket_highlight_row':choice(799,822,True),'groove_trough_row':choice(1043,1061),
            'slit_dark_center_samples':slit,'slit_tip_approx_xy':[511,422]}


def meridian_controls(profile,points):
    al=read(ASSETS/'original-alignment.json')
    factor=1254/300/al['scale']/profile['scale']
    arr=np.array(points)
    return np.stack((arr[:,0]*factor,(profile['y0']-arr[:,1])*factor/math.cos(math.radians(54))),axis=1)


class Fit:
    def __init__(self):
        self.spec=read(DOC/'side-refit.json')
        p=read(BASE/'profile.json')
        self.old=meridian_controls(p,p['profile'])
        self.cap=meridian_controls(p,p['finial']['profile'])
        self.height=self.spec['locked_height']
        frame=read(BASE/'camera.json')
        m=np.array(frame['projectionMatrix']).reshape(4,4)@np.array(frame['worldToCamera']).reshape(4,4)
        self.ox=(1+m[0,3])*627; self.oy=(1-m[1,3])*627
        self.xr=627*m[0,0]; self.depth=627*m[1,1]; self.vertical=627*m[1,2]
        self.target=read(PREVIOUS/'side-target.json')
        render=sprite()
        arr=np.asarray(render)
        self.reference=half_widths((arr[:,:,3]>127)&(arr[:,:,:3].max(2)>12))
        self.white_land=landmarks(render)
        self.detail_land=landmarks(Image.open(ASSETS/'reference.png').convert('RGBA'))
        self.fy=np.arange(156,1116,5)
        self.side=half_widths(screenshot_mask(Image.open(PREVIOUS/'owner-side-crop.png'),11))
        self.sy=np.arange(30,249,2)
        self.sz=(self.target['floor_y']-self.sy-.5)/self.target['pixels_per_unit']
        self.base_measures=read(PREVIOUS/'measurements.json')['compromise']
        # Calibrate the few sampling and subdivision biases to the previous
        # saved render once. These offsets stay fixed across candidate shapes.
        neutral={'base_factor':1.,'stem_radius':1.,'collar_radius':1.,'collar_height':1.,'head_radius':1.,'head_height':1.}
        raw=self.predict(neutral)
        original_alpha=np.asarray(Image.open(BASE/'render-clay.png'))[:,:,3]
        self.bias=half_widths(original_alpha>127)[self.fy]-raw['width']
        self.rim_bias=np.array(list(self.base_measures['front_collar_rim_rows'].values()))-raw['rims']

    def predict(self,params):
        p,dz=shape(self.old,self.height,self.spec,params)
        b=smooth_meridian(p)
        fin=smooth_meridian(self.cap*[params['head_radius'],params['head_height']]+[0,dz])
        tail=np.vstack((b[:-1],fin[:-1]))
        nxt=np.vstack((b[1:],fin[1:]))
        step=nxt-tail
        t=(self.sz[:,None]-tail[:,1])/np.where(abs(step[:,1])>1e-12,step[:,1],1e-12)
        side=np.max(np.where((t>=0)&(t<=1),tail[:,0]+t*step[:,0],0),axis=1)*self.target['pixels_per_unit']
        rz=np.vstack((b,fin))
        r,z=rz.T
        q=(self.fy[:,None]+.5-self.oy+z*self.vertical)/np.maximum(r*self.depth,1e-8)
        width=np.sqrt(np.max(np.maximum(1-q*q,0)*(r*self.xr)**2,axis=1))
        front=self.oy-self.vertical*b[:,1]+self.depth*b[:,0]
        rims=np.array([front[lo*6:hi*6].max() for lo,hi in ((66,72),(57,64),(48,55))])
        # Limit secondary bulges on the visible taper and guard the thickness
        # of the original direct head/button join above control row 110.
        head=b[MITRE*6:110*6]
        peak=int(head[:,0].argmax())
        reverse=np.maximum(head[peak:,0]-np.minimum.accumulate(head[peak:,0]),0.).max()
        # A deep saw must stay low enough relative to the head to be readable.
        # Preserve the whole floor with the affine head map in these proposals.
        return {'width':width,'rims':rims,'side':side,'reverse':reverse}

    def errors(self,v):
        params=dict(zip(NAMES,v))
        data=self.predict(params)
        w=np.maximum(0,data['width']+self.bias)
        diff=abs(w-self.reference[self.fy])
        groups={k:float(np.mean(diff[(self.fy>=a)&(self.fy<b)])) for k,(a,b) in XY_BANDS.items()}
        rims=data['rims']+self.rim_bias
        rim_err=abs(rims-self.white_land['collar_trough_rows'])
        side=float(np.mean(abs(data['side']-self.side[self.sy])))
        return groups,rim_err,side,data['reverse'],float((np.minimum(w,self.reference[self.fy]).sum())/np.maximum(w,self.reference[self.fy]).sum())

    def search(self,weights):
        a,b,c=weights
        def loss(v):
            e,arcs,side,reverse,iou=self.errors(v)
            groups=.30*e['mitre']+.24*e['collars']+.10*e['stem']+.12*e['rear_flare']+.24*e['foot']
            # The optical trough lies just below a physical crest. Source
            # resolution allows a two-pixel dead band on those front arcs.
            arc_loss=np.maximum(arcs-2,0).mean()
            button=abs(v[NAMES.index('head_radius')]-1.015)*8
            return groups+a*arc_loss+b*side+c*(1-iou)+60*reverse+button
        start=self.spec['cases']['raised']
        v=np.array([start.get(n,0.) for n in NAMES])
        result=loss(v)
        for step in [.25,.125,.0625,.03125,.015625]:
            for _ in range(5):
                changed=False
                for i in range(len(v)):
                    cand=[]
                    for sign in [-1,1]:
                        u=v.copy()
                        u[i]=float(np.clip(v[i]+sign*step*(LIMITS[i,1]-LIMITS[i,0]),*LIMITS[i]))
                        cand.append((loss(u),u))
                    l,u=min(cand,key=lambda it:it[0])
                    if l<result-1.e-5:
                        result,v,changed=l,u,True
                if not changed:break
        e,r,s,reverse,iou=self.errors(v)
        return {'case':{k:round(float(x),7) for k,x in zip(NAMES,v)},'proxy_outline_iou':iou,
                'half_width_errors':e,'rim_errors':r.tolist(),'side_half_width_mae':s,
                'secondary_bulge_native':float(reverse),'weights':weights}


if __name__=='__main__':
    fit=Fit()
    proposals={k:fit.search(w) for k,w in [('arc-fit',[.7,.35,24.]),('contour-fit',[.27,.2,80.])]}
    (DOC/'fit-proposals.json').write_text(json.dumps({'model':'Calibrated cubic meridian envelope at the 026 saved camera. Predictions and photographic arc cues are independently checked on real renders.',
        'original_white_features':fit.white_land,'white_3_features':fit.detail_land,
        'radius_and_height_parameter_bounds':dict(zip(NAMES,LIMITS.tolist())),'proposals':proposals},indent=2)+'\n')
    for k,row in proposals.items():
        print(k,round(row['proxy_outline_iou']*100,3),row['rim_errors'],row['case'],flush=True)

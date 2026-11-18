"""Propose a regional fit using a sampled lathe, a fixed screenshot ruler and the saved camera."""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image

from compare_side_refit import ARCHIVE, ASSETS, DOC, read, screenshot_mask, spans
from compare_shared_turning import sprite
from side_refit_profile import shape


def smooth_meridian(controls):
    # Subdivision limit of a uniform cubic ring chain. Ends are repeated at
    # the axis. Blender's exact evaluated mesh and Boolean are checked later.
    pad=np.pad(controls,((1,2),(0,0)),mode='edge')
    t=np.arange(6,dtype=float)/6
    w=np.stack(((1-t)**3,4-6*t*t+3*t**3,1+3*t+3*t*t-3*t**3,t**3),axis=1)/6
    windows=np.stack([pad[i:i+len(controls)] for i in range(4)],axis=1)
    return np.einsum('kj,ijd->ikd',w,windows).reshape(-1,2)


def half_widths(image_mask):
    yes,l,r=spans(image_mask)
    return np.where(yes,(r-l+1)*.5,0.)


def main():
    spec=read(DOC/'side-refit.json')
    target=read(DOC/'side-target.json')
    profile=read(ARCHIVE/'profile.json')
    al=read(ASSETS/'original-alignment.json')
    f=1254/300/al['scale']/profile['scale']
    angle=math.radians(54)
    def decode(points):
        q=np.array(points)
        return np.stack((q[:,0]*f,(profile['y0']-q[:,1])*f/math.cos(angle)),axis=1)
    old=decode(profile['profile'])
    cap=decode(profile['finial']['profile'])
    height=target['old_height']
    frame=read(ARCHIVE/'camera.json')
    mat=np.array(frame['projectionMatrix']).reshape(4,4)@np.array(frame['worldToCamera']).reshape(4,4)
    oy=(1-mat[1,3])*627
    xr=mat[0,0]*627
    ydepth=mat[1,1]*627
    yheight=mat[1,2]*627
    crop=Image.open(DOC/'owner-side-crop.png')
    side=half_widths(screenshot_mask(crop,11))
    sy=np.arange(29,249)
    sz=(target['floor_y']-sy-.5)/target['pixels_per_unit']
    raw=np.asarray(sprite())
    ref=half_widths((raw[:,:,3]>127)&(raw[:,:,:3].max(2)>12))
    fy=np.arange(165,1117,5)
    names=['stem_radius','collar_radius','collar_height','head_radius','head_height','waist_height']
    lower=np.array([.93,.934,.845,.931,.855,-.055])
    upper=np.array([.974,.981,.981,.979,.966,.055])
    def evaluate(v):
        case=dict(zip(names,v))
        body,dz=shape(old,height,spec,case)
        button=cap*[case['head_radius'],case['head_height']]+[0,dz]
        body=smooth_meridian(body); button=smooth_meridian(button)
        a=np.concatenate((body[:-1],button[:-1]))
        b=np.concatenate((body[1:],button[1:]))
        dr=b[:,0]-a[:,0];zh=b[:,1]-a[:,1]
        t=(sz[:,None]-a[:,1])/np.where(abs(zh)>1e-10,zh,1e-10)
        sr=np.max(np.where((t>=0)&(t<=1),a[:,0]+t*dr,0.),axis=1)
        side_error=np.mean(np.abs(sr*target['pixels_per_unit']-side[sy]))
        pts=np.vstack((body,button))
        r,z=pts.T
        # Projection of a circular ring at each sensor row. The union over
        # rings supplies the visible exterior of the revolved mesh.
        q=(fy[:,None]+.5-oy+yheight*z)/np.maximum(r*ydepth,1e-7)
        px=np.sqrt(np.max(np.maximum(1-q*q,0.)*(r*xr)**2,axis=1))
        fixed=np.mean(np.abs(ref[fy]-px))
        # Front collar crests are interior evidence missing from silhouette IoU.
        rims=[]
        for lo,hi in [(66,72),(57,64),(48,55)]:
            seg=body[lo*6:hi*6]
            rims.append(np.max(oy-yheight*seg[:,1]+ydepth*seg[:,0]))
        arcs=np.mean(np.abs(np.array(rims)-[513.,568.,612.]))
        return float(side_error),float(fixed),float(arcs)
    start=np.array([spec['cases']['balanced'].get(k,0.) for k in names])
    def search(weights):
        v=start.copy()
        metrics=evaluate(v)
        score=lambda tup:float(np.dot(tup,weights))
        for step in [0.18,0.09,0.045,0.0225]:
            for _ in range(6):
                changed=False
                for j in range(len(v)):
                    trials=[]
                    for sign in [-1.,1.]:
                        vv=v.copy(); vv[j]=np.clip(v[j]+sign*step*(upper[j]-lower[j]),lower[j],upper[j])
                        mm=evaluate(vv); trials.append((score(mm),vv,mm))
                    val,best,meas=min(trials,key=lambda row:row[0])
                    if val<score(metrics)-1e-6:
                        v,metrics,changed=best,meas,True
                if not changed:break
        return {'parameters':{k:round(float(x),6) for k,x in zip(names,v)},'predicted_errors':metrics,'weights':weights}
    proposals={name:search(w) for name,w in [('side-first',[1.,0.,0.]),('compromise',[1.,.12,.035])]}
    result={'method':'Cubic control-ring envelope, sampled side and orthographic ring projection. Predictions only. Each proposed model is compared again after subdivision, Boolean and rendering.',
            'error_units':['screenshot_px','registered_outline_px','front_collar_rows_px'],'balanced':evaluate(start),'proposals':proposals}
    (DOC/'fit-proposals.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(proposals,indent=2))


if __name__=='__main__':
    main()

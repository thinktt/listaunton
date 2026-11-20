"""Bound a small change to the pawn's flare by both original silhouettes.

A horizontal lathe ring projects as an ellipse at the fixed orthographic
elevation. Fit the envelope of those ellipses, regularizing the meridian;
Blender renders and closure/sizing checks decide whether the fit is useful.
"""
import argparse,json
from pathlib import Path
import numpy as np
from audit_mission import ROOT, registered, mask

def refined_controls(profile):
    # One Catmull-Clark level on a regular revolved quad grid. Dense
    # meridian interpolation estimates the silhouette between adjacent rings.
    even=profile.copy()
    even[1:-1]=(profile[:-2]+6*profile[1:-1]+profile[2:])/8
    rz=np.empty((2*len(profile)-1,2))
    rz[::2]=even;rz[1::2]=(profile[:-1]+profile[1:])/2
    sub=np.linspace(0,len(rz)-1,(len(rz)-1)*16+1)
    result=np.column_stack([np.interp(sub,np.arange(len(rz)),rz[:,i]) for i in (0,1)])
    result[:,0]*=.99955
    return result

def run(out):
    cfg=json.loads((ROOT/"scripts/pawn/profile.json").read_text())
    align=json.loads((ROOT/"assets/pawn/original-alignment.json").read_text())
    original=np.array(cfg["profile"],dtype=float)
    first=json.loads((ROOT/"docs/pawn-mission/iteration-001/003-walnut-seated-sphere.json").read_text())
    original[:5]=first["round_head"]["foot_profile"]
    rows=np.arange(609,865,3);factor=1254/300/align["scale"];sine=np.sin(np.deg2rad(54))
    references=registered();widths={}
    for name,im in references.items():
        m=mask(im,True);widths[name]=np.array([np.ptp(np.flatnonzero(m[y]))/2 for y in rows])
    target=.64*widths["original_black"]+.23*widths["original_white"]+.13*widths["selected"]
    def envelope(profile):
        smoothed=refined_controls(profile[:33])
        radius=smoothed[:,0]*factor;axis=(smoothed[:,1]-3*align["y"])*factor
        sq=radius[None,:]**2-((rows[:,None]-axis[None,:])/sine)**2
        return np.sqrt(np.maximum(sq.max(1),0))
    # Four broad overlapping adjustments prevent a saw-toothed fitted edge.
    ids=np.arange(13,21);centers=np.array([13.6,15.6,17.5,19.7])
    basis=np.exp(-.5*((ids[:,None]-centers)/1.15)**2)
    basis*=np.sin(np.pi*(ids-12)/9)[:,None]
    def profile(x):
        result=original.copy()
        result[ids,0]+=basis@x[:4]
        result[ids,1]+=basis@x[4:]
        return result
    def residual(x):
        q=profile(x);front=(q[ids,1]-original[ids,1]+sine*(q[ids,0]-original[ids,0]))*factor
        slope=np.diff(q[13:21,1])/np.minimum(np.diff(q[13:21,0]),-.08)
        # The upper roll should lose slope toward the socket. Penalize
        # curvature reversals that would create an extra reflective ridge.
        reverse=np.maximum(np.diff(slope),0)
        return np.r_[envelope(q)-target,front*.70,x*1.8,reverse*17,
                     np.maximum(np.diff(q[13:21,0])+.10,0)*50,
                     np.maximum(np.diff(q[12:22,1])+.05,0)*50]
    x=np.zeros(8);start=residual(x)
    for _ in range(30):
        old=residual(x);J=np.column_stack([(residual(x+np.eye(8)[i]*.02)-residual(x-np.eye(8)[i]*.02))/.04 for i in range(8)])
        delta=np.linalg.lstsq(J,-old,rcond=None)[0]
        accepted=False
        for step in (1,.5,.25,.125,.0625):
            trial=np.clip(x+delta*step,-2.3,2.3)
            if np.linalg.norm(residual(trial))<np.linalg.norm(old)-1e-5:
                x=trial;accepted=True;break
        if not accepted:break
    q=profile(x)
    changes={str(i):q[i].round(5).tolist() for i in ids}
    out.mkdir(parents=True,exist_ok=True)
    study={"rows":[int(rows.min()),int(rows.max())],"original_black_weight":.64,"original_white_weight":.23,"selected_weight":.13,"method":"Registered row half-widths against the envelope of projected lathe rings. Bounded smooth control edits; front-landmark and curvature penalties. No camera fit.","prior_width_rmse_px":float(np.sqrt(np.mean((envelope(original)-target)**2))),"trial_width_rmse_px":float(np.sqrt(np.mean((envelope(q)-target)**2))),"profiles":changes,"parameters":x.tolist()}
    (out/"flare-fit.json").write_text(json.dumps(study,indent=2)+"\n")
    result={"variant":"011-original-flare-fit","source":"history/pawn-mission-002/pawn-rebuilt.blend","source_sha256":"8d81351fee5d4cbe6a290ea80e8915a92a7ebef31f4a5e40c86dadedd940b5f0","profiles":changes,"samples":128}
    (out/"011-geometry.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(study,indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("output",type=Path)
    a=p.parse_args();run(a.output)

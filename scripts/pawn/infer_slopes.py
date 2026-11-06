"""Fit limited, static wood normal variation to measured tangent-space responses."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from derive_wood import ROOT, blur, ramp, sample
from lathe_projection import visible_tiles

WEIGHTS=np.array([.24,.53,.23],np.float32)


def rgba(path):
    return np.asarray(Image.open(path).convert("RGBA"),dtype=np.float32)/255


def weighted_dot(a,b):
    return np.sum(a*b*WEIGHTS,axis=2)


def fit_screen(reference,passes,cfg,poses=None):
    flat=passes["flat"][:,:,:3]
    common=(reference[:,:,3]>.99)&(passes["flat"][:,:,3]>.99)
    delta=reference[:,:,:3]-flat
    # The broad lighting arrangement stays with the studio. Concentrate on
    # ripples that the actual measured slope response can reproduce.
    target=delta-(1-cfg["broad_scale_fraction"])*blur(delta,r=4,passes=2)
    base_loss=weighted_dot(target,target)
    best=base_loss.copy()
    slopes=np.zeros((*best.shape,2),np.float32)
    response_strength=np.zeros_like(best)
    penalty=(cfg["prior_255"]/255)**2
    if poses is not None:
        # Each measured direction includes the actual nonlinear response
        # of the varnish, including diagonal movement across a strip light.
        for name,(du,dv) in poses.items():
            if name=="flat":
                continue
            response=passes[name][:,:,:3]-flat
            sensitivity=weighted_dot(response,response)
            prior=penalty*(du*du+dv*dv)
            amount=np.clip(weighted_dot(response,target)/(sensitivity+prior+1e-10),0,1)
            residual=target-response*amount[:,:,None]
            loss=weighted_dot(residual,residual)+prior*amount*amount
            better=loss<best
            best[better]=loss[better]
            slopes[:,:,0][better]=du*amount[better]
            slopes[:,:,1][better]=dv*amount[better]
            response_strength[better]=np.sqrt(sensitivity[better])
        confidence=common*ramp(response_strength,3/255,15/255)*ramp(base_loss-best,0,(5/255)**2)
        return slopes,confidence
    for uname,usign in (("u-plus",1),("u-minus",-1)):
        u=passes[uname][:,:,:3]-flat
        gu=weighted_dot(u,target)
        uu=weighted_dot(u,u)+penalty
        for vname,vsign in (("v-plus",1),("v-minus",-1)):
            v=passes[vname][:,:,:3]-flat
            gv=weighted_dot(v,target)
            vv=weighted_dot(v,v)+penalty
            uv=weighted_dot(u,v)
            det=np.maximum(uu*vv-uv*uv,1e-12)
            a=np.clip((gu*vv-gv*uv)/det,0,1)
            b=np.clip((gv-uv*a)/vv,0,1)
            a=np.clip((gu-uv*b)/uu,0,1)
            # Stay in the simplex covered by flat and these two measured
            # poses. Do not infer a steep normal from extrapolated radiance.
            divisor=np.maximum(1,a+b)
            a/=divisor;b/=divisor
            residual=target-u*a[:,:,None]-v*b[:,:,None]
            loss=weighted_dot(residual,residual)+penalty*(a*a+b*b)
            improve=loss<best
            best[improve]=loss[improve]
            slopes[:,:,0][improve]=usign*a[improve]
            slopes[:,:,1][improve]=vsign*b[improve]
            response_strength[improve]=np.sqrt(np.maximum(uu,vv)[improve])
    confidence=common*ramp(response_strength,4/255,18/255)*ramp(base_loss-best,0,(6/255)**2)
    return slopes,confidence


def run(cfg):
    directory=ROOT/"build/pawn-mission"/cfg["measurement"]
    record=json.loads((directory/"measurement.json").read_text())
    alpha=np.asarray(Image.open(directory/"flat.png").getchannel("A"))
    y,x=np.nonzero(alpha>127)
    box=np.s_[max(0,y.min()-12):min(alpha.shape[0],y.max()+13),max(0,x.min()-12):min(alpha.shape[1],x.max()+13)]
    passes={}
    for name,expected in record["pass_sha256"].items():
        path=directory/(name+".png")
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
        passes[name]=rgba(path)[box].copy()
    slopes=np.zeros((*alpha.shape,2),np.float32)
    confidence=np.zeros(alpha.shape,np.float32)
    poses=None
    if record["config"].get("rings"):
        step=record["config"]["step"]
        poses={k:[dx/step,dy/step] for k,(dx,dy) in record["poses"].items()}
    slopes[box],confidence[box]=fit_screen(rgba(ROOT/"assets/pawn/reference.png")[box],passes,cfg,poses)
    del passes
    geom=ROOT/"build/pawn-mission"/cfg["geometry_measurement"]
    # The saved mesh binary includes positions, normals, UVs and triangles.
    assert hashlib.sha256((ROOT/"assets/pawn/mesh.bin").read_bytes()).hexdigest()==cfg["mesh_sha256"]
    profile=np.load(geom/"meridian.npy");depth=np.load(geom/"depth.npy")
    if depth.ndim==3:
        depth=depth[:,:,0]
    camera=json.loads((ROOT/"assets/pawn/camera.json").read_text())
    pigment=rgba(ROOT/cfg["pigment"])[:,:,:3]
    wood=np.log(.03+pigment@WEIGHTS)
    dy,dx=np.gradient(wood-blur(wood,r=3,passes=2))
    step=record["config"]["step"]
    limit=cfg["max_slope"]
    # A little variation follows unlit pigment even round the back.
    if "prior_texture" in cfg:
        prior=ROOT/cfg["prior_texture"]
        assert hashlib.sha256(prior.read_bytes()).hexdigest()==cfg["prior_sha256"]
        atlas=(np.asarray(Image.open(prior).convert("RGB"),np.float32)[:,:,:2]-128)*(cfg["prior_slope_limit"]/127)
    else:
        atlas=np.clip(np.stack((-dx,dy),axis=-1)*cfg["grain_gain"],-.030,.030)
    for rows,_,_,_,px,py,visible in visible_tiles(profile,depth,camera,len(wood)):
        reliable=visible*sample(confidence,px,py)
        measured=step*sample(slopes,px,py)
        if "prior_texture" in cfg:
            atlas[rows]+=cfg.get("delta_scale",1)*measured*reliable[:,:,None]
        else:
            atlas[rows]=atlas[rows]*(1-reliable[:,:,None])+measured*reliable[:,:,None]
    amplitude=np.linalg.norm(atlas,axis=2)
    atlas*=np.minimum(1,limit/np.maximum(amplitude,1e-6))[:,:,None]
    rg=np.uint8(np.rint(128+127*np.clip(atlas/limit,-1,1)))
    encoded=np.dstack((rg,np.full(wood.shape,255,np.uint8)))
    path=ROOT/cfg["texture"]
    Image.fromarray(encoded).save(path)
    angles=np.degrees(np.arctan(np.linalg.norm(atlas,axis=2)))
    result={"config":cfg,"source":record,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"confident_observed_pixels":int((confidence>.5).sum()),"median_angle_degrees":float(np.median(angles)),"q99_angle_degrees":float(np.quantile(angles,.99)),"max_angle_degrees":float(angles.max())}
    (directory/"slope-fit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print({key:result[key] for key in ("sha256","confident_observed_pixels","median_angle_degrees","q99_angle_degrees","max_angle_degrees")})


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("config",type=Path)
    args=p.parse_args()
    run(json.loads(args.config.read_text()))

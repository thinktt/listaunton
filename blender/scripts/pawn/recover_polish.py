"""Fit bounded finish properties only where their measured response exceeds noise."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

from derive_wood import ROOT,blur,ramp,sample
from lathe_projection import visible_tiles

W=np.array([.24,.53,.23],np.float32)


def pixels(path,box):
    return np.asarray(Image.open(path).convert("RGBA").crop(box),np.float32)/255


def dot(a,b):
    return np.sum(a*b*W,axis=2)


def run(cfg):
    directory=ROOT/"build/pawn-mission"/cfg["measurement"]
    record=json.loads((directory/"measurement.json").read_text())
    alpha=Image.open(directory/"flat.png").getchannel("A")
    x0,y0,x1,y1=alpha.getbbox()
    box=(max(0,x0-10),max(0,y0-10),min(alpha.width,x1+10),min(alpha.height,y1+10))
    flat=pixels(directory/"flat.png",box)
    other=pixels(directory/"flat-independent.png",box)[:,:,:3]
    ref=pixels(ROOT/"assets/pawn/reference.png",box)
    valid=(flat[:,:,3]>.99)&(ref[:,:,3]>.99)
    flat=flat[:,:,:3]
    change=ref[:,:,:3]-.5*(flat+other)
    target=change-(1-cfg["broad_fraction"])*blur(change,r=4,passes=2)
    noise_sq=blur(dot(flat-other,flat-other),r=2,passes=2)*.5
    loss0=dot(target,target);best=loss0.copy()
    shift=np.zeros((*loss0.shape,2),np.float32)
    sensitivity=np.zeros_like(best)
    for name,spec in record["poses"].items():
        if name=="flat":continue
        path=directory/(name+".png")
        assert hashlib.sha256(path.read_bytes()).hexdigest()==spec["sha256"]
        response=pixels(path,box)[:,:,:3]-flat
        energy=dot(response,response)
        step=np.log([spec["rough"],spec["polish"]])
        penalty=(cfg["prior_255"]/255)**2*(step[0]**2+1.35*step[1]**2)+cfg["noise_prior"]*noise_sq
        amount=np.clip(dot(target,response)/(energy+penalty+1e-9),0,1)
        remaining=target-response*amount[:,:,None]
        loss=dot(remaining,remaining)+penalty*amount**2
        better=loss<best
        best[better]=loss[better]
        shift[:,:,0][better]=step[0]*amount[better]
        shift[:,:,1][better]=step[1]*amount[better]
        sensitivity[better]=np.sqrt(energy[better])
    confidence=valid*ramp(sensitivity-.55*np.sqrt(noise_sq),3/255,16/255)
    confidence*=ramp((loss0-best)/((4/255)**2+noise_sq),.15,2.2)
    full=np.zeros((alpha.height,alpha.width,3),np.float32)
    dst=np.s_[box[1]:box[3],box[0]:box[2]]
    full[dst]=np.dstack((shift,confidence))
    prior=ROOT/cfg["roughness_source"]
    assert hashlib.sha256(prior.read_bytes()).hexdigest()==cfg["roughness_sha256"]
    prior_pixels=np.asarray(Image.open(prior).convert("RGB"))
    value=prior_pixels[:,:,0].astype(np.float32)/255
    rlo,rhi=cfg["prior_rough_range"]
    rough=rlo+(rhi-rlo)*value
    polish=np.ones_like(rough)
    if cfg.get("prior_polish_range"):
        plo,phi=cfg["prior_polish_range"]
        polish=plo+(phi-plo)*prior_pixels[:,:,1].astype(np.float32)/255
    focus=None
    if cfg.get("uv_focus"):
        v=1-(np.arange(len(rough),dtype=np.float32)+.5)/len(rough)
        a,b,c,d=cfg["uv_focus"]
        focus=ramp(v,a,b)*(1-ramp(v,c,d))
    geom=ROOT/"build/pawn-mission"/cfg["geometry_measurement"]
    profile=np.load(geom/"meridian.npy");depth=np.load(geom/"depth.npy")[:,:,0]
    assert hashlib.sha256((ROOT/"assets/pawn/mesh.bin").read_bytes()).hexdigest()==cfg["mesh_sha256"]
    camera=json.loads((ROOT/"assets/pawn/camera.json").read_text())
    for rows,_,_,_,px,py,visibility in visible_tiles(profile,depth,camera,len(rough)):
        prop=sample(full,px,py)
        w=cfg["update"]*visibility*prop[:,:,2]
        if focus is not None:w*=focus[rows,None]
        rough[rows]*=np.exp(w*prop[:,:,0])
        polish[rows]*=np.exp(w*prop[:,:,1])
    def encode(values,bounds):
        lo,hi=bounds
        return np.uint8(np.rint(255*np.clip((values-lo)/(hi-lo),0,1)))
    packed=np.dstack((encode(rough,cfg["rough_range"]),encode(polish,cfg["polish_range"]),np.full(rough.shape,255,np.uint8)))
    if focus is not None:packed[focus==0]=prior_pixels[focus==0]
    out=ROOT/cfg["texture"]
    Image.fromarray(packed).save(out)
    report={"config":cfg,"calibration":record,"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"confident_pixels":int((confidence>.5).sum()),"polish_range_fitted":[float(polish.min()),float(polish.max())],"fraction_of_uv_with_polish_change_over_10pct":float(np.mean(np.abs(polish-1)>.10))}
    (directory/"recovered-polish.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print({k:report[k] for k in ("sha256","confident_pixels","polish_range_fitted","fraction_of_uv_with_polish_change_over_10pct")})


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args();run(json.loads(a.config.read_text()))

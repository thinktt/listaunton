"""Update the existing unlit walnut only where the measured diffuse response is reliable."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image,ImageFilter
from derive_wood import ROOT,blur,display,linear,ramp,sample
from lathe_projection import visible_tiles

W=np.array([.2126,.7152,.0722],np.float32)


def run(cfg):
    directory=ROOT/"build/pawn-mission"/cfg["measurement"]
    record=json.loads((directory/"measurement.json").read_text())
    assert record["source_sha256"]==cfg["source_sha256"]
    black=np.load(directory/"black.npy")
    neutral=np.load(directory/"gray.npy")
    actual=np.load(directory/"beauty.npy")[:,:,:3]
    target=np.load(directory/"target-linear.npy")
    reference=np.load(directory/"reference-srgb.npy")
    response=(neutral[:,:,:3]-black[:,:,:3])/.1
    body=(black[:,:,3]>.995)&(reference.max(2)>12/255)
    safe=np.asarray(Image.fromarray(body.astype(np.uint8)*255).filter(ImageFilter.MinFilter(7)),np.float32)/255
    # Avoid the reflection floor, grazing transitions and neighborhoods in
    # which the measured lamp response dominates the visible base color.
    floor=black[:,:,:3]@W
    spec_fraction=floor/np.maximum(actual@W,.004)
    confidence=safe*(1-ramp(spec_fraction,.23,.66))*ramp(response@W,.09,.38)
    confidence*=ramp((target-black[:,:,:3])@W,.0004,.005)
    delta=(target-actual)/np.maximum(response,.07)
    delta=np.clip(delta,-.16,.16)
    density=blur(confidence,r=1,passes=2)
    local=blur(delta*confidence[:,:,None],r=1,passes=2)/np.maximum(density[:,:,None],.03)
    delta+=cfg["fine_gain"]*(delta-local)
    src=ROOT/cfg["base_texture"]
    assert hashlib.sha256(src.read_bytes()).hexdigest()==cfg["base_sha256"]
    prior=linear(np.asarray(Image.open(src).convert("RGB"),np.float32)/255)
    result=prior.copy()
    size=len(prior)
    meridian=np.load(directory/"meridian.npy")
    depth=np.load(directory/"depth.npy")[:,:,0]
    camera=json.loads((ROOT/"assets/pawn/camera.json").read_text())
    for rows,_,_,_,px,py,visible in visible_tiles(meridian,depth,camera,size):
        base=prior[rows]
        shift=sample(delta,px,py)
        bound=cfg["relative_limit"]*base+cfg["dark_limit"]
        shift=np.clip(shift,-bound,bound)
        reliable=visible*sample(confidence,px,py)
        result[rows]=np.clip(base+cfg["step"]*reliable[:,:,None]*shift,.00012,.85)
    out=ROOT/cfg["texture"]
    Image.fromarray(np.uint8(np.rint(255*np.clip(display(result),0,1)))).save(out)
    change=np.abs(result-prior)
    report={"config":cfg,"measurement":record,"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"trusted_pixels":int((confidence>.7).sum()),"mean_abs_linear_change":float(change.mean()),"q99_abs_linear_change":float(np.quantile(change,.99)),"mean_abs_linear_hidden_change":float(np.mean(change[:int(.01*size)]))}
    (directory/"pigment-refinement.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    print({k:report[k] for k in ("sha256","trusted_pixels","mean_abs_linear_change","q99_abs_linear_change")})


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("config",type=Path)
    a=p.parse_args()
    run(json.loads(a.config.read_text()))

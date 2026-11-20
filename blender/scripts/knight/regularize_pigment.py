"""Separate slowly varying wood tone from fine grain and suppress reflected glare."""
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts/queen"))
from image_math import blur
DATA = ROOT/"build/knight-mission/material-observations"
OUT = DATA.parent/"soft-pigment"
OUT.mkdir(exist_ok=True)


def smooth_weighted(field, weights, radius, fallback):
    density=blur(weights,radius,3)
    smoothed=blur(field*weights[:,:,None],radius,3)/np.maximum(density[:,:,None],1e-6)
    gate=np.clip(density/.24,0,1)[:,:,None]
    return fallback+gate*(smoothed-fallback)


def run():
    display=np.load(DATA/"reference-display.npy")
    target=np.load(DATA/"reference-linear.npy")
    black=np.load(DATA/"black.npy")
    gray=np.load(DATA/"gray.npy")
    prior=np.load(DATA/"prior.npy")[:,:,:3]
    weights=np.array([.2126,.7152,.0722],dtype=np.float32)
    response=np.maximum((gray[:,:,:3]-black[:,:,:3])/.16,.015)
    foreground=(display[:,:,3]>.8)&(black[:,:,3]>.99)&(display[:,:,:3].max(2)>.05)
    interior=np.asarray(Image.fromarray(np.uint8(foreground)*255).filter(ImageFilter.MinFilter(11)),dtype=np.float32)/255
    feather=blur(interior,3,3)
    # Approximate the source's dielectric reflection from excess neutral light.
    # Blur the reliable low-frequency material field across rejected highlights.
    red=target[:,:,0]
    spec=np.maximum(0,(target[:,:,2]-.085*red)/(.84-.085))
    diffuse=np.maximum(target-spec[:,:,None]*[1,.93,.84],.0004)
    estimate=diffuse/response
    confidence=interior*np.clip((.60-spec/np.maximum(red,.012))/.39,0,1)
    confidence*=np.clip(((display[:,:,:3]@weights)-.025)/.07,0,1)
    confidence*=np.clip(((response@weights)-.04)/.18,0,1)
    yy,xx=np.indices(interior.shape)
    for x,y,rx,ry in [(505,479,45,23),(704,507,26,15)]:
        confidence*=np.clip((((xx-x)/rx)**2+((yy-y)/ry)**2-.5)/1.15,0,1)
    r=np.clip(estimate[:,:,0],.016,.46)
    estimate=np.stack((r,np.clip(estimate[:,:,1],r*.15,r*.41),np.clip(estimate[:,:,2],r*.03,r*.14)),axis=2).astype(np.float32)
    prior_broad=blur(prior,7,3)
    broad=np.exp(smooth_weighted(np.log(estimate+.002),confidence,8,np.log(prior_broad+.002)))-.002
    broad=np.maximum(broad,.001)
    # Add fine observed pigment texture, suppressing strong carving/shadow edges.
    log_l=np.log(.004+np.maximum(diffuse@weights,0)).astype(np.float32)
    local=blur(log_l*interior,3,3)/np.maximum(blur(interior,3,3),1e-5)
    detail=np.clip(log_l-local,-.42,.42)
    prior_detail=np.clip(np.log((.003+prior@weights)/(.003+prior_broad@weights)),-.42,.42)
    visible_weight=blur(confidence,2,2)
    grain=detail*visible_weight+prior_detail*(1-visible_weight)
    color=np.clip(broad*np.exp(1.08*grain)[:,:,None],.001,.7)
    transfer=feather*.95*np.clip((blur(confidence,9,3)+.05)/.47,0,1)
    np.save(OUT/"estimated-pigment.npy",color.astype(np.float32))
    np.save(OUT/"transfer-confidence.npy",transfer.astype(np.float32))
    report={"source":"material-observations","method":"Estimate warm diffuse color with a constrained neutral reflection component. Interpolate broad pigment across uncertain pixels, use bounded high-pass detail, feather transfer at geometry edges. Preserve continuous 3D walnut on hidden surfaces.",
            "bounds":[.016,.46],"broad_radius":8,"detail_radius":3,"mean_direct_weight":float(confidence[foreground].mean())}
    (OUT/"inference.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))


if __name__=="__main__":
    run()

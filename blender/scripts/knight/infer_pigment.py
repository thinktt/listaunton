"""Bounded wood pigment estimate from measured illumination of the actual mesh."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/"scripts/queen"))
from image_math import blur
DATA = ROOT/"build/knight-mission/material-observations"


def run():
    source = np.load(DATA/"reference-display.npy")
    target = np.load(DATA/"reference-linear.npy")
    black = np.load(DATA/"black.npy")
    gray = np.load(DATA/"gray.npy")
    prior = np.load(DATA/"prior.npy")
    rgb = source[:,:,:3]
    weights = np.array([.2126,.7152,.0722],dtype=np.float32)
    response = np.maximum((gray[:,:,:3]-black[:,:,:3])/.16,.008)
    inferred = (target-black[:,:,:3])/response
    # A single exposure cannot separate color and glare everywhere. Constrain
    # the estimate to walnut chromaticities, then interpolate uncertain color
    # from nearby wood rather than turning reflections into white pigment.
    red = np.clip(inferred[:,:,0],.012,.59)
    pigment = np.stack((red,np.clip(inferred[:,:,1],red*.13,red*.43),
                            np.clip(inferred[:,:,2],red*.025,red*.16)),axis=-1)
    interior = (source[:,:,3]>.78) & (black[:,:,3]>.985) & (rgb.max(2)>.045)
    interior = np.asarray(Image.fromarray(np.uint8(interior)*255).filter(ImageFilter.MinFilter(9)))/255
    weight = interior.astype(np.float32)
    weight *= np.clip((.38-rgb.min(2))/.19,0,1)
    weight *= np.clip((.86-(black[:,:,:3]@weights)/np.maximum(target@weights,.008))/.59,0,1)
    weight *= np.clip(((rgb@weights)-.025)/.060,0,1)
    weight *= np.clip(((response@weights)-.04)/.18,0,1)
    yy,xx=np.indices(weight.shape)
    # Carved features ahead of the current geometry are not color marks.
    for x,y,rx,ry in [(507,480,48,21),(706,511,25,14)]:
        distance=((xx-x)/rx)**2+((yy-y)/ry)**2
        weight *= np.clip((distance-.45)/.9,0,1)
    # Smooth extension is used only where measurement is uncertain. Retain
    # fine directly observed pigment in the reliable interior.
    density=blur(weight,9,3)
    extended=blur(pigment*weight[:,:,None],9,3)/np.maximum(density[:,:,None],.0001)
    confidence=np.clip(density/.28,0,1)
    prior_color=prior[:,:,:3]
    filled=prior_color+(extended-prior_color)*confidence[:,:,None]
    result=filled+(pigment-filled)*weight[:,:,None]
    transfer=np.clip(interior*(.25+.73*np.maximum(weight,confidence*.76)),0,.98)
    np.save(DATA/"estimated-pigment.npy",result.astype(np.float32))
    np.save(DATA/"transfer-confidence.npy",transfer.astype(np.float32))
    report={"method":"Invert AgX, subtract measured black-BSDF response, divide by measured diffuse response. Bound pigment to wood colors and blend only on camera-visible surfaces. Eye and nostril cavities excluded from direct color estimation.",
            "source_sha256":hashlib.sha256((ROOT/"assets/knight/ref.png").read_bytes()).hexdigest(),
            "gray_calibration":.16,"foreground_pixels":int(interior.sum()),"direct_weight_mean":float(weight[interior>.9].mean()),
            "reference_modified":False,"caveat":"Local diffuse response and single-view light separation are approximate. Hidden surfaces use continuous wood."}
    (DATA/"inference.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    run()

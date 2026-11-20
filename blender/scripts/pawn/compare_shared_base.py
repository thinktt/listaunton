"""Compare real pawn trials with the native sprite at a common camera and floor."""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from audit_mission import ASSETS, ROOT, black, mask, registered, rgba
from compare_native import to_native

REGIONS={"head":(83,85,149,144),"collar_stem":(84,139,148,192),"base":(58,187,174,244)}
FEATURES={"ball_seat":(104,127,144.,.014,"dark"),"collar_front":(104,127,154.,.016,"fall"),
          "socket_front":(117,132,185.5,.016,"fall"),"foot_groove":(94,136,230.5,.0085,"dark")}

def landmark_curves(image,reference):
    ygray=np.asarray(black(image).convert("L").filter(ImageFilter.GaussianBlur(.7)),dtype=float)
    edge=np.gradient(ygray,axis=0)
    silhouette=mask(image,reference)
    center=115.5
    result={}
    for name,(x0,x1,y0,curve,kind) in FEATURES.items():
        loc=[]
        for x in range(x0,x1+1):
            expected=y0-curve*(x-center)**2
            ys=np.arange(round(expected)-7,round(expected)+8)
            samples=(ygray if kind=="dark" else edge)[ys,x]
            where=int(np.argmin(samples))
            # Subpixel minimum from the three nearest samples.
            row=float(ys[where])
            if 0<where<len(samples)-1:
                a,b,c=samples[where-1:where+2]
                if a-2*b+c>1e-8:
                    row+=float(np.clip((a-c)/(2*(a-2*b+c)),-.5,.5))
            loc.append(row)
        result[name]=loc
    result["ball_apex"]=[float(np.flatnonzero(silhouette[:,x])[0]) for x in range(111,120)]
    result["foot_bottom"]=[float(np.flatnonzero(silhouette[:,x])[-1]) for x in range(101,130)]
    head_x=np.where(silhouette[113])[0]
    result["ball_width"]=[float(head_x[-1]-head_x[0]+1)]
    return result

def score(image,original,reference=False):
    target=mask(original,True)
    measured=mask(image,reference)
    actual=np.asarray(black(image),float)
    expected=np.asarray(black(original),float)
    common=measured&target
    a=landmark_curves(original,True)
    b=landmark_curves(image,reference)
    features={}
    for key in a:
        delta=np.asarray(b[key])-a[key]
        features[key]={"mae_px":float(np.abs(delta).mean()),"bias_px":float(delta.mean()),
                       "native_position":float(np.median(b[key])),"reference_position":float(np.median(a[key]))}
    regions={}
    for key,(x0,y0,x1,y1) in REGIONS.items():
        box=np.s_[y0:y1,x0:x1]
        regions[key]=float(np.abs(actual[box]-expected[box])[common[box]].mean())
    return {"native_mask_iou":float((target&measured).sum()/(target|measured).sum()),
            "native_rgb_error":float(np.abs(actual-expected)[common].mean()),
            "region_errors":regions,"landmarks":features}

def side_tile(path,width,height,base_px):
    im=rgba(path)
    alpha=np.asarray(im)[:,:,3]>127
    yy=np.flatnonzero(alpha.any(axis=1))
    floor=yy[-1]+1
    widths=alpha.sum(axis=1)
    candidate_rows=np.arange(int(floor-(floor-yy[0])*.24),floor)
    strongest=candidate_rows[np.argmax(widths[candidate_rows])]
    xs=np.flatnonzero(alpha[strongest])
    center=(xs[-1]+xs[0]+1)/2
    scale=base_px/(xs[-1]-xs[0]+1)
    mat=(1/scale,0,center-width/(2*scale),0,1/scale,floor-(height-5)/scale)
    crop=im.transform((width,height),Image.Transform.AFFINE,mat,Image.Resampling.BICUBIC)
    background=Image.new("RGBA",crop.size,"#222526")
    background.alpha_composite(crop)
    return background.convert("RGB")

def font(size):
    paths=["C:/Windows/Fonts/segoeui.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    return next((ImageFont.truetype(p,size) for p in paths if Path(p).is_file()),ImageFont.load_default(size=size))

def run(cfg,out):
    out.mkdir(parents=True,exist_ok=True)
    baseline=ROOT/Path(cfg["source"]).parent
    original=rgba(ASSETS/"original.png")
    refs=registered()
    full_masks={k:mask(v,True) for k,v in refs.items()}
    align=json.loads((ASSETS/"original-alignment.json").read_text(encoding="utf-8"))
    dims=json.loads((baseline/"mission-validation.json").read_text(encoding="utf-8"))
    entries=[("Previously accepted",baseline/"render.png",baseline/"profile.png",dims["diameter"],dims["height"])]
    variants=[c["name"] for c in cfg["candidates"]]+cfg.get("lighting_variants",[])
    for name in variants:
        folder=ROOT/cfg["output"]/name
        if (folder/"geometry.json").exists():
            geom=json.loads((folder/"geometry.json").read_text(encoding="utf-8"))
            entries.append((name,folder/"fixed.png",folder/"side.png",geom["actual_diameter"],geom["actual_height"]))
    images=[("Original black",original),("Black candidate 2",to_native(refs["selected"],align))]
    results={}
    for name,fixed,side,width,height in entries:
        raw=rgba(fixed)
        native=to_native(raw,align)
        sm=mask(raw,False)
        results[name]=score(native,original)
        results[name].update(diameter=width,height=height,ratio=height/width,
                             fixed_iou={k:float((m&sm).sum()/(m|sm).sum()) for k,m in full_masks.items()})
        images.append((name,native))
    (out/"measurements.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    w=193;h=286
    plate=Image.new("RGB",(len(images)*w,h+35),"#202325")
    draw=ImageDraw.Draw(plate)
    for i,(name,im) in enumerate(images):
        draw.text((i*w+w//2,5),name,font=font(14),anchor="mt",fill="white")
        v=black(im).crop((53,80,177,250)).resize((w-3,h-23),Image.Resampling.LANCZOS)
        plate.paste(v,(i*w+1,28))
    plate.save(out/"fixed-trials.png")
    plate=Image.new("RGB",(len(entries)*w,361),"#202325")
    draw=ImageDraw.Draw(plate)
    # These images preserve the common camera's physical scale and pin the floor.
    # Only the separate donor plate normalizes foot diameter.
    for i,(name,_,path,width,height) in enumerate(entries):
        pos=i*w
        draw.text((pos+w//2,4),name,font=font(13),anchor="mt",fill="white")
        plate.paste(side_tile(path,w,307,142*width/dims["diameter"]),(pos,24))
        draw.text((pos+w//2,339),f"W {width:.3f}   H {height:.3f}",font=font(13),anchor="mt",fill="#ded3bd")
    plate.save(out/"side-trials.png")
    for key,v in results.items():
        fs=v["landmarks"]
        print(key,round(v["diameter"],4),round(v["height"],4),round(v["fixed_iou"]["original_black"]*100,2),
              round(v["native_rgb_error"],2),{k:round(f["bias_px"],2) for k,f in fs.items()},flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("config",type=Path)
    parser.add_argument("output",type=Path)
    parser.add_argument("--lighting-target",action="store_true",help="Also write the registered original for fitting Cycles lights.")
    args=parser.parse_args()
    config=json.loads(args.config.read_text(encoding="utf-8"))
    run(config,args.output)
    if args.lighting_target:
        target=np.asarray(black(registered()["original_black"]),np.float32)/255
        np.save(ROOT/config["output"]/"registered-original.npy",target)

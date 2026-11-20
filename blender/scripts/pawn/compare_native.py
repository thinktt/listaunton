"""Inspect the actual black pawn sprite at its native 300-pixel canvas size."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from audit_mission import ASSETS, BUILD, black, mask, rgba, sheet


def to_native(image, alignment):
    # This is the inverse of the immutable selected-candidate registration.
    # Supersample once, then integrate into native sprite pixels.
    s=alignment["scale"]*300/image.width
    dx,dy=alignment["x"]*3,alignment["y"]*3
    transform=(1/(4*s),0,-dx/s,0,1/(4*s),-dy/s)
    return image.transform((1200,1200),Image.Transform.AFFINE,transform,Image.Resampling.BICUBIC).resize((300,300),Image.Resampling.LANCZOS)


def compare(variant,previous):
    out=BUILD/variant
    alignment=json.loads((ASSETS/"original-alignment.json").read_text())
    original=rgba(ASSETS/"original.png")
    images={"Original black":original,"Selected black 2":to_native(rgba(ASSETS/"reference.png"),alignment),"Before":to_native(rgba(previous),alignment),"Trial":to_native(rgba(out/"fixed.png"),alignment)}
    s=alignment["scale"]*300/1254
    dx,dy=alignment["x"]*3,alignment["y"]*3
    outline=mask(original,True)
    y,x=np.nonzero(outline)
    box=(max(0,x.min()-6),max(0,y.min()-6),min(300,x.max()+7),min(300,y.max()+7))
    sheet(list(images.items()),box,220,out/"native-comparison.png")
    weights=np.array([.24,.53,.23])
    target=np.asarray(black(original),np.float32)
    summary={}
    for name,im in images.items():
        rgb=np.asarray(black(im),np.float32)
        luma=rgb@weights
        valid=outline&mask(im,name in ("Original black","Selected black 2"))
        entry={"common_rgb_mae_255":float(np.abs(rgb-target)[valid].mean()),"glints":{}}
        for label,px,py,rx,ry in (("left",461,451,16,15),("upper",509,435,20,19),("right",515,490,18,23)):
            xx,yy=np.meshgrid(np.arange(300),np.arange(300))
            area=(((xx-(px*s+dx))/(rx*s))**2+((yy-(py*s+dy))/(ry*s))**2)<1
            values=luma[area]
            excess=np.maximum(values-np.quantile(values,.5),0)
            entry["glints"][label]={"native_center_xy":[float(np.average(xx[area],weights=excess)),float(np.average(yy[area],weights=excess))],"native_90th_brightness":float(np.quantile(values,.9))}
        summary[name]=entry
    centers=summary["Original black"]["glints"]
    for entry in summary.values():
        for label,data in entry["glints"].items():
            data["center_error_original_pixels"]=float(np.linalg.norm(np.array(data["native_center_xy"])-centers[label]["native_center_xy"]))
    (out/"native-measurement.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf8")
    for name,item in summary.items():
        print(name,round(item["common_rgb_mae_255"],2),[round(q["center_error_original_pixels"],2) for q in item["glints"].values()])


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("variant")
    parser.add_argument("--previous",type=Path,default=ASSETS/"render.png")
    args=parser.parse_args()
    compare(args.variant,args.previous)

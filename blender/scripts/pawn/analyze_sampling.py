"""Check crop registration, sampling convergence and reproducible grain contrast."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from derive_wood import ROOT,blur

W=np.array([.24,.53,.23],np.float32)


def rgb(path):
    return np.asarray(Image.open(path).convert("RGB"),np.float32)


def run(trial,directory):
    record=json.loads((directory/"sampling.json").read_text())
    source=rgb(trial/"fixed.png")
    ref=rgb(ROOT/"assets/pawn/reference.png")
    seed=record["original_seed"]
    result={}
    for name,(x,y,_,_) in record["bounds_top_left"].items():
        low=rgb(directory/f"{name}-128-clean-{seed}.png")
        h,w=low.shape[:2]
        options=[]
        for dx in range(-2,3):
            for dy in range(-2,3):
                known=source[y+dy:y+dy+h,x+dx:x+dx+w]
                opts=np.abs(known-low)[6:-6,6:-6]
                options.append((float(opts.mean()),dx,dy))
        mae,dx,dy=min(options)
        assert abs(dx)<=1 and abs(dy)<=1,(name,dx,dy)
        x+=dx;y+=dy
        target=ref[y:y+h,x:x+w]
        key=lambda a:a[6:-6,6:-6].ravel()
        high=lambda a:(a@W)-blur(a@W,r=2,passes=2)
        target_hp=key(high(target))
        seed2=rgb(directory/f"{name}-768-clean-{seed+31}.png")
        values={}
        for samples,style,s in [(128,"clean",seed),(512,"clean",seed),(768,"clean",seed),(768,"clean",seed+31),(768,"raw",seed)]:
            im=rgb(directory/f"{name}-{samples}-{style}-{s}.png")
            hp=key(high(im))
            values[f"{samples}-{style}-{s}"]={"mae_to_reference":round(float(np.abs(key(im-target)).mean()),3),"rms_fine_contrast":round(float(np.sqrt(np.mean(hp**2))),3),"fine_correlation_to_reference":round(float(np.corrcoef(hp,target_hp)[0,1]),4),"mae_to_768_other_seed":round(float(np.abs(key(im-seed2)).mean()),3)}
        result[name]={"registered_xy":[x,y],"crop_dimensions":[w,h],"128_full_vs_crop_mae":round(mae,3),"reference_fine_contrast":round(float(np.sqrt(np.mean(target_hp**2))),3),"checks":values}
    (directory/"sampling-comparison.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    for k,r in result.items():
        print(k,r["registered_xy"],r["128_full_vs_crop_mae"],r["reference_fine_contrast"],r["checks"])


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("trial");p.add_argument("measurement")
    a=p.parse_args();b=ROOT/"build/pawn-mission";run(b/a.trial,b/a.measurement)

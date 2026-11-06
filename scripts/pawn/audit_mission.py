"""Compare an actual pawn trial at its registered coordinates. Run in ordinary Python."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts/queen"))
from overlay_qa import largest_component, fill_holes

ASSETS = ROOT/"assets/pawn"
BUILD = ROOT/"build/pawn-mission"
REGIONS = {"head":(353,340,618,601), "collar-stem":(345,524,631,782), "base-foot":(252,703,716,1014)}
FULL = (245,330,723,1018)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rgba(path):
    return Image.open(path).convert("RGBA")

def registered():
    ref = rgba(ASSETS/"reference.png")
    a = json.loads((ASSETS/"original-alignment.json").read_text())
    src = json.loads((ROOT/"assets/candidates/alignment.json").read_text())["pieces"]["pawn"]
    reg = next(item for item in src if item["id"]=="white")
    step,dx,dy = a["scale"]*300/ref.width, a["x"]*3, a["y"]*3
    def place(im,s,x,y):
        return im.transform(ref.size,Image.Transform.AFFINE,(s,0,x,0,s,y),Image.Resampling.BILINEAR)
    original = place(rgba(ASSETS/"original.png"),step,dx,dy)
    white = place(rgba(ASSETS/"white-original.png"),step/reg["scale"],(dx-reg["x"]*3)/reg["scale"],(dy-reg["y"]*3)/reg["scale"])
    return {"selected":ref,"original_black":original,"original_white":white}

def mask(im,reference):
    a = np.asarray(im)
    m = a[:,:,3]>127
    if reference: m &= a[:,:,:3].max(axis=2)>12
    ys,xs = np.nonzero(m)
    window = np.s_[ys.min():ys.max()+1,xs.min():xs.max()+1]
    result=np.zeros_like(m)
    result[window]=fill_holes(largest_component(m[window]))
    return result

def black(im):
    return Image.alpha_composite(Image.new("RGBA",im.size,(0,0,0,255)),im).convert("RGB")

def sheet(items,box,width,path):
    height=round((box[3]-box[1])/(box[2]-box[0])*width)
    canvas=Image.new("RGB",((width+8)*len(items)+8,height+44),(22,24,27))
    draw=ImageDraw.Draw(canvas)
    fontpath=Path("C:/Windows/Fonts/segoeui.ttf")
    font=ImageFont.truetype(str(fontpath),18) if fontpath.is_file() else ImageFont.load_default(size=18)
    for i,(label,image) in enumerate(items):
        x=8+(width+8)*i
        draw.text((x,7),label,font=font,fill="#edebe6")
        canvas.paste(black(image).crop(box).resize((width,height),Image.Resampling.LANCZOS),(x,36))
    canvas.save(path)

def audit(directory, previous):
    trial=rgba(directory/"fixed.png")
    refs=registered()
    tm=mask(trial,False)
    results={}
    for key,image in refs.items():
        m=mask(image,True)
        results[key]=float((tm&m).sum()/(tm|m).sum())
    ref=refs["selected"]
    rs=np.asarray(ref,dtype=float)[:,:,:3]; ts=np.asarray(trial,dtype=float)[:,:,:3]
    roi=tm&mask(ref,True)
    regions={}
    for name,(x0,y0,x1,y1) in REGIONS.items():
        valid=roi[y0:y1,x0:x1]
        delta=np.abs(rs[y0:y1,x0:x1]-ts[y0:y1,x0:x1])[valid]
        regions[name]={"mean_absolute_rgb_error_255":float(delta.mean()),"overlap_pixels":int(valid.sum())}
    # Rank separated foreground patches so a good average cannot conceal
    # a missing reflection, displaced turning or localized color cast.
    error=np.abs(rs-ts).mean(2)
    tiles=[]
    x0,y0,x1,y1=FULL
    for y in range(y0,y1-31,12):
        for x in range(x0,x1-31,12):
            valid=roi[y:y+32,x:x+32]
            if valid.mean()>=.86:
                tiles.append((float(error[y:y+32,x:x+32][valid].mean()),x,y))
    worst=[]
    for value,x,y in sorted(tiles,reverse=True):
        if any(abs(x-item["xy"][0])<36 and abs(y-item["xy"][1])<36 for item in worst):
            continue
        worst.append({"xy":[x,y],"size":32,"mean_absolute_rgb_error_255":round(value,3)})
        if len(worst)==8:
            break
    prev=rgba(previous)
    items=[("Selected black 2",ref),("Previous model",prev),("Trial "+directory.name.split("-")[0],trial)]
    sheet(items,FULL,330,directory/"comparison.png")
    for name,box in REGIONS.items():sheet(items,box,330,directory/(name+".png"))
    sheet([("Original black",refs["original_black"]),("Selected black 2",ref),("Model",trial)],FULL,330,directory/"original-comparison.png")
    for name in ["selected","original_black"]:
        Image.blend(black(refs[name]),black(trial),.5).crop(FULL).save(directory/("overlay-"+name+".png"))
    result={"trial":directory.name,"iou":results,"regions":regions,"render_sha256":sha(directory/"fixed.png"),"model_sha256":sha(directory/"pawn.blend"),"previous_render_sha256":sha(previous),"reference_sha256":sha(ASSETS/"reference.png"),"original_sha256":sha(ASSETS/"original.png"),"camera_assumption_above_board":54,"method":"Fixed registration. Foreground alpha >127 and reference max RGB >12. Largest component, filled holes. RGB errors only on common foreground."}
    result["largest_local_residuals"]=worst
    (directory/"metrics.json").write_text(json.dumps(result,indent=2)+"\n")
    print(directory.name,results,flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("variants",nargs="+")
    p.add_argument("--previous",default="assets/pawn/render.png")
    args=p.parse_args()
    for variant in args.variants:audit(BUILD/variant,ROOT/args.previous)

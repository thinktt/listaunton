"""Measure both silhouettes at the same 54° registration and make a side comparison."""
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from compare_socket_flare import registered_original
from overlay_qa import largest_component, fill_holes

def mask(im,reference=False):
    a=np.asarray(im.convert("RGBA"))
    valid=a[:,:,3]>127
    if reference:
        valid &= a[:,:,:3].max(2)>12
    return fill_holes(largest_component(valid))

def main():
    assets=ROOT/"assets/queen-base-studies"
    highres=Image.open(ROOT/"assets/queen/reference.png")
    refs={"lichess_black":mask(registered_original(),True),"selected_highres":mask(highres,True)}
    ids=[("socket","Raised socket"),("compressed","Raised socket · 12% compressed")]
    box=(132,532,468,805)
    w,h=box[2]-box[0],box[3]-box[1]
    sheet=Image.new("RGB",(len(ids)*w+(len(ids)-1)*6,h+34),"#141820")
    draw=ImageDraw.Draw(sheet)
    font=ImageFont.load_default(size=17)
    result={}
    for i,(key,label) in enumerate(ids):
        shape=mask(Image.open(assets/key/"fixed-wood.png"))
        result[key]={}
        for source,ref in refs.items():
            intersection=shape&ref
            union=shape|ref
            result[key][source]={"full_iou":float(intersection.sum()/union.sum()),
                                 "below_row_570_iou":float(intersection[570:].sum()/union[570:].sum())}
        x=i*(w+6)
        draw.text((x+8,5),label,font=font,fill="white")
        pic=Image.open(assets/key/"side-wood.png").convert("RGBA")
        crop=Image.alpha_composite(Image.new("RGBA",pic.size,(8,10,13,255)),pic).convert("RGB").crop(box)
        sheet.paste(crop,(x,34))
    sheet.save(assets/"side-comparison.png")
    report={"camera_degrees_above_board":54,"silhouettes":result,
            "method":"Fixed registration. Intersection divided by union of foreground pixels, using the queen mission's reference and render masks."}
    (assets/"comparison.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()

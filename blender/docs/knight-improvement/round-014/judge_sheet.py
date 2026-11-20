"""Collect registered, identically cropped evidence for a three-way decision."""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
from PIL import Image, ImageDraw, ImageOps

p=argparse.ArgumentParser()
p.add_argument("root",type=Path)
p.add_argument("round",type=int)
p.add_argument("names",nargs="*")
a=p.parse_args()
root=a.root.resolve()
assets=root/"assets/knight"
sys.path.insert(0,str(root/"scripts/knight"))
from audit_mission import registered,black
refs=registered()
build=root/"build/knight-mission"
out=build/f"round-{a.round:03}-judge"
out.mkdir(exist_ok=True)
sources=[("Original",refs["original"],None),("Black 2",refs["selected"],None),
         ("Parent",Image.open(assets/"render.png"),Image.open(assets/"guide-render.png"))]
for name in a.names:
    folder=build/f"improvement-{a.round:03}-{name}"
    sources.append((name,Image.open(folder/"wood.png"),Image.open(folder/"wood-side.png")))
def sheet(name,panels,box,size):
    w,h=size
    img=Image.new("RGB",(w*len(panels),h+27),"#191917")
    d=ImageDraw.Draw(img)
    for i,(title,im) in enumerate(panels):
        d.text((i*w+8,6),title,fill="#f1ebdf")
        crop=black(im.convert("RGBA")).crop(box)
        img.paste(crop.resize(size,Image.Resampling.LANCZOS),(i*w,26))
    img.save(out/(name+".png"))
for name,box,size,view in [
    ("fixed",(160,250,805,1090),(220,287),1),
    ("head",(175,270,785,575),(320,160),1),
    ("side",(215,100,990,1154),(270,367),2),
    ("side-face",(270,112,955,605),(300,216),2)]:
    sheet(name,[(s[0],s[view]) for s in sources if s[view] is not None],box,size)
stats={}
target=np.array(refs["selected"].convert("RGBA"),dtype=np.int16)
for label,im,_ in sources[2:]:
    arr=np.asarray(im.convert("RGBA"),dtype=np.int16)
    mask=(arr[:,:,3]>245)&(target[:,:,3]>245)
    for region,(l,t,r,b) in {"foreground":(0,0,1254,1254),"head":(190,280,758,560),"eye":(440,425,612,523),"muzzle":(560,405,760,565)}.items():
        m=mask[t:b,l:r]
        stats.setdefault(label,{})[region]=round(float(np.abs(arr[t:b,l:r,:3]-target[t:b,l:r,:3])[m].mean()),3)
(out/"regional-error.json").write_text(json.dumps(stats,indent=2)+"\n")
print(stats)

"""Compare registered pedestal contours, turned edges, pigment and side profile."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw

from audit_mission import black,registered
from measure_pedestal_arcs import FEATURES,strongest_arc

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"build/knight-mission";ASSETS=ROOT/"assets/knight"


def main():
    p=argparse.ArgumentParser();p.add_argument("variant");p.add_argument("--previous",required=True)
    args=p.parse_args();trial=BUILD/args.variant;prior=BUILD/args.previous
    refs=registered()
    images=[refs["original"],refs["selected"],Image.open(prior/"render.png").convert("RGBA"),Image.open(trial/"wood.png").convert("RGBA")]
    labels=["Original black","Selected black 2","Prior accepted","Trial "+args.variant.split("-")[0]]
    sheet=Image.new("RGB",(1056,328),"#181b1d");draw=ImageDraw.Draw(sheet)
    for i,(im,label) in enumerate(zip(images,labels)):
        x=264*i;draw.text((x+3,3),label,fill="white")
        for y,box,size in [(19,(212,665,777,1060),(258,181)),(210,(354,810,626,887),(258,72)),(287,(365,980,628,1019),(258,38))]:
            patch=black(im).crop(box).resize(size,Image.Resampling.LANCZOS)
            sheet.paste(patch,(x+2,y))
    sheet.save(trial/"pedestal-comparison.png")
    sides=[Image.open(ASSETS/"concepts/side-01.png").convert("RGBA"),Image.open(prior/"guide-render.png").convert("RGBA"),Image.open(trial/"wood-side.png").convert("RGBA")]
    sheet=Image.new("RGB",(822,182),"#191b1e");draw=ImageDraw.Draw(sheet)
    for i,(im,label) in enumerate(zip(sides,["Imagined side guide","Previous","Turned profile"])):
        patch=im.crop((319,801,930,1141));patch.thumbnail((268,152),Image.Resampling.LANCZOS)
        sheet.paste(patch,(i*274+2,21),patch);draw.text((i*274+4,4),label,fill="white")
    sheet.save(trial/"pedestal-side.png")
    ref,prev,now=[np.asarray(f,dtype=np.float32) for f in images[1:]]
    common=(ref[:,:,3]>245)&(prev[:,:,3]>245)&(now[:,:,3]>245);y,x=np.indices(common.shape)
    stats={}
    for label,part in [("foreground",np.ones_like(common)),("pedestal",y>788),
                       ("collar",((x-492)/212)**2+((y-695)/180)**2<1.07),
                       ("front_collar",(y>817)&(y<887)&(x>330)&(x<660)),
                       ("foot",(y>960)&(y<1035))]:
        mask=common&part
        stats[label]={key:float(np.abs(image[:,:,:3]-ref[:,:,:3])[mask].mean()) for key,image in [("prior_mae_255",prev),("trial_mae_255",now)]}
    (trial/"feature-error.json").write_text(json.dumps(stats,indent=2)+"\n")
    report={}
    for name,(radii,fronts,band) in FEATURES.items():
        all_fits={}
        for label,im in zip(["original","selected","previous","trial"],images):
            c,cx,r,front=strongest_arc(im,radii,fronts,band,np.linspace(-.85,.85,79))
            all_fits[label]={"x":cx,"radius":r,"front_row":front,"contrast":c}
        report[name]=all_fits
    (trial/"arc-fit.json").write_text(json.dumps(report,indent=2)+"\n")
    print(args.variant,{k:round(v["trial_mae_255"],2) for k,v in stats.items()},
        {k:(v["trial"]["radius"],v["trial"]["front_row"]) for k,v in report.items()})


if __name__=="__main__":main()

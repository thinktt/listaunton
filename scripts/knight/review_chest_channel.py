"""Register and compare the chest carving, wood, reflections and side profile."""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image,ImageDraw

from audit_mission import black,registered
from locate_chest_channel import GUIDE
from refit_face_pigment import sample

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"assets/knight";BUILD=ROOT/"build/knight-mission"


def main():
    p=argparse.ArgumentParser();p.add_argument("trial");p.add_argument("--previous",required=True)
    p.add_argument("--paths",type=Path,required=True);a=p.parse_args()
    trial=BUILD/a.trial;prev=BUILD/a.previous;source=registered()
    sources=[source["original"],source["selected"],Image.open(prev/"render.png").convert("RGBA"),
             Image.open(trial/"wood.png").convert("RGBA")]
    paths=json.loads(a.paths.read_text())["curves"]
    sheet=Image.new("RGB",(1024,431),"#191b1d");draw=ImageDraw.Draw(sheet)
    yy,off=np.mgrid[548:744,-106:96];cx=np.interp(yy,GUIDE[:,1],GUIDE[:,0])
    for i,(im,label) in enumerate(zip(sources,["Original black","Selected black 2","Prior accepted","Trial "+a.trial.split("-")[0]])):
        x=256*i
        draw.text((x+3,4),label,fill="white")
        img=black(im);patch=img.crop((272,504,714,815)).resize((250,176),Image.Resampling.LANCZOS)
        sheet.paste(patch,(x+2,21))
        array=np.asarray(img,float)
        part=np.stack([sample(array[:,:,k],cx+off,yy) for k in range(3)],2)
        sheet.paste(Image.fromarray(np.uint8(part)),(x+24,212))
    draw.text((4,414),"Lower row follows the near chest ridge from the throat to its rounded termination.",fill="#c3c9cd")
    sheet.save(trial/"chest-study.png")
    side_images=[Image.open(ASSETS/"concepts/side-01.png").convert("RGBA"),Image.open(prev/"guide-render.png").convert("RGBA"),Image.open(trial/"wood-side.png").convert("RGBA")]
    sheet=Image.new("RGB",(834,279),"#191b1e");draw=ImageDraw.Draw(sheet)
    for i,(im,label) in enumerate(zip(side_images,["Imagined side guide","Previous","Trial"])):
        cut=im.crop((314,365,902,878));cut.thumbnail((270,249),Image.Resampling.LANCZOS)
        sheet.paste(cut,(278*i+3,20),cut);draw.text((278*i+4,4),label,fill="white")
    sheet.save(trial/"chest-side.png")
    ref,previous,test=[np.asarray(im,dtype=float) for im in sources[1:]]
    y,x=np.indices(ref.shape[:2]);base=np.interp(y,GUIDE[:,1],GUIDE[:,0]);offset=x-base
    mask=(ref[:,:,3]>245)&(previous[:,:,3]>245)&(test[:,:,3]>245)
    regions={"foreground":np.ones_like(mask),"chest":(y>549)&(y<753)&(offset>-112)&(offset<93),
             "shoulder":(y>590)&(y<714)&(offset>-94)&(offset<-43),"panel":(y>571)&(y<724)&(offset>15)&(offset<63)}
    intensities={}
    for name,pts in paths.items():
        co=np.array([r["pixel"] for r in pts]);center=np.interp(y,co[:,1],co[:,0])
        line=(y>=608)&(y<=698)&(np.abs(x-center)<=3);regions[name+"_line"]=line
        intensities[name]={k:float(im[:,:,1][mask&line].mean()) for k,im in [("selected",ref),("previous",previous),("trial",test)]}
    stats={}
    for name,part in regions.items():
        pick=mask&part
        stats[name]={key:float(np.abs(im[:,:,:3]-ref[:,:,:3])[pick].mean()) for key,im in [("prior_mae_255",previous),("trial_mae_255",test)]}
    (trial/"feature-error.json").write_text(json.dumps(stats,indent=2)+"\n")
    (trial/"channel-intensity.json").write_text(json.dumps(intensities,indent=2)+"\n")
    print(a.trial,{k:round(stats[k]["trial_mae_255"],2) for k in ("foreground","chest","shoulder","trough_line","crest_line")})


if __name__=="__main__":main()

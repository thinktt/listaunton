"""Estimate visible front arcs of the turned foot and collar at the fixed camera.

Each arc is only an observed photometric landmark. Radius and physical height
are inferred from the known camera and should be checked on actual geometry.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from audit_mission import registered
from refit_face_pigment import sample

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"assets/knight"
FEATURES={"collar":(np.arange(196,235,2),np.arange(854,884,1),5),
          "foot":(np.arange(232,267,2),np.arange(985,1025,1),5)}


def strongest_arc(image,radii,fronts,band,orientations):
    a=np.asarray(image.convert("RGB"),np.float32)/255
    luma=np.log(.025+a@np.array([.24,.64,.12],np.float32))
    s=np.sin(np.deg2rad(54))
    scores=[]
    for cx in np.arange(482,506,2):
        for radius in radii:
            x=cx+radius*orientations[None,:]
            y=fronts[:,None]-radius*s*(1-np.sqrt(1-orientations[None,:]**2))
            mid=sample(luma,x,y)
            contrast=mid-.5*(sample(luma,x,y-band)+sample(luma,x,y+band))
            # Trim a few speckles or directional lamp edges that happen to
            # intersect the arc. Use evidence from a substantial front sector.
            score=np.sort(contrast,axis=1)[:,5:-5].mean(axis=1)
            i=score.argmax()
            scores.append((float(score[i]),float(cx),float(radius),float(fronts[i])))
    return max(scores)


def main():
    p=argparse.ArgumentParser();p.add_argument("out",type=Path);args=p.parse_args()
    cam=json.loads((ASSETS/"camera.json").read_text())
    vp=np.reshape(cam["projectionMatrix"],(4,4))@np.reshape(cam["worldToCamera"],(4,4))
    sy=(1-vp[1,3])*627;scale=1254/cam["orthoScale"]
    refs=registered();refs["current"]=Image.open(ASSETS/"render.png").convert("RGBA")
    report={}
    for name,(radii,fronts,band) in FEATURES.items():
        report[name]={}
        for source,img in refs.items():
            sector=np.linspace(-.85,.85,79)
            score,cx,r,front=strongest_arc(img,radii,fronts,band,sector)
            z=(sy+r*np.sin(np.deg2rad(54))-front)/(scale*np.cos(np.deg2rad(54)))
            report[name][source]={"center_x":cx,"radius_pixels":r,"front_y":front,"radius_world":r/scale,
                                  "height_world_at_bright_edge":float(z),"trimmed_log_contrast":score}
    args.out.parent.mkdir(exist_ok=True,parents=True);args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()

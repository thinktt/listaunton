"""Compare sampled brightness across the true front occlusion edge in registered views."""
import argparse
import json
from pathlib import Path

import numpy as np
from audit_mission import ASSETS,BUILD,black,registered,rgba,sheet
from derive_wood import sample

W=np.array([.24,.53,.23])


def run(study,geometry,variants,out):
    data=json.loads(study.read_text())
    pts=np.asarray(data["edge_xy"][geometry])
    pts=pts[(pts[:,0]>=434)&(pts[:,0]<=529)]
    offsets=np.arange(-6,11.01,.25)
    x=pts[:,0][None,:];y=pts[:,1][None,:]+offsets[:,None]
    images=registered()
    images.update({v:rgba(BUILD/v/"fixed.png") for v in variants})
    curves={}
    for name,im in images.items():
        brightness=np.asarray(black(im),np.float32)@W
        values=sample(brightness,x,y)
        curves[name]=np.median(values,axis=1)
    target=curves["selected"]
    records={}
    for name,c in curves.items():
        core=(offsets>=-2)&(offsets<=4)
        records[name]={"darkest_core_level":round(float(c[core].min()),2),
                       "darkest_core_offset":float(offsets[core][c[core].argmin()]),
                       "level_at_six_pixels":round(float(c[offsets==6][0]),2),
                       "rmse_to_selected_curve":round(float(np.sqrt(np.mean((c-target)**2))),2),
                       "median_brightness_curve":c.round(3).tolist()}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"geometry":geometry,"edge_offsets_pixels":offsets.tolist(),"records":records},indent=2)+"\n",encoding="utf8")
    sheet([("Selected black 2",images["selected"]),("Previous",rgba(ASSETS/"render.png")),("Trial",images[variants[-1]])],(401,546,565,632),360,out.with_suffix(".png"))
    print({k:(v["darkest_core_level"],v["level_at_six_pixels"],v["rmse_to_selected_curve"]) for k,v in records.items()})


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("study",type=Path);p.add_argument("geometry")
    p.add_argument("output",type=Path);p.add_argument("variants",nargs="+")
    a=p.parse_args()
    run(a.study,a.geometry,a.variants,a.output)

"""Locate the carved chest features in both registered black references."""
from pathlib import Path
import argparse
import json

import numpy as np

from audit_mission import registered
from lower_carving_fit import rest_coords
from probe_reflections import surface_probe
from refit_face_pigment import sample

GUIDE=np.array([(392,538),(413,565),(432,585),(450,605),(473,625),(493,645),
                (514,665),(533,685),(551,700),(571,723),(600,745)])


def locate(mesh,output,trim_shoulder=False):
    probe,digest=surface_probe(mesh)
    refs=registered()
    images=[np.asarray(refs[name].convert("RGB"),float)[:,:,1] for name in ("original","selected")]
    pose_data=Path(__file__).resolve().parents[2]/"docs/knight-mission/iteration-001/001-carving-pose-pose.json"
    cfg=json.loads(pose_data.read_text());pose=[cfg[k] for k in ("dx","dy","twist_degrees")]
    shape=json.loads((mesh/"mesh.json").read_text())
    base=next(p for p in shape["parts"] if p["name"].endswith("turned pedestal"))
    data=np.fromfile(mesh/"mesh.bin",dtype="<f4",count=shape["vertexCount"]*8).reshape(-1,8)
    idx=base["vertexOffset"];foot=data[idx:idx+base["vertexCount"],0]
    foot_center=float((foot.max()+foot.min())*.5)
    curves={k:[] for k in ("trough","bevel","crest","shoulder","panel","far_lip")}
    rows=np.arange(555,736,12);trace={k:[] for k in curves}
    for y in rows:
        yy,off=np.mgrid[y-3:y+4,-110:102]
        cx=np.interp(yy,GUIDE[:,1],GUIDE[:,0])
        profiles=[np.convolve(sample(im,cx+off,yy).mean(0),np.ones(5)/5,"same") for im in images]
        profiles=[(v-v.min())/max(float(np.ptp(v)),1.) for v in profiles]
        p=.68*profiles[0]+.32*profiles[1]
        def at(lo,hi,direction):
            return lo+int(np.argmax(direction*p[110+lo:111+hi]))
        base_center=float(np.interp(y,GUIDE[:,1],GUIDE[:,0]))
        trough=at(-56,-11,-1);crest=at(-9,9,1);far=at(60,87,1)
        offsets={"trough":trough,"bevel":.54*trough+.46*crest,"crest":crest,
                 "shoulder":at(-89,min(-42,trough-10),1),"panel":.45*crest+.55*far,"far_lip":far}
        for name,delta in offsets.items():trace[name].append(base_center+delta)
    for name in curves:
        measured=np.array(trace[name])
        smooth=np.convolve(np.pad(measured,(2,2),mode="edge"),[.08,.20,.44,.20,.08],"valid")
        # Preserve end positions rather than pushing endpoints toward the interior.
        smooth[0]=measured[0];smooth[-1]=measured[-1]
        for x,y in zip(smooth,rows):
            if trim_shoulder and name=="shoulder" and y<575:continue
            hit=probe(int(round(x)),int(y))
            if not hit or not hit["part"].endswith("continuous horse head and neck"):continue
            point=np.asarray([hit["position"]]);z=point[0,2];u=np.clip((2.48-z)/.72,0,1)
            point[0,0]-=foot_center*u*u*(3-2*u)
            rest=rest_coords(point,pose)[0]
            curves[name].append({"pixel":hit["pixel"],"rest":rest.tolist()})
        assert len(curves[name])>=10
    info={"source_sha256":digest,"pose":pose,"foot_center_x":foot_center,"curves":curves,
          "method":"Straighten the source's diagonal chest strip, bracket each dark channel and bright bevel, and smooth their observed paths. Weight original black 68% and selected black candidate 2 32%. Trace those paths onto the existing near flank for bilateral physical carving."}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(info,indent=2)+"\n")
    print({k:len(v) for k,v in curves.items()},foot_center)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mesh",type=Path);p.add_argument("output",type=Path)
    p.add_argument("--trim-shoulder",action="store_true",help="Omit weak shoulder landmarks under the jaw where the inferred side curve turns back.")
    args=p.parse_args();locate(args.mesh,args.output,args.trim_shoulder)

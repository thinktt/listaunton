"""Fit the lower mane and neck in depth while locking camera, height and base."""
from pathlib import Path
import json
import numpy as np

from mission_pose import posed,bend_weight

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"assets/knight"
ARCHIVE=ROOT/"history/knight/mission-001"
OUT=ROOT/"build/knight-mission/012-lower-carving"


def ease(z,low,high):
    t=np.clip((z-low)/(high-low),0,1)
    return t*t*(3-2*t)


def rest_coords(points,pose):
    r=points.copy();w=bend_weight(r[:,2]);angle=np.radians(pose[2])*w
    x=r[:,0]-w*pose[0];y=r[:,1]-w*pose[1]
    r[:,0]=np.cos(angle)*x+np.sin(angle)*y
    r[:,1]=-np.sin(angle)*x+np.cos(angle)*y
    return r


def lower_offset(points, mane, params):
    forward,thickness,rear=params
    z=points[:,2]
    w=ease(z,1.63,2.22)*(1-ease(z,3.20,4.10))
    points=points.copy()
    points[:,1] += w*(-forward + thickness*points[:,1]*mane)
    points[:,0] -= rear*w*mane
    return points


def main():
    from PIL import Image
    meta=json.loads((ARCHIVE/"mesh.json").read_text())
    cam=meta["referenceCamera"]
    m=np.asarray(cam["projectionMatrix"]).reshape(4,4)@np.asarray(cam["worldToCamera"]).reshape(4,4)
    raw=np.fromfile(ARCHIVE/"mesh.bin",dtype="<f4",count=meta["vertexCount"]*8).reshape(-1,8)
    pose_cfg=json.loads((ROOT/"docs/knight-mission/iteration-001/001-carving-pose-pose.json").read_text())
    pose=[pose_cfg["dx"],pose_cfg["dy"],pose_cfg["twist_degrees"]]
    points=[];mane_rows=[];fixed=[]
    def project(p):return (p@m[:2,:3].T+m[:2,3])*[627,-627]+627
    for part in meta["parts"]:
        i=part["vertexOffset"];xyz=raw[i:i+part["vertexCount"],:3]
        if "pedestal" in part["name"] or "eye" in part["name"] or "ear" in part["name"]:
            fixed.append(project(xyz));continue
        r=rest_coords(xyz,pose);points.append(r);mane_rows.extend(["mane" in part["name"]]*len(r))
    fixed=np.concatenate(fixed);points=np.concatenate(points);mane=np.array(mane_rows)
    align=json.loads((ASSETS/"original-alignment.json").read_text());s=align["scale"]*300/1254
    original=Image.open(ASSETS/"original.png").convert("RGBA").transform((1254,1254),Image.Transform.AFFINE,
       (s,0,align["x"]*3,0,s,align["y"]*3),Image.Resampling.BILINEAR)
    rows=np.arange(535,703,4)
    def edges(image):
        a=np.array(image.convert("RGBA"));mask=(a[:,:,3]>127)&(a[:,:,:3].max(2)>12)
        return np.column_stack((mask.argmax(1)[rows],1253-mask[:,::-1].argmax(1)[rows]))
    target=.82*edges(original)+.18*edges(Image.open(ASSETS/"ref.png"))
    def loss(params):
        moved=posed(lower_offset(points,mane,params),*pose)
        uv=np.vstack((fixed,project(moved)))
        ids=np.floor((uv[:,1]-rows[0]+2)/4).astype(int)
        ok=(ids>=0)&(ids<len(rows));left=np.full(len(rows),np.inf);right=-left.copy()
        np.minimum.at(left,ids[ok],uv[ok,0]);np.maximum.at(right,ids[ok],uv[ok,0])
        error=np.mean(np.abs(np.column_stack((left,right))-target))
        # Prefer depth changes to side-profile displacement. Penalize
        # disproportionate mane width even when its outline score improves.
        return float(error+2*abs(params[0])+2.7*abs(params[1])+10*abs(params[2]))
    p=np.zeros(3);base=best=loss(p)
    for step in [(.09,.20,.04),(.035,.075,.015),(.014,.03,.006)]:
        for _ in range(10):
            old=best
            for j,d in enumerate(step):
                for sign in (-1,1):
                    q=p.copy();q[j]+=d*sign
                    if np.any(q<0) or np.any(q>[.42,1.20,.135]):continue
                    val=loss(q)
                    if val<best-.001:p,best=q,val
            if best==old:break
    OUT.mkdir(parents=True,exist_ok=True)
    report={"forward":float(p[0]),"mane_width_gain":float(p[1]),"mane_rear_offset":float(p[2]),
            "baseline_loss":base,"proxy_loss":best,"row_range":[535,699],"original_weight":.82,
            "purpose":"Bring the lower mane forward and fill its prematurely narrowing elevated outline. Lock Z, floor, upper head, pedestal and reference registration. Validate actual fixed and side renders."}
    (OUT/"fit.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()

"""Trace observed highlights onto the exported carving and infer mirror rays."""
from pathlib import Path
import argparse
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"assets/knight"
BUILD=ROOT/"build/knight-mission"

FEATURES={
    "chest_crest":[(432,585),(450,605),(473,625),(493,645),(514,665),(533,685),(551,700)],
    "chest_far":[(497,565),(514,585),(531,605),(547,625),(566,645),(583,665),(600,685)],
    "chest_flank":[(403,605),(416,625),(429,645),(437,665),(447,678)],
}


def surface_probe(assets):
    data=json.loads((assets/"mesh.json").read_text())
    blob=(assets/"mesh.bin").read_bytes()
    vertices=np.frombuffer(blob[:data["vertexByteLength"]],dtype="<f4").reshape(-1,data["vertexStrideBytes"]//4)
    index=np.frombuffer(blob[data["indexByteOffset"]:],dtype="<u4").reshape(-1,3)
    xyz=vertices[:,:3].astype(float)
    camera=data["referenceCamera"]
    view=np.reshape(camera["worldToCamera"],(4,4));proj=np.reshape(camera["projectionMatrix"],(4,4))
    camera_xyz=xyz@view[:3,:3].T+view[:3,3]
    ndc=camera_xyz@proj[:3,:3].T+proj[:3,3]
    screen=np.column_stack(((1+ndc[:,0])*camera["width"]/2,(1-ndc[:,1])*camera["height"]/2))
    xy=screen[index]
    left=xy.min(axis=1);right=xy.max(axis=1)
    part_starts=np.array([p["indexOffset"]//3 for p in data["parts"]])
    def probe(x,y):
        q=np.array([x+.5,y+.5])
        ids=np.where(((left<=q)&(right>=q)).all(axis=1))[0]
        if not len(ids):return None
        a=xy[ids,0];ab=xy[ids,1]-a;ac=xy[ids,2]-a;offset=q-a
        cross=lambda p,r:p[:,0]*r[:,1]-p[:,1]*r[:,0]
        area=cross(ab,ac);area[np.abs(area)<1e-12]=np.nan
        u=cross(offset,ac)/area;v=cross(ab,offset)/area
        bary=np.column_stack((1-u-v,u,v))
        inside=np.all(bary>=-1e-9,axis=1)
        if not np.any(inside):return None
        ids=ids[inside];bary=bary[inside]
        hit=(bary*camera_xyz[index[ids],2]).sum(axis=1).argmax()
        tri=ids[hit];vertex_ids=index[tri]
        point=bary[hit]@xyz[vertex_ids]
        normal=bary[hit]@vertices[vertex_ids,3:6]
        normal/=np.linalg.norm(normal)
        toward_camera=view[2,:3]
        mirror=2*np.dot(normal,toward_camera)*normal-toward_camera
        part=data["parts"][np.searchsorted(part_starts,tri,side="right")-1]["name"]
        return {"pixel":[x,y],"part":part,"position":point.tolist(),"normal":normal.tolist(),"mirror":mirror.tolist()}
    return probe,data["sourceSha256"]


def main():
    p=argparse.ArgumentParser();p.add_argument("output",type=Path)
    args=p.parse_args()
    probe,digest=surface_probe(ASSETS)
    result={group:[probe(x,y) for x,y in samples] for group,samples in FEATURES.items()}
    args.output.parent.mkdir(exist_ok=True,parents=True)
    args.output.write_text(json.dumps({"source_sha256":digest,"features":result},indent=2)+"\n")
    for group,samples in result.items():
        print(group)
        for s in samples:
            print(s["pixel"],s["part"].split("| ")[1],np.round(s["position"],2),np.round(s["mirror"],2))


if __name__=="__main__":main()

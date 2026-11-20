"""Check that a local pigment edit does not change other parts' sampled wood."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mesh",type=Path,required=True)
    p.add_argument("--before",type=Path,required=True)
    p.add_argument("--after",type=Path,required=True)
    p.add_argument("--allowed-part",required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    meta=json.loads((a.mesh/"mesh.json").read_text(encoding="utf-8"))
    raw=(a.mesh/"mesh.bin").read_bytes()
    before=np.asarray(Image.open(a.before).convert("RGB"))
    after=np.asarray(Image.open(a.after).convert("RGB"))
    assert before.shape==after.shape
    h,w=before.shape[:2]
    points=np.frombuffer(raw,dtype="<f4",count=meta["indexByteOffset"]//4).reshape(-1,8)
    result={}
    for part in meta["parts"]:
        index=np.frombuffer(raw,dtype="<u4",offset=meta["indexByteOffset"]+4*part["indexOffset"],count=part["indexCount"]).reshape(-1,3)
        uv=points[index,6:8]
        samples=np.concatenate((uv.reshape(-1,2),uv.mean(1)),0)
        x=np.clip(np.floor(samples[:,0]*w).astype(int),0,w-1)
        y=np.clip(np.floor((1-samples[:,1])*h).astype(int),0,h-1)
        delta=np.max(np.abs(before[y,x].astype(int)-after[y,x].astype(int)),1)
        if part["name"]!=a.allowed_part:assert not delta.any(),(part["name"],int(delta.max()))
        result[part["name"]]={"vertex_and_triangle_center_samples":len(delta),
            "changed_samples":int((delta>0).sum()),"max_rgb_change_255":int(delta.max())}
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    output={"mesh_source_sha256":meta.get("sourceSha256",meta.get("source_sha256")),
        "before_sha256":sha(a.before),"after_sha256":sha(a.after),
        "changed_texels":int(np.any(before!=after,2).sum()),"parts":result,
        "method":"Nearest pigment texels at every triangle corner and center. Other components must stay byte-identical at every sampled surface point; the camera visibility and depth masks separately restrict the allowed component."}
    a.output.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("KNIGHT_ATLAS_SCOPE_OK",output["changed_texels"],result)

if __name__=="__main__":main()

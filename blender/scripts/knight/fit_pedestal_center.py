"""Fit the turned axis to the original outlines without changing its diameter."""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image,ImageDraw
from audit_mission import registered,silhouette,iou


def draw_part(points,triangles,width=1254):
    # A 2x coverage mask gives a smooth subpixel estimate for the center search.
    canvas=Image.new("L",(2*width,2*width))
    draw=ImageDraw.Draw(canvas)
    pixel=np.rint(points*2).astype(np.int32)
    for poly in pixel[triangles].tolist():draw.polygon([tuple(p) for p in poly],fill=255)
    return canvas


def main():
    p=argparse.ArgumentParser();p.add_argument("mesh",type=Path);p.add_argument("arcs",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args();m=json.loads((a.mesh/"mesh.json").read_text());arcs=json.loads(a.arcs.read_text())
    c=m["referenceCamera"];camera=np.reshape(c["worldToCamera"],(4,4));proj=np.reshape(c["projectionMatrix"],(4,4))@camera
    blob=(a.mesh/"mesh.bin").read_bytes();v=np.frombuffer(blob[:m["vertexByteLength"]],"<f4").reshape(-1,8)[:,:3]
    ix=np.frombuffer(blob[m["indexByteOffset"]:],"<u4").reshape(-1,3)
    screen=((v@proj[:2,:3].T+proj[:2,3])*[1,-1]+1)*627
    base=next(q for q in m["parts"] if q["name"].endswith("turned pedestal"))
    off=base["indexOffset"]//3;end=off+base["triangleCount"]
    pedestal=draw_part(screen,ix[off:end]);other=draw_part(screen,np.r_[ix[:off],ix[end:]])
    other=np.asarray(other.resize((1254,1254),Image.Resampling.BOX))>127
    ref=registered()
    target={k:silhouette(im,True) for k,im in ref.items()}
    center=(proj[0,3]+1)*627
    arc_target=.72*arcs["foot"]["original"]["center_x"]+.28*arcs["foot"]["selected"]["center_x"]
    # Keep the fit within the axis range observed in the black original and
    # the selected detail reference. Model X maintains the registered side floor.
    rows=[]
    for dx in np.arange(-1,8.25,.25):
        world_x=dx/(627*proj[0,0]);dy=-627*proj[1,0]*world_x
        shifted=pedestal.transform(pedestal.size,Image.Transform.AFFINE,(1,0,-2*dx,0,1,-2*dy),Image.Resampling.BILINEAR)
        pixels=other|(np.asarray(shifted.resize((1254,1254),Image.Resampling.BOX))>127)
        scores={k:iou(pixels,mask) for k,mask in target.items()}
        loss=1000*(1-.81*scores["original"]-.19*scores["selected"])+.22*abs(center+dx-arc_target)
        rows.append({"screen_dx":float(dx),"screen_dy":float(dy),"world_x":float(world_x),"scores":scores,"loss":float(loss)})
    chosen=min(rows,key=lambda r:r["loss"])
    result={"source_sha256":m["sourceSha256"],"old_center_x":center,"foot_arc_target_x":arc_target,
            "selected":chosen,"trials":rows,"method":"Fit a single horizontal physical offset of the pedestal in the locked camera. Its side-view floor, diameter and overall piece height stay fixed. The actual lower carving is carried smoothly with its seat."}
    a.output.parent.mkdir(exist_ok=True,parents=True);a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("FIXED_AXIS",center,arc_target,chosen)


if __name__=="__main__":main()

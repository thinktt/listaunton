"""Recover bounded walnut tone from measured diffuse response on the real face.

The original texture supplies the hue, hidden wood and continuous surface.
A neutral reflection term is separated before estimating a scalar wood gain.
Only camera-visible, front-facing atlas texels receive that adjustment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image,ImageFilter

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/"build/knight-mission";ASSETS=ROOT/"assets/knight"
sys.path.insert(0,str(ROOT/"scripts/queen"))
from image_math import blur

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ease(x,low,high):
    t=np.clip((x-low)/(high-low),0,1)
    return t*t*(3-2*t)


def diffuse_field(response,measurement,region):
    ref=np.asarray(Image.open(ASSETS/"ref.png").convert("RGBA"),dtype=np.float32)/255
    target=np.load(BUILD/"material-observations/reference-linear.npy")
    assert np.max(np.abs(np.load(BUILD/"material-observations/reference-display.npy")-ref))<1e-6
    full,dim=response["full"],response["dim"]
    diffuse=np.maximum((full[:,:,:3]-dim[:,:,:3])/(1-measurement["dim_gain"]),.0001)
    # Subtract the direction of an approximately neutral varnish reflection
    # from both measurements. It cannot turn a white reflected streak into pigment.
    neutral=np.array([1,.925,.85],np.float32);neutral/=np.linalg.norm(neutral)
    chroma=diffuse-(diffuse@neutral)[:,:,None]*neutral
    observed=target-(target@neutral)[:,:,None]*neutral
    norm=(chroma*chroma).sum(2)
    lower=.30 if region=="brow" else .37
    gain=np.clip(((observed*chroma).sum(2)+.00009)/(norm+.00009),lower,1.85)
    reflection=np.maximum(0,(target-diffuse*gain[:,:,None])@neutral)
    interior=(full[:,:,3]>.99)&(ref[:,:,3]>.85)&(ref[:,:,:3].max(2)>.055)
    interior=np.asarray(Image.fromarray(np.uint8(interior)*255).filter(ImageFilter.MinFilter(9)),np.float32)/255
    conf=interior*ease(np.sqrt(norm),.012,.085)*(1-.88*ease(reflection/(target[:,:,0]+.03),.30,.88))
    log=np.log(gain)
    broad=blur(log*conf,4,3)/np.maximum(blur(conf,4,3),1e-5)
    local=blur(log*conf,2,2)/np.maximum(blur(conf,2,2),1e-5)
    detail=.68 if region=="brow" else .50
    result=broad+detail*np.clip(log-local,-.34,.34)*conf
    return (result*blur(interior,2,2)*np.clip(blur(conf,4,3)/.48,0,1)*.91).astype(np.float32)


def sample(field,x,y):
    x=np.clip(x,0,field.shape[1]-1.001);y=np.clip(y,0,field.shape[0]-1.001)
    ix=x.astype(int);iy=y.astype(int);u=x-ix;v=y-iy
    return ((1-u)*(1-v)*field[iy,ix]+u*(1-v)*field[iy,ix+1]+
            (1-u)*v*field[iy+1,ix]+u*v*field[iy+1,ix+1])


def project_surface(path,depth,field,atlas,box):
    data=np.load(path)
    h,w=atlas.shape
    uv=data["uv"].astype(float)*[w,-h]+[-.5,h-.5]
    screen=data["screen"];normal=data["facing"];tri=data["triangles"]
    points=screen[tri];highest=points.max(1);lowest=points.min(1)
    x0,y0,x1,y1=box
    valid=(highest[:,0]>x0)&(lowest[:,0]<x1)&(highest[:,1]>y0)&(lowest[:,1]<y1)&(normal[tri].max(1)>.07)
    visible=0
    for face in tri[valid]:
        texels=uv[face];origin=texels[0];a=texels[1]-origin;b=texels[2]-origin
        det=a[0]*b[1]-a[1]*b[0]
        if abs(det)<1e-7:continue
        lo=np.maximum(np.ceil(texels.min(0)).astype(int),0);hi=np.minimum(np.floor(texels.max(0)).astype(int),[w-1,h-1])
        if any(hi<lo):continue
        iy,ix=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
        dx=ix-origin[0];dy=iy-origin[1]
        u=(dx*b[1]-dy*b[0])/det;v=(a[0]*dy-a[1]*dx)/det;t=1-u-v
        inside=(u>=0)&(v>=0)&(t>=0)
        if not inside.any():continue
        bary=np.column_stack((t[inside],u[inside],v[inside]))
        sx,sy,sz=(bary@screen[face]).T
        geometric_weight=ease(bary@normal[face],.065,.40)
        depth_weight=1-ease(np.abs(sample(depth,sx,sy)-sz),.011,.036)
        value=sample(field,sx,sy)*geometric_weight*depth_weight
        atlas[iy[inside],ix[inside]]=value
        visible+=int(((geometric_weight*depth_weight)>.5).sum())
    return visible


def main():
    p=argparse.ArgumentParser();p.add_argument("--carving",required=True);p.add_argument("--variant",required=True)
    p.add_argument("--response",type=Path,default=BUILD/"muzzle-response")
    p.add_argument("--texture",type=Path)
    p.add_argument("--region",choices=("muzzle","brow"),default="muzzle")
    args=p.parse_args()
    out=BUILD/args.variant;out.mkdir(exist_ok=True)
    source=BUILD/args.carving;texture=args.texture or source/"pigment.png"
    measured=json.loads((args.response/"measurement.json").read_text())
    assert measured["source_sha256"]==sha(source/"knight.blend") and measured["texture_sha256"]==sha(texture)
    data=np.load(args.response/"light-response.npz")
    field=diffuse_field(data,measured,args.region)
    prior=np.asarray(Image.open(texture).convert("RGB"));log_gain=np.zeros(prior.shape[:2],np.float32)
    y,x=np.indices(field.shape)
    if args.region=="muzzle":
        jobs=[("continuous horse head and neck",ease(x,467,556)*ease(y,302,352)*(1-ease(y,521,557)),(466,300,748,559))]
    else:
        jobs=[("near swept ear",ease(x,255,279)*(1-ease(x,542,562)),(254,349,563,483)),
              ("continuous horse head and neck",ease(x,455,498)*(1-ease(x,602,638))*ease(y,352,388)*(1-ease(y,498,523)),(454,351,639,524))]
    visibility=0;receivers=[]
    for suffix,weight,box in jobs:
        receiver=next(o for o in measured["objects"] if o["object"].endswith(suffix))
        visibility+=project_surface(args.response/receiver["file"],data["depth"],field*weight,log_gain,box)
        receivers.append(receiver["object"])
    changed=np.abs(log_gain)>.001
    assert 12000<changed.sum()<750000,(visibility,changed.sum(),float(data["depth"].max()))
    color=prior.copy();display=color[changed].astype(float)/255
    linear=np.where(display<=.04045,display/12.92,((display+.055)/1.055)**2.4)*np.exp(log_gain[changed,None])
    result=np.where(linear<=.0031308,12.92*linear,1.055*np.maximum(linear,0)**(1/2.4)-.055)
    color[changed]=np.rint(255*np.clip(result,0,1)).astype(np.uint8)
    Image.fromarray(color).save(out/"pigment.png")
    report={"source_sha256":sha(source/"knight.blend"),"previous_texture_sha256":sha(texture),
            "pigment_sha256":sha(out/"pigment.png"),"changed_texels":int(changed.sum()),"visible_samples":visibility,
            "gain_quantiles_05_50_95":np.quantile(np.exp(log_gain[changed]),[.05,.5,.95]).tolist(),
            "receivers":receivers,"region":args.region,"method":"Use measured diffuse response and a separate neutral-reflection component. Refit bounded warm pigment on visible wood UVs while retaining the underlying hue and the hidden wood."}
    (out/"grade.json").write_text(json.dumps(report,indent=2)+"\n")
    print(report)


if __name__=="__main__":main()

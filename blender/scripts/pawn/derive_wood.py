"""Infer diffuse wood in the fixed view and wrap it onto a full, static lathe UV atlas.

The photograph supplies visible pigment detail. Measured Blender responses
remove modeled illumination; uncertain reflections are filled from nearby
wood. A continuous unlit grain field supplies grazing and unseen surfaces.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts/queen"))
from image_math import blur

def linear(value):
    return np.where(value<=.04045,value/12.92,((value+.055)/1.055)**2.4)

def display(value):
    value=np.maximum(value,0)
    return np.where(value<=.0031308,12.92*value,1.055*value**(1/2.4)-.055)

def sample(arr,x,y):
    h,w=arr.shape[:2]
    x=np.clip(x,0,w-1.00001); y=np.clip(y,0,h-1.00001)
    i=x.astype(np.int32);j=y.astype(np.int32);dx=x-i;dy=y-j
    if arr.ndim==3:dx=dx[...,None];dy=dy[...,None]
    return (1-dy)*((1-dx)*arr[j,i]+dx*arr[j,i+1])+dy*((1-dx)*arr[j+1,i]+dx*arr[j+1,i+1])

def ramp(x,lo,hi):
    t=np.clip((x-lo)/(hi-lo),0,1)
    return t*t*(3-2*t)

def pigment_field(directory):
    black=np.load(directory/"black.npy"); gray=np.load(directory/"gray.npy")
    target=np.load(directory/"target-linear.npy")
    srgb=np.load(directory/"reference-srgb.npy")
    # Evaluating gray near the walnut's albedo limits indirect-light changes
    # compared with a unit-white response. Remaining uncertainty is masked.
    response=np.clip((gray[:,:,:3]-black[:,:,:3])/.1,.025,20)
    fg=(gray[:,:,3]>.99)&(srgb.max(2)>.05)
    interior=np.asarray(Image.fromarray(np.uint8(fg)*255).filter(ImageFilter.MinFilter(9)))/255
    pigment=(target-black[:,:,:3])/response
    bfrac=black[:,:,:3].max(2)/np.maximum(target.max(2),.004)
    weight=interior*(1-ramp(srgb.min(2),.19,.39))*(1-ramp(bfrac,.25,.73))
    weight*=ramp(response.mean(2),.09,.35)*ramp(pigment[:,:,0],.003,.018)
    weight*=ramp(pigment[:,:,1],.0004,.004)
    valid=weight>.8
    assert valid.sum()>20000,valid.sum()
    median=np.median(pigment[valid],axis=0)
    pigment=np.clip(pigment,np.maximum(median*.06,.0003),np.minimum(median*4.2,.9))
    # Multiscale normalized convolution. Dark pigment never supplies a white
    # halo to a masked glint. Preserve direct measurements where reliable.
    filled=np.broadcast_to(median,pigment.shape).copy()
    for radius in (32,12,4):
        density=blur(weight,r=radius,passes=2)
        local=blur(pigment*weight[:,:,None],r=radius,passes=2)/np.maximum(density[:,:,None],1e-6)
        mix=ramp(density,.055,.40)[:,:,None]
        filled=filled*(1-mix)+local*mix
    result=filled*(1-weight[:,:,None])+pigment*weight[:,:,None]
    return result.astype(np.float32),median,interior.astype(np.float32),weight

def derive(directory,atlas_path,size):
    field,median,interior,confidence=pigment_field(directory)
    meridian=np.load(directory/"meridian.npy")
    depth=np.load(directory/"depth.npy")[:,:,0]
    assets=ROOT/"assets/pawn"; camera=json.loads((assets/"camera.json").read_text())
    inverse=np.array(camera["worldToCamera"]).reshape(4,4)
    projection=np.array(camera["projectionMatrix"]).reshape(4,4)@inverse
    view=inverse[2,:3];W=camera["width"];H=camera["height"]
    tilepath=ROOT/"assets/queen/walnut-fine-albedo.png"
    tile=linear(np.asarray(Image.open(tilepath).convert("RGB"),dtype=np.float32)/255)
    tile_med=np.median(tile[::4,::4].reshape(-1,3),axis=0)
    width=tile.shape[1];height=tile.shape[0]
    atlas=np.empty((size,size,3),dtype=np.uint8)
    u=(np.arange(size)+.5)/size
    theta=2*np.pi*(u+.25);cos=np.cos(theta);sin=np.sin(theta)
    coverage_sum=0
    for top in range(0,size,80):
        rows=np.arange(top,min(top+80,size))
        v=1-(rows+.5)/size
        radius,z,nr,nz=[np.interp(v,meridian[:,0],meridian[:,index])[:,None] for index in (1,2,3,4)]
        x=radius*cos;y=radius*sin
        px=((projection[0,0]*x+projection[0,1]*y+projection[0,2]*z+projection[0,3])+1)*W/2-.5
        py=(1-(projection[1,0]*x+projection[1,1]*y+projection[1,2]*z+projection[1,3]))*H/2-.5
        camera_depth=-(inverse[2,0]*x+inverse[2,1]*y+inverse[2,2]*z+inverse[2,3])
        ndot=(nr*cos*view[0]+nr*sin*view[1]+nz*view[2])/np.maximum(np.hypot(nr,nz),.01)
        visible=1-ramp(np.abs(sample(depth,px,py)-camera_depth),.012,.047)
        coverage=visible*ramp(ndot,.045,.40)*sample(interior,px,py)
        # World coordinates and reflected tile edges give a continuous hidden
        # material around the seam and poles. Both colors are pigment values.
        tx=1-np.abs((.45+.63*x+.25*y)%2-1)
        ty=1-np.abs((.20+.59*z+.12*y+.035*np.sin(7*x))%2-1)
        hidden=sample(tile,tx*(width-1),ty*(height-1))*median/tile_med
        color=hidden*(1-coverage[:,:,None])+sample(field,px,py)*coverage[:,:,None]
        atlas[rows]=np.uint8(np.rint(np.clip(display(color),0,1)*255))
        coverage_sum+=float(coverage.sum())
    atlas_path.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(atlas).save(atlas_path)
    Image.fromarray(np.uint8(np.clip(display(field),0,1)*255)).save(directory/"inferred-pigment-diagnostic.png")
    Image.fromarray(np.uint8(np.clip(confidence,0,1)*255)).save(directory/"confidence-diagnostic.png")
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    report={"method":"Bounded diffuse pigment inferred from measured scene-linear black/0.1-gray responses, with multiscale highlight filling and depth/facing visibility. Hidden wood uses a continuous object-space sample of the existing unlit walnut source.","assumptions":"Local de-lighting and hidden grain are artistic estimates. The PNG stores pigment, rendered through a real Principled BSDF and real lamps.","resolution":size,"median_linear_pigment":median.tolist(),"mean_projected_weight":coverage_sum/size**2,"source_measurement":json.loads((directory/"measurement.json").read_text()),"hidden_wood_sha256":sha(tilepath),"atlas_sha256":sha(atlas_path)}
    (directory/"derivation.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("measurement");p.add_argument("texture");p.add_argument("--size",type=int,default=2048)
    args=p.parse_args();derive(ROOT/"build/pawn-mission"/args.measurement,ROOT/args.texture,args.size)

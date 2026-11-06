"""Extend trustworthy diffuse samples through highlight gaps and around the lathe.

Interpolate low-frequency pigment on the surface. Supply fine grain with the
existing unlit walnut texture in gaps. The same atlas works from every camera.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from derive_wood import ROOT, blur, display, linear, pigment_field, ramp, sample

def wrapped_blur(a,radius):
    pad=2*radius
    extended=np.concatenate((a[:,-pad:],a,a[:,:pad]),axis=1)
    return blur(extended,r=radius,passes=2)[:,pad:-pad]

def run(directory,output,size=2048):
    _,median,interior,weight=pigment_field(directory)
    black=np.load(directory/"black.npy")[:,:,:3]
    gray=np.load(directory/"gray.npy")[:,:,:3]
    target=np.load(directory/"target-linear.npy")
    observed=(target-black)/np.maximum((gray-black)/.1,.05)
    reliability=weight.copy()
    reliability*=1-ramp(observed[:,:,0]/median[0],2.0,3.2)
    ratio=observed[:,:,1]/np.maximum(observed[:,:,0],.003)
    reliability*=ramp(ratio,.07,.13)*(1-ramp(ratio,.44,.64))
    observed=np.clip(observed,np.maximum(.0003,median*.075),median*3.4)
    profile=np.load(directory/"meridian.npy")
    depth=np.load(directory/"depth.npy")[:,:,0]
    camera=json.loads((ROOT/"assets/pawn/camera.json").read_text())
    view=np.array(camera["worldToCamera"]).reshape(4,4)
    proj=np.array(camera["projectionMatrix"]).reshape(4,4)@view
    theta=((np.arange(size)+.5)/size+.25)*2*np.pi
    cs,sn=np.cos(theta),np.sin(theta)
    wood=linear(np.asarray(Image.open(ROOT/"assets/queen/walnut-fine-albedo.png").convert("RGB"),dtype=np.float32)/255)
    wm=np.median(wood[::4,::4].reshape(-1,3),axis=0)
    base=np.empty((size,size,3),dtype=np.float32)
    known=np.empty_like(base);weights=np.empty((size,size),np.float32)
    W,H=camera["width"],camera["height"]
    for first in range(0,size,64):
        rows=np.arange(first,min(first+64,size));v=1-(rows+.5)/size
        r,z,nr,nz=[np.interp(v,profile[:,0],profile[:,i])[:,None] for i in (1,2,3,4)]
        x=r*cs;y=r*sn
        def project(row):
            return row[0]*x+row[1]*y+row[2]*z+row[3]
        px=(project(proj[0])+1)*W/2-.5;py=(1-project(proj[1]))*H/2-.5
        dz=np.abs(sample(depth,px,py)+project(view[2]))
        facing=(nr*cs*view[2,0]+nr*sn*view[2,1]+nz*view[2,2])/np.maximum(np.hypot(nr,nz),.01)
        weights[rows]=(1-ramp(dz,.008,.035))*ramp(facing,.08,.48)*sample(reliability,px,py)
        known[rows]=sample(observed,px,py)
        tx=1-np.abs((.45+.63*x+.25*y)%2-1)
        ty=1-np.abs((.20+.59*z+.12*y+.035*np.sin(7*x))%2-1)
        base[rows]=sample(wood,tx*(wood.shape[1]-1),ty*(wood.shape[0]-1))*median/wm
    # Work in log pigment. Low-frequency correction follows the known wood
    # in the neighborhood of each gap; high-frequency fallback keeps texture.
    floor=.002
    log_base=np.log(np.maximum(base,floor))
    difference=np.log(np.maximum(known,floor))-log_base
    difference=np.clip(difference,-1.9,1.5)
    summed=weights.sum(1)
    rows=np.flatnonzero(summed>16)
    assert len(rows)>size//2
    row_correction=(difference*weights[:,:,None]).sum(1)/np.maximum(summed[:,None],1)
    correction=np.column_stack([np.interp(np.arange(size),rows,row_correction[rows,i]) for i in range(3)])
    correction=blur(correction[:,None,:],r=10,passes=2) + np.zeros_like(base)
    for radius in (70,24,7):
        density=wrapped_blur(weights,radius)
        for c in range(3):
            neighborhood=wrapped_blur(weights*difference[:,:,c],radius)/np.maximum(density,1e-6)
            influence=ramp(density,.025,.35)
            correction[:,:,c]=correction[:,:,c]*(1-influence)+neighborhood*influence
    # Soften the handoff across grazing and reflection boundaries, preserving
    # direct high-frequency pigment in reliable camera-facing areas.
    w=weights[:,:,None]
    pigment=np.exp(log_base+correction*(1-w)+difference*w)
    output.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(np.uint8(np.rint(np.clip(display(pigment),0,1)*255))).save(output)
    report={"method":"Surface-space, confidence-weighted log pigment interpolation plus continuous unlit walnut grain. Exclude model-dominated glints and unreliable chromaticities; retain measured detail on trustworthy faces.","size":size,"mean_confidence":float(weights.mean()),"direct_coverage_fraction":float(np.mean(weights>.8)),"atlas_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),"source_measurement":json.loads((directory/"measurement.json").read_text())}
    (directory/"surface-completion.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("measurement");p.add_argument("texture");p.add_argument("--size",type=int,default=2048)
    a=p.parse_args();run(ROOT/"build/pawn-mission"/a.measurement,ROOT/a.texture,a.size)

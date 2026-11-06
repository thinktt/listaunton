"""Apply a bounded wood tone to the carved recesses and both inset eyes."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from fit_muzzle_profile import carved_profile,muzzle_shape
from lower_carving_fit import rest_coords

ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/"assets/knight";BUILD=ROOT/"build/knight-mission"


def paint_triangle(layer,coords,value):
    lo=np.maximum(np.ceil(coords.min(0)).astype(int),0)
    hi=np.minimum(np.floor(coords.max(0)).astype(int),np.array(layer.shape[::-1])-1)
    if np.any(hi<lo):return
    p=coords[0];ab=coords[1]-p;ac=coords[2]-p
    den=ab[0]*ac[1]-ab[1]*ac[0]
    if abs(den)<1e-8:return
    yy,xx=np.ogrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
    ax,ay=xx-p[0],yy-p[1]
    u=(ax*ac[1]-ay*ac[0])/den;v=(ab[0]*ay-ab[1]*ax)/den
    inside=(u>=-1e-6)&(v>=-1e-6)&(u+v<=1.000001)
    target=layer[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
    weight=np.round(255*(value[0]+u*(value[1]-value[0])+v*(value[2]-value[0]))).clip(0,255)
    np.maximum(target,np.where(inside,weight,0).astype(np.uint8),out=target)


def main():
    p=argparse.ArgumentParser();p.add_argument("--carving",required=True)
    p.add_argument("--variant",required=True);p.add_argument("--eye-gain",type=float,default=.38)
    opt=p.parse_args()
    out=BUILD/opt.variant;out.mkdir(exist_ok=True)
    carving=BUILD/opt.carving;cfg=json.loads((carving/"parameters.json").read_text())
    meta=json.loads((ASSETS/"mesh.json").read_text())
    assert meta["sourceSha256"]==cfg["source_sha256"]
    blob=(ASSETS/"mesh.bin").read_bytes()
    data=np.frombuffer(blob[:meta["vertexByteLength"]],dtype="<f4").reshape(-1,8)
    tri=np.frombuffer(blob[meta["indexByteOffset"]:],dtype="<u4").reshape(-1,3)
    pigment=Image.open(ROOT/meta["texture"]).convert("RGB");w,h=pigment.size
    texels=data[:,6:8].astype(float)*[w,-h]+[-.5,h-.5]
    amount=np.zeros(len(data))
    for part in meta["parts"]:
        s=part["vertexOffset"];e=s+part["vertexCount"];name=part["name"]
        if name.endswith(" eye"):amount[s:e]=1-opt.eye_gain
        if name.endswith("continuous horse head and neck"):
            shape=cfg["profile"]
            rest=muzzle_shape(rest_coords(data[s:e,:3].astype(float),shape["pose"]),shape["advance_lift_underdrop_width"])
            nose=-carved_profile(rest,np.array(cfg["nostril_curve_rest"]),cfg["nostril_width"],1,0)
            mouth=-carved_profile(rest,np.array(cfg["mouth_curve_rest"]),.025,1,0)
            amount[s:e]=np.maximum(.61*nose,.22*mouth)
    amount=amount.clip(0,.82)
    painted=np.zeros((h,w),np.uint8)
    active=amount[tri].max(axis=1)>.003
    for face in tri[active]:paint_triangle(painted,texels[face],amount[face])
    # Pad island boundaries for bilinear sampling, protecting every triangle
    # outside the requested parts from color changes in the padding step.
    protect=Image.new("1",(w,h));draw=ImageDraw.Draw(protect)
    for polygon in np.rint(texels[tri[~active]]).astype(np.int32):
        draw.polygon([tuple(p) for p in polygon.tolist()],fill=1)
    padding=np.asarray(Image.fromarray(painted).filter(ImageFilter.MaxFilter(7)))
    painted=np.maximum(painted,np.where(np.asarray(protect),0,padding)).astype(np.uint8)
    gain=1-painted.astype(float)/255
    color=np.asarray(pigment).copy();changed=painted>0;value=color[changed].astype(float)/255
    linear=np.where(value<=.04045,value/12.92,((value+.055)/1.055)**2.4)*gain[changed,None]
    srgb=np.where(linear<=.0031308,12.92*linear,1.055*linear**(1/2.4)-.055)
    color[changed]=np.rint(255*srgb).clip(0,255).astype(np.uint8)
    Image.fromarray(color).save(out/"pigment.png")
    result={"source_sha256":hashlib.sha256((carving/"knight.blend").read_bytes()).hexdigest(),
            "previous_texture_sha256":meta["textureSha256"],"pigment_sha256":hashlib.sha256((out/"pigment.png").read_bytes()).hexdigest(),
            "eye_linear_gain":opt.eye_gain,"deepest_nostril_gain":.39,"deepest_mouth_gain":.78,"changed_texels":int(changed.sum()),
            "method":"Multiply linear walnut reflectance on the two eye UV islands and inside the actual bilateral incisions; protect unaffected surfaces and the original pigment atlas."}
    (out/"grade.json").write_text(json.dumps(result,indent=2)+"\n")
    print(result)


if __name__=="__main__":main()

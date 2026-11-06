"""Fit low studio reflections to the original's turned collar and foot."""
from pathlib import Path
import argparse
import json
import math
import sys

import bpy
import numpy as np
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from fit_eye_reflection import display_transform
from fit_chest_reflections import panel_from_samples
from fit_surface_polish import read_reference
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera

CROP=(199,603,784,1064)
BASIS_POWER=160


def add_card(scene,receivers,label,center,dimensions,color,target=None):
    data=bpy.data.lights.new("Knight | "+label,"AREA")
    data.shape="RECTANGLE";data.size,data.size_y=dimensions;data.color=color;data.energy=0
    lamp=bpy.data.objects.new(data.name,data);scene.collection.objects.link(lamp);lamp.location=center
    if target is None:
        lamp.rotation_euler=(math.pi,0,0)
    else:
        lamp.rotation_euler=(Vector(target)-lamp.location).to_track_quat("-Z","Y").to_euler()
        data.spread=math.radians(62)
    lamp.visible_diffuse=False;lamp.visible_glossy=True
    lamp.light_linking.receiver_collection=receivers
    return lamp


def solve(base,responses,target,weights,transform):
    def loss(power):
        linear=base.copy()
        for value,delta in zip(power,responses):
            if value:linear+=value*delta
        transform.applyRGB(linear)
        e=linear-target
        err=np.sqrt(.042**2+e*e)-.042+.55*e*e
        return float(np.average(err.mean(1),weights=weights))
    factors=np.zeros(len(responses));initial=best=loss(factors)
    for step in (1,.25,.06,.015,.003):
        for _ in range(32):
            before=best
            for i in range(len(factors)):
                for sign in (-1,1):
                    trial=factors.copy();trial[i]+=step*sign
                    if not 0<=trial[i]<=12:continue
                    err=loss(trial)
                    if err<best-1e-8:factors,best=trial,err
            if best==before:break
    return factors,initial,best


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
    p.add_argument("--arcs",type=Path,required=True);p.add_argument("--variant",required=True)
    p.add_argument("--focused",type=Path,help="Registered rim mirror-ray samples for compact, directed cards.")
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/args.variant;out.mkdir(exist_ok=True)
    arcs=json.loads(args.arcs.read_text())
    bpy.ops.wm.open_mainfile(filepath=str(args.source),load_ui=False);scene=bpy.context.scene
    receivers=bpy.data.collections.new("Knight | pedestal reflection receivers")
    receivers.objects.link(bpy.data.objects["Knight | turned pedestal"])
    lamps=[];records=[]
    presets=[("front foot reflector",(.12,-3.57,1.21),(3.45,.84),(1,.91,.81),(.1,-1.3,.42))]
    if args.focused:
        hits=json.loads(args.focused.read_text())
        assert hits["source_sha256"]==sha(args.source)
        collar=hits["features"]["collar"]
        for label,lo,hi,distance,spread in [("left collar strip",388,506,.85,16),("right collar strip",535,647,.80,18)]:
            portion=[hit for hit in collar if lo<=hit["pixel"][0]<=hi]
            assert len(portion)>=4
            lamp,spec=panel_from_samples(scene,receivers,label,portion,distance,(.10,.045))
            lamp.data.size_y=max(.065,min(lamp.data.size_y,.22))
            lamp.data.spread=math.radians(spread);lamp.data.color=(1,.86,.73)
            spec["size"][1]=lamp.data.size_y;spec["spread"]=spread;spec["color"]=list(lamp.data.color)
            lamps.append(lamp);records.append(spec)
    else:
        presets[:0]=[("low front-left card",(-.57,-3.62,.02),(2.60,1.35),(1,.87,.76),None),
                     ("low right card",(2.36,-1.30,.02),(1.68,1.75),(1,.92,.82),None)]
    for label,xyz,size,color,target in presets:
        lamps.append(add_card(scene,receivers,label,xyz,size,color,target))
        records.append({"name":label,"position":xyz,"size":size,"color":color,"target":target})
    configure_render(scene,144);scene.cycles.use_denoising=False;scene.cycles.use_light_tree=False
    x0,y0,x1,y1=CROP;w=1254
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.05)/w;scene.render.border_max_x=(x1+.05)/w
    scene.render.border_min_y=(w-y1+.05)/w;scene.render.border_max_y=(w-y0+.05)/w
    base=read_pass(scene,out/"no-low-cards.exr");target=read_reference()[y0:y1,x0:x1]
    yy,xx=np.indices(base.shape[:2]);yy+=y0;xx+=x0
    assert base.shape==target.shape
    mask=(base[:,:,3]>.99)&(target[:,:,3]>.86)&(target[:,:,:3].max(2)>.06)
    weight=np.ones(mask.shape,dtype=np.float32)
    for name,importance in [("collar",8),("foot",3)]:
        obs=arcs[name]["selected"];cx=obs["center_x"];r=obs["radius_pixels"];front=obs["front_y"]
        ycenter=front-r*np.sin(np.deg2rad(54))
        radius=np.hypot(xx-cx,(yy-ycenter)/np.sin(np.deg2rad(54)))
        forward=np.clip((yy-ycenter-25)/65,0,1)
        weight+=importance*np.exp(-((radius-r)/3.8)**2)*forward*(.8+.7*target[:,:,1])
    if args.focused:
        mask&=(xx+yy)%2==0
    else:
        mask&=((xx%2==0)&(yy%2==0))|(weight>2)
    points=base[:,:,:3][mask];responses=[]
    for i,lamp in enumerate(lamps):
        lamp.data.energy=BASIS_POWER
        frame=read_pass(scene,out/(f"card-{i}.exr"))
        responses.append(np.maximum(frame[:,:,:3][mask]-points,0));lamp.data.energy=0
    factors,initial,best=solve(points,responses,target[:,:,:3][mask],weight[mask],display_transform(scene))
    for lamp,factor,record in zip(lamps,factors,records):
        lamp.data.energy=float(BASIS_POWER*factor);record["watts"]=float(lamp.data.energy)
        if not factor:bpy.data.objects.remove(lamp,do_unlink=True)
    scene.render.use_border=False;scene.render.use_crop_to_border=False
    configure_render(scene,144);scene.cycles.use_light_tree=True
    cfg={"source_sha256":sha(args.source),"samples":144,"basis_samples":144,"crop":CROP,
         "lights":records,"start_loss":initial,"selected_loss":best,"fit_samples":int(mask.sum()),
         "method":"Trace mirror directions from the turned rims and fit two finite low warm cards plus a foot reflector against the measured full-resolution response. Retain nonnegative powers, protect the rest of the piece by linking these reflections to its turned base."}
    scene["knight_pedestal_cards"]=json.dumps(cfg)
    save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,144);render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg);print("KNIGHT_TURNED_REFLECTIONS",initial,best,records,flush=True)


if __name__=="__main__":main()

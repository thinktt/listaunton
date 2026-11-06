"""Fit physical studio panels to the two chest ridges in the fixed knight view."""
import argparse
import json
import math
from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Matrix

sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from fit_eye_reflection import display_transform
from knight_polish import add_grain_relief
from mission_scene import ASSETS, BUILD, MODEL, configure_render, json_file, render, save_model, sha, use_side_camera

BASIS_WATTS=50


def panel_from_samples(scene, collection, name, samples, distance, margins):
    points=np.array([s["position"] for s in samples])
    directions=np.array([s["mirror"] for s in samples])
    assert len({s["part"] for s in samples})==1
    normal=directions.mean(0);normal/=np.linalg.norm(normal)
    plane=points.mean(0)+distance*normal
    ray_distances=((plane-points)@normal)/(directions@normal)
    assert min(ray_distances)>.1
    intersections=points+ray_distances[:,None]*directions
    center=intersections.mean(0)
    _,_,axes=np.linalg.svd(intersections-center,full_matrices=False)
    long=axes[0]-np.dot(axes[0],normal)*normal;long/=np.linalg.norm(long)
    short=np.cross(normal,long)
    spread=(intersections-center)@np.column_stack((long,short))
    lower,upper=np.quantile(spread,[.04,.96],axis=0)
    center=center+np.column_stack((long,short))@((lower+upper)/2)
    length,width=(upper-lower)+np.array(margins)
    data=bpy.data.lights.new("Walnut | "+name,"AREA")
    data.shape="RECTANGLE";data.size=float(length);data.size_y=float(width)
    data.color=(1,.925,.855);data.energy=0
    obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj)
    obj.location=center.tolist()
    obj.rotation_euler=Matrix(np.column_stack((long,short,normal)).tolist()).to_euler()
    obj.visible_diffuse=False;obj.visible_glossy=True
    obj.light_linking.receiver_collection=collection
    return obj,{"name":name,"center":center.tolist(),"normal":normal.tolist(),"long_axis":long.tolist(),
                "size":[float(length),float(width)],"target_pixels":[s["pixel"] for s in samples]}


def target_and_weights(features,base):
    image=bpy.data.images.load(str(ASSETS/"ref.png"),check_existing=False)
    image.colorspace_settings.name="Non-Color"
    rgba=np.empty(1254*1254*4,dtype=np.float32);image.pixels.foreach_get(rgba)
    rgba=rgba.reshape(1254,1254,4)[::-1].copy()
    bpy.data.images.remove(image)
    target=rgba.reshape(627,2,627,2,4).mean(axis=(1,3))
    # Sample the complete piece to penalize new reflections outside the crest.
    y,x=np.indices(base.shape[:2]);px=x*2+1;py=y*2+1
    neck=(py>=558)&(py<752)&(px>344)&(px<658)
    weight=.45+.85*neck
    for samples,width,strength in [(features["chest_crest"],12,3.0),(features["chest_far"],7,2.5),(features["chest_flank"],22,1.0)]:
        positions=np.array([s["pixel"] for s in samples])
        center=np.interp(py,positions[:,1],positions[:,0])
        length_weight=np.clip((py-positions[0,1]+12)/16,0,1)*np.clip((positions[-1,1]+12-py)/16,0,1)
        weight+=strength*np.exp(-((px-center)/width)**2)*length_weight
    weight*=1+1.8*neck*np.clip((target[:,:,1]-.25)/.5,0,1)
    mask=(base[:,:,3]>.99)&(target[:,:,3]>.88)&(target[:,:,:3].max(2)>.07)&((x%2)==0)&((y%2)==0)
    return target[:,:,:3][mask],weight[mask].astype(np.float32),mask


def fit(base,basis,target,weight,transform):
    def estimate(values):
        lit=base.copy()
        for value,response in zip(values,basis):
            if value:lit+=value*response
        transform.applyRGB(lit)
        return float(np.average(np.sum((lit-target)**2,axis=1),weights=weight))
    factors=np.zeros(len(basis));initial=best=estimate(factors)
    for step in (2, .5, .125, .035, .008):
        for _ in range(25):
            before=best
            for i in range(len(factors)):
                for sign in (-1,1):
                    trial=factors.copy();trial[i]+=sign*step
                    if not 0<=trial[i]<=22:continue
                    loss=estimate(trial)
                    if loss<best-2e-8:factors,best=trial,loss
            if before==best:break
    return factors,initial,best


def main():
    args=argparse.ArgumentParser()
    args.add_argument("--source",type=Path,default=MODEL)
    args.add_argument("--probes",type=Path,default=BUILD/"chest-light-study/probes.json")
    args.add_argument("--variant",default="014-chest-panels")
    args.add_argument("--grain-height",type=float,default=0)
    args.add_argument("--beam-degrees",type=float,default=180)
    args.add_argument("--strip-width",type=float,default=1)
    args.add_argument("--samples",type=int,default=96)
    opt=args.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/opt.variant;out.mkdir(parents=True,exist_ok=True)
    probes=json.loads(opt.probes.read_text())
    assert probes["source_sha256"]==sha(opt.source)
    bpy.ops.wm.open_mainfile(filepath=str(opt.source),load_ui=False);scene=bpy.context.scene
    if opt.grain_height:
        add_grain_relief(scene,opt.grain_height)
    receivers=bpy.data.collections.new("Knight | chest reflection receivers")
    receivers.objects.link(bpy.data.objects["Knight | continuous horse head and neck"])
    features=probes["features"]
    placements=[
        ("crest",features["chest_crest"],1.5,(.13,.06)),
        ("narrow crest",features["chest_crest"][2:-1],1.4,(.05,.025)),
        ("far ridge",features["chest_far"],2.6,(.12,.08)),
        ("outer shoulder",features["chest_flank"],2.2,(.62,.49))]
    lights=[];settings=[]
    for name,samples,distance,margins in placements:
        obj,spec=panel_from_samples(scene,receivers,name,samples,distance,margins)
        obj.data.spread=math.radians(opt.beam_degrees)
        if name!="outer shoulder":
            obj.data.size_y*=opt.strip_width
            spec["size"][1]=obj.data.size_y
        lights.append(obj);settings.append(spec)
    configure_render(scene,128);scene.render.resolution_percentage=50
    scene.cycles.use_denoising=False;scene.cycles.use_light_tree=False
    base=read_pass(scene,out/"base.exr")
    transform=display_transform(scene)
    target,weights,mask=target_and_weights(features,base)
    responses=[]
    for i,lamp in enumerate(lights):
        lamp.data.energy=BASIS_WATTS
        frame=read_pass(scene,out/("panel-"+str(i)+".exr"))
        responses.append(np.maximum(0,frame[:,:,:3][mask]-base[:,:,:3][mask]))
        lamp.data.energy=0
    factors,initial,best=fit(base[:,:,:3][mask],responses,target,weights,transform)
    for i,lamp in enumerate(lights):
        lamp.data.energy=float(factors[i]*BASIS_WATTS)
        settings[i]["watts"]=lamp.data.energy
        if not lamp.data.energy:bpy.data.objects.remove(lamp,do_unlink=True)
    configure_render(scene,opt.samples);scene.cycles.use_light_tree=True
    info={"source_sha256":sha(opt.source),"probe_sha256":sha(opt.probes),"samples":opt.samples,
          "pigment_log_relief_distance":opt.grain_height,"beam_degrees":opt.beam_degrees,
          "basis_samples":128,"initial_display_loss":initial,"predicted_display_loss":best,
          "measured_pixels":int(mask.sum()),"physical_rectangles":settings,
          "method":"Fit finite specular-only panels to reflected rays on the actual shoulder. Score the complete fixed-view rendering and verify the side."}
    scene["knight_chest_panels"]=json.dumps(info)
    save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,opt.samples)
    render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",info)
    print("KNIGHT_CHEST_PANELS",initial,best,[(s["name"],s["watts"]) for s in settings],flush=True)


if __name__=="__main__":main()

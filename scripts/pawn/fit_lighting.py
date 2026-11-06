"""Fit real, shaped area lights against measured pawn BSDF responses in AgX."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
import PyOpenColorIO as ocio
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).parent))
from mission_render import BUILD, ROOT, Surface, save_json
from polish_trial import finish,open_source,save_trial
from capture_pigment import reference_srgb

def shape(surface, spec):
    x,y=spec["pixel"];hit,n=surface.hit(x,y)
    direction=(-surface.back).reflect(n)
    center=hit+direction*spec.get("distance",3.)
    def plane_hit(px,py):
        point,normal=surface.hit(px,py);ray=(-surface.back).reflect(normal)
        return np.asarray(point+ray*((center-point).dot(direction)/ray.dot(direction)))
    # Local change in reflected rays per pixel defines the lamp footprint.
    dx=(plane_hit(x+1.5,y)-plane_hit(x-1.5,y))/3
    dy=(plane_hit(x,y+1.5)-plane_hit(x,y-1.5))/3
    angle=math.radians(spec.get("angle",0));c=math.cos(angle);s=math.sin(angle)
    axes=np.column_stack((dx,dy))@np.array([[c,-s],[s,c]])@np.diag(spec["half_axes"])
    U,scale,_=np.linalg.svd(axes,full_matrices=False)
    major=Vector(U[:,0].tolist())
    minor=direction.cross(major).normalized()
    rotation=Matrix((major,minor,direction)).transposed().to_euler()
    return {"name":spec["name"],"pixel":spec["pixel"],"position":list(center),"rotation":list(rotation),
            "size":float(np.clip(2*scale[0],.035,3.8)),"size_y":float(np.clip(2*scale[1],.025,2.8)),
            "spread":spec.get("spread",26),"color":spec.get("color",[1,.68,.48]),"energy":20.}

def make_light(scene,row):
    data=bpy.data.lights.new(row["name"],"AREA");data.shape="ELLIPSE"
    data.size=row["size"];data.size_y=row["size_y"];data.energy=row["energy"]
    data.color=row["color"];data.spread=math.radians(row["spread"])
    light=bpy.data.objects.new(row["name"],data);scene.collection.objects.link(light)
    light.location=row["position"];light.rotation_euler=row["rotation"]
    light.visible_diffuse=False;light.visible_glossy=True
    return light

def clear_reflectors(scene):
    for obj in list(scene.objects):
        if obj.type=="LIGHT" and not obj.visible_diffuse and obj.visible_glossy:
            bpy.data.objects.remove(obj,do_unlink=True)

def response(scene,directory):
    path=directory/"lighting-response.exr";scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(path),check_existing=False)
    try:
        w,h=im.size;a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a)
        return a.reshape(h,w,4)[::-1].copy()
    finally:bpy.data.images.remove(im)

def nonnegative_fit(base,responses,target,weight,processor,initial):
    def display(x):
        a=np.ascontiguousarray(x,dtype=np.float32);processor.applyRGB(a);return a.astype(np.float64)
    base=base.astype(np.float64);X=responses.astype(np.float64);power=initial.copy()
    def error(candidate):
        resid=display(base+X@candidate)-target
        return float(np.mean(weight[:,None]*resid*resid))
    errs=[error(power)]
    for _ in range(18):
        lin=base+X@power;prediction=display(lin)
        derivative=[]
        for c in range(3):
            step=np.maximum(.001,lin[:,c]*.012)
            up=lin.copy();down=lin.copy();up[:,c]+=step;down[:,c]=np.maximum(down[:,c]-step,0)
            derivative.append((display(up)-display(down))/(up[:,c]-down[:,c])[:,None])
        J=np.einsum("nct,ncl->ntl",np.stack(derivative,axis=1),X,optimize=True).reshape(-1,len(power))
        wr=np.repeat(weight,3);a=J*np.sqrt(wr[:,None]);rhs=(target-prediction).ravel()+J@power
        G=a.T@a+np.eye(len(power))*.0001;v=J.T@(wr*rhs)
        proposed=power.copy()
        for _ in range(120):
            before=proposed.copy()
            for i in range(len(power)):
                proposed[i]=np.clip(proposed[i]+(v[i]-G[i]@proposed)/max(G[i,i],1e-8),0,35)
            if np.max(np.abs(proposed-before))<1e-5:break
        best=errs[-1]
        for rate in (1,.5,.25,.125,.0625):
            trial=power+rate*(proposed-power);loss=error(trial)
            if loss<best:
                best=loss;power=trial;break
        errs.append(best)
        if errs[-2]-best<2e-8:break
    return power,errs

def run(cfg):
    scene,body=open_source(cfg)
    if cfg.get("finish"):finish(scene,body,cfg["finish"])
    clear_reflectors(scene)
    if "fitted_lights" in cfg:
        for row in cfg["fitted_lights"]:
            if row["energy"]>.00001:make_light(scene,row)
        save_trial(scene,cfg)
        return
    directory=BUILD/cfg["variant"];directory.mkdir(parents=True,exist_ok=True)
    surface=Surface(scene,body);rows=[shape(surface,p) for p in cfg["landmarks"]]
    fixed_lights=[ob for ob in scene.objects if ob.type=="LIGHT"]
    fixed_powers=[ob.data.energy for ob in fixed_lights]
    bg=scene.world.node_tree.nodes["Background"].inputs["Strength"];world_power=bg.default_value
    scene.render.resolution_percentage=50
    scene.cycles.samples=cfg.get("response_samples",96)
    scene.cycles.use_denoising=False;scene.cycles.use_adaptive_sampling=False
    scene.render.image_settings.file_format="OPEN_EXR";scene.render.image_settings.color_depth="32"
    fixed=response(scene,directory)
    rgba=reference_srgb()
    target=rgba.reshape(627,2,627,2,3).mean((1,3))
    mask=(fixed[:,:,3]>.995)&(target.max(2)>.065)
    # Same registered coordinates and foreground for every basis image.
    fixed=fixed[:,:,:3][mask];target=target[mask].astype(np.float64)
    for ob in fixed_lights:ob.data.energy=0
    bg.default_value=0
    reflectors=[];responses=[];scales=[]
    for row in rows:
        ob=make_light(scene,row);reflectors.append(ob)
        a=response(scene,directory)[:,:,:3][mask]
        # Normalize energy columns for the solver; restore actual watts below.
        positive=a.max(1);peak=np.quantile(positive[positive>max(positive.max()*.025,1e-8)],.92)
        scale=1/max(float(peak),.00001)
        responses.append(a*scale);scales.append(scale)
        ob.data.energy=0
        print("PAWN_MEASURED_LIGHT",row["name"],flush=True)
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display=scene.display_settings.display_device,view=scene.view_settings.view_transform)
    processor=config.getProcessor(transform).getDefaultCPUProcessor()
    weight=1+cfg.get("glint_weight",6)*np.clip((target.min(1)-.16)/.55,0,1)
    power,errors=nonnegative_fit(fixed,np.stack(responses,axis=-1),target,weight,processor,np.ones(len(rows)))
    for ob,energy in zip(fixed_lights,fixed_powers):ob.data.energy=energy
    bg.default_value=world_power
    for ob,row,scale,gain in zip(reflectors,rows,scales,power):
        row["energy"]=float(20*scale*gain)
        ob.data.energy=row["energy"]
        if row["energy"]<=.00001:bpy.data.objects.remove(ob,do_unlink=True)
    save_json(directory/"fit.json",{"method":"Actual colored-BSDF isolated area responses, fixed diffuse rig, nonnegative real light energies through the AgX display transform. The independent full render determines the decision.","foreground_pixels":len(target),"loss":errors,"lights":rows,"fixed_light_powers":dict(zip([o.name for o in fixed_lights],fixed_powers))})
    scene.cycles.use_adaptive_sampling=True
    delivery=dict(cfg);delivery.pop("landmarks");delivery["fitted_lights"]=rows
    save_json(directory/"reproduction.json",delivery)
    save_trial(scene,delivery)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(json.loads(a.config.read_text()))

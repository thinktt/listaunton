"""Fit real reflector colors to walnut midtones and highlight distributions."""
import argparse
import json
import sys
from pathlib import Path

import bpy
import numpy as np
import PyOpenColorIO as ocio
sys.path.insert(0,str(Path(__file__).parent))
from capture_pigment import reference_srgb
from fit_lighting import response,clear_reflectors,make_light
from mission_render import ROOT,BUILD,save_json
from polish_trial import open_source,save_trial

W=np.array([.24,.53,.23],dtype=np.float32)


def fitted_color(rest,basis,target,processor):
    def display(gain):
        data=np.ascontiguousarray(np.maximum(rest+basis*gain,0),dtype=np.float32)
        processor.applyRGB(data)
        return data
    influence=np.sum(basis,axis=1)/np.maximum(np.sum(rest+basis,axis=1),1e-5)
    influence=.08+np.clip(influence,0,1)
    quantiles=[.50,.82,.95,.99]
    q_target=np.quantile(target@W,quantiles)
    def loss(gain):
        prediction=display(gain)
        d=prediction-target
        chroma=np.column_stack((d[:,0]-d[:,1],d[:,1]-d[:,2]))
        chroma_loss=np.average((chroma**2).sum(1),weights=influence)
        spatial=np.average((d*d)@W,weights=influence)
        tones=np.quantile(prediction@W,quantiles)-q_target
        return float(1.65*chroma_loss+.37*spatial+np.dot([.13,.20,.26,.41],tones*tones)+.00009*np.sum(np.log(gain)**2))
    gain=np.ones(3)
    initial=loss(gain)
    for step in (.52,.28,.15,.08,.04):
        for _ in range(3):
            prev=gain.copy()
            for c in range(3):
                options=[]
                for d in (-step,0,step):
                    candidate=gain.copy()
                    candidate[c]=np.clip(candidate[c]*np.exp(d),.17,5.)
                    options.append((loss(candidate),candidate))
                gain=min(options,key=lambda pair:pair[0])[1]
            if np.array_equal(prev,gain):
                break
    return gain,{"rgb_gain":gain.tolist(),"loss_before":initial,"loss_after":loss(gain),"reference_quantiles":q_target.tolist(),"predicted_quantiles":np.quantile(display(gain)@W,quantiles).tolist()}


def set_spectra(scene,rows):
    for name,data in rows.items():
        lamp=scene.objects[name].data
        lamp.energy=data["energy"]
        lamp.color=data["color"]


def run(cfg):
    scene,body=open_source(cfg)
    if cfg.get("slope_config"):
        from micro_normals import apply
        apply(scene,body,json.loads((ROOT/cfg["slope_config"]).read_text()))
    if cfg.get("base_rig"):
        rig=json.loads((ROOT/cfg["base_rig"]).read_text())
        clear_reflectors(scene,rig["keep_reflectors"])
        for row in rig["fitted_lights"]:
            if row["energy"]>.00001:
                make_light(scene,row)
    if "spectra" in cfg:
        set_spectra(scene,cfg["spectra"])
        save_trial(scene,cfg)
        return
    out=BUILD/cfg["variant"]
    out.mkdir(parents=True,exist_ok=True)
    scene.render.image_settings.file_format="OPEN_EXR"
    scene.render.image_settings.color_depth="32"
    scene.cycles.samples=cfg.get("response_samples",96)
    full=response(scene,out)
    predicted=full[:,:,:3].copy()
    opaque=full[:,:,3]>.99
    target=reference_srgb()
    y,x=np.mgrid[:1254,:1254]
    lamps=[o for o in scene.objects if o.type=="LIGHT"]
    powers={o.name:o.data.energy for o in lamps}
    colors={o.name:np.array(o.data.color[:]) for o in lamps}
    for ob in lamps:
        ob.data.energy=0
    world=scene.world.node_tree.nodes["Background"].inputs["Strength"]
    strength=world.default_value
    world.default_value=0
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display=scene.display_settings.display_device,view=scene.view_settings.view_transform)
    processor=config.getProcessor(transform).getDefaultCPUProcessor()
    rows={}
    reports={}
    for group in cfg["groups"]:
        members=[scene.objects[n] for n in group["lamps"] if n in powers]
        assert members,group["name"]
        for ob in members:
            ob.data.energy=powers[ob.name]
        isolated=response(scene,out)[:,:,:3]
        for ob in members:
            ob.data.energy=0
        region=np.zeros(opaque.shape,bool)
        for cx,cy,rx,ry in group["ellipses"]:
            region|=((x-cx)/rx)**2+((y-cy)/ry)**2<1
        region&=opaque
        rest=np.maximum(predicted-isolated,0)
        gain,details=fitted_color(rest[region],isolated[region],target[region],processor)
        predicted=rest+isolated*gain
        reports[group["name"]]=details
        for ob in members:
            rgb=colors[ob.name]*gain
            intensity=float(rgb.max())
            rows[ob.name]={"energy":powers[ob.name]*intensity,"color":(rgb/intensity).tolist()}
        print("PAWN_REFLECTOR_COLOR",group["name"],gain.tolist(),flush=True)
    for ob in lamps:
        ob.data.energy=powers[ob.name]
    world.default_value=strength
    set_spectra(scene,rows)
    explicit=dict(cfg)
    explicit.pop("groups");explicit["spectra"]=rows
    save_json(out/"fit.json",{"method":"Measured per-group spectral gain from isolated colored Cycles emitters, fitted to displayed chromatic differences, spatial RGB error and 50th/82nd/95th/99th brightness percentiles.","groups":reports})
    save_json(out/"reproduction.json",explicit)
    save_trial(scene,explicit)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(a.config.read_text()))

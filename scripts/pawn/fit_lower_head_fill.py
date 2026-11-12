"""Measure actual small diffuse emitters beneath the pawn ball, preserving its rig."""
import argparse,json,math,sys
from pathlib import Path
import bpy,numpy as np,PyOpenColorIO as ocio
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,BUILD,Surface,area,save_json
from polish_trial import open_source,save_trial
from fit_lighting import response,nonnegative_fit
from capture_pigment import reference_srgb

def light(scene,spec):
    ob=area(scene,spec["name"],spec["position"],spec["target"],spec["energy"],spec["size"],glossy=False,color=spec.get("color",[1,.97,.93]))
    ob.data.spread=math.radians(spec["spread"])
    return ob

def run(cfg):
    scene,body=open_source(cfg)
    scene.cycles.glossy_bounces=cfg["glossy_bounces"]
    if "fitted_fill" in cfg:
        for row in cfg["fitted_fill"]:light(scene,row)
        save_trial(scene,cfg);return
    out=BUILD/cfg["variant"];out.mkdir(parents=True,exist_ok=True)
    surface=Surface(scene,body);rows=[]
    for i,p in enumerate(cfg["probes"]):
        hit,n=surface.hit(*p["pixel"])
        rows.append({"name":"Lower ball diffuse "+str(i),"position":list(hit+n*p["distance"]),"target":list(hit),
                     "size":p["size"],"spread":p["spread"],"energy":1.0,"color":[1,.97,.93]})
    lamps=[light(scene,spec) for spec in rows]
    for ob in lamps:ob.data.energy=0
    existing=[o for o in scene.objects if o.type=="LIGHT" and o not in lamps]
    powers=[o.data.energy for o in existing]
    world=scene.world.node_tree.nodes["Background"].inputs["Strength"];world_power=world.default_value
    scene.render.image_settings.file_format="OPEN_EXR";scene.render.image_settings.color_depth="32"
    scene.cycles.samples=cfg.get("response_samples",96)
    fixed=response(scene,out);target=reference_srgb()
    edge=np.asarray(json.loads((ROOT/cfg["edge"]).read_text())["edge_xy"]["031-lower-cheek"])
    y,x=np.mgrid[:1254,:1254];dy=y-np.interp(x,edge[:,0],edge[:,1])
    ball=(x>=417)&(x<=549)&(dy>=-23)&(dy<0)
    contact=(x>=414)&(x<=552)&(dy>=0)&(dy<12)
    mask=(fixed[:,:,3]>.995)&(target.max(2)>.025)&(ball|contact|((x%3==0)&(y%3==0)))
    weights=np.ones(mask.shape);weights[ball]=4;weights[contact]=8
    base=fixed[:,:,:3][mask];target=target[mask];weight=weights[mask]
    for ob in existing:ob.data.energy=0
    world.default_value=0
    basis=[];scales=[]
    for ob,spec in zip(lamps,rows):
        ob.data.energy=spec["energy"];a=response(scene,out)[:,:,:3][mask]
        peak=max(float(np.quantile(a.max(1),.99)),.001)
        basis.append(a/peak);scales.append(peak);ob.data.energy=0
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display=scene.display_settings.display_device,view=scene.view_settings.view_transform)
    processor=config.getProcessor(transform).getDefaultCPUProcessor()
    power,loss=nonnegative_fit(base,np.stack(basis,axis=-1),target,weight,processor,np.zeros(len(rows)))
    fitted=[]
    for ob,spec,value,peak in zip(lamps,rows,power,scales):
        energy=float(spec["energy"]*value/peak)
        if energy<1e-5:bpy.data.objects.remove(ob,do_unlink=True)
        else:ob.data.energy=energy;fitted.append(dict(spec,energy=energy))
    for ob,value in zip(existing,powers):ob.data.energy=value
    world.default_value=world_power
    explicit=dict(cfg);explicit.pop("probes");explicit["fitted_fill"]=fitted
    save_json(out/"fit.json",{"method":"Nonnegative fit of measured Cycles responses from physical diffuse-only emitters beside the underside of the ball. Existing lighting held.","probes":rows,"fitted":fitted,"loss":loss})
    save_json(out/"reproduction.json",explicit)
    save_trial(scene,explicit)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(json.loads(a.config.read_text()))

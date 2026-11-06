"""Measure and fit real studio reflections on the swept ear and face."""
from pathlib import Path
import argparse
import json
import math
import sys
import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from fit_chest_reflections import panel_from_samples
from fit_eye_reflection import display_transform
from fit_surface_polish import read_reference
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera


def infer_powers(base,responses,target,weights,transform):
    def error(values):
        val=base.copy()
        for v,b in zip(values,responses):
            if v:val+=v*b
        transform.applyRGB(val)
        # Reward the brighter reference marks while penalizing spill across
        # the rest of the actual piece with a smooth absolute-error objective.
        delta=val-target
        cost=np.sqrt(delta*delta+.045**2)-.045+.45*delta*delta
        return float(np.average(cost.mean(1),weights=weights))
    v=np.zeros(len(responses));initial=best=error(v)
    for step in (1,.25,.0625,.015625,.0039):
        for _ in range(32):
            before=best
            for i in range(len(v)):
                for sign in (-1,1):
                    candidate=v.copy();candidate[i]+=step*sign
                    if not 0<=candidate[i]<=18:continue
                    value=error(candidate)
                    if value<best-1e-8:v,best=candidate,value
            if best==before:break
    return v,initial,best


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
    p.add_argument("--probes",type=Path,required=True);p.add_argument("--variant",required=True)
    opt=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    out=BUILD/opt.variant;out.mkdir(parents=True,exist_ok=True)
    inputs=json.loads(opt.probes.read_text());assert inputs["source_sha256"]==sha(opt.source)
    bpy.ops.wm.open_mainfile(filepath=str(opt.source),load_ui=False);scene=bpy.context.scene
    ears=bpy.data.collections.new("Knight | ear reflection receivers")
    for side in ("near","far"):ears.objects.link(bpy.data.objects[f"Knight | {side} swept ear"])
    skin=bpy.data.collections.get("Knight | chest reflection receivers")
    assert skin and len(skin.objects)==1
    lamps=[];details=[]
    settings=[("ear patch",ears,1.50,(.32,.27),48,.75),
              ("ear edge",ears,1.00,(.12,.08),52,.50),
              ("forehead",skin,1.70,(.27,.23),37,.84),
              ("lower eyelid",skin,.80,(.10,.07),32,.58)]
    for label,collection,distance,margins,spread,width in settings:
        rows=inputs["features"].get(label)
        if not rows:continue
        lamp,detail=panel_from_samples(scene,collection,label,rows,distance,margins)
        lamp.data.size_y*=width;lamp.data.spread=math.radians(spread)
        detail["size"][1]=lamp.data.size_y;detail["spread"]=spread
        lamps.append(lamp);details.append(detail)
    assert lamps
    configure_render(scene,160);scene.render.resolution_percentage=50
    scene.cycles.use_denoising=False;scene.cycles.use_light_tree=False
    base=read_pass(scene,out/"baseline.exr")
    target=read_reference().reshape(627,2,627,2,4).mean(axis=(1,3))
    y,x=np.indices(base.shape[:2]);px=2*x+1;py=2*y+1
    mask=(base[:,:,3]>.995)&(target[:,:,3]>.88)&(target[:,:,:3].max(2)>.06)
    mask&=((x%2==0)&(y%2==0))|((px>270)&(px<645)&(py>355)&(py<514))
    weight=np.ones(base.shape[:2],np.float32)
    for label,(ax,ay) in {"ear patch":(19,10),"ear edge":(22,7),"forehead":(23,11),"lower eyelid":(14,5)}.items():
        bump=np.zeros_like(weight)
        for row in inputs["features"].get(label,[]):
            cx,cy=row["pixel"]
            bump=np.maximum(bump,np.exp(-((px-cx)/ax)**2-((py-cy)/ay)**2))
        weight+=1.8*bump
    samples=base[:,:,:3][mask];responses=[]
    for i,lamp in enumerate(lamps):
        lamp.data.energy=20
        frame=read_pass(scene,out/(f"gloss-{i}.exr"))
        responses.append(np.maximum(0,frame[:,:,:3][mask]-samples));lamp.data.energy=0
    values,initial,best=infer_powers(samples,responses,target[:,:,:3][mask],weight[mask],display_transform(scene))
    for lamp,factor,info in zip(lamps,values,details):
        lamp.data.energy=float(20*factor);info["watts"]=float(lamp.data.energy)
        if not factor:bpy.data.objects.remove(lamp,do_unlink=True)
    configure_render(scene,144);scene.cycles.use_light_tree=True
    cfg={"source_sha256":sha(opt.source),"samples":144,"basis_samples":160,"initial_loss":initial,
         "fitted_loss":best,"sample_count":int(mask.sum()),"lights":details,
         "method":"Fit directed glossy-only area lights using the actual scene response and the projected gradients of the selected reference. Include the whole foreground in the loss."}
    scene["knight_head_reflections"]=json.dumps(cfg);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,144);render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    json_file(out/"parameters.json",cfg)
    print("KNIGHT_HEAD_REFLECTIONS",initial,best,[(r["name"],r["watts"]) for r in details],flush=True)


if __name__=="__main__":main()

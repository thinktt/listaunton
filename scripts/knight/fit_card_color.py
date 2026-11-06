"""Calibrate the warmth and power of the actual collar reflection cards."""
import argparse
import json
from pathlib import Path
import shutil
import sys

import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).parent))
from capture_material import read_pass
from fit_eye_reflection import display_transform
from fit_pedestal_lights import CROP
from fit_surface_polish import read_reference
from mission_scene import BUILD,configure_render,json_file,render,save_model,sha,use_side_camera


def warmth(value):
    return np.array([1,.38+.62*value,.095+.905*value**1.5],np.float32)


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
    p.add_argument("--variant",required=True);p.add_argument("--arcs",type=Path,required=True)
    opt=p.parse_args(sys.argv[sys.argv.index("--")+1:]);out=BUILD/opt.variant;out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(opt.source),load_ui=False);scene=bpy.context.scene
    lamps=[bpy.data.objects[name] for name in ("Walnut | left collar strip","Walnut | right collar strip","Knight | front foot reflector")]
    powers=[ob.data.energy for ob in lamps];prior_colors=[list(ob.data.color) for ob in lamps]
    for lamp in lamps:lamp.data.energy=0
    configure_render(scene,192);scene.cycles.use_denoising=False;scene.cycles.use_light_tree=False
    x0,y0,x1,y1=CROP;w=1254
    scene.render.use_border=True;scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.05)/w;scene.render.border_max_x=(x1+.05)/w
    scene.render.border_min_y=(w-y1+.05)/w;scene.render.border_max_y=(w-y0+.05)/w
    base=read_pass(scene,out/"no-cards.exr")
    ref=read_reference()[y0:y1,x0:x1]
    yy,xx=np.indices(ref.shape[:2]);yy+=y0;xx+=x0
    valid=(ref[:,:,3]>.88)&(base[:,:,3]>.99)&(ref[:,:,:3].max(2)>.045)&((xx+yy)%2==0)
    weight=np.ones(valid.shape,np.float32);arc=json.loads(opt.arcs.read_text())
    for name,amount in [("collar",5.5),("foot",2.3)]:
        d=arc[name]["selected"];r=d["radius_pixels"];cy=d["front_y"]-.809017*r
        q=np.hypot(xx-d["center_x"],(yy-cy)/.809017)
        weight+=amount*np.exp(-((q-r)/4.2)**2)*np.clip((yy-cy-20)/62,0,1)
    weight=weight[valid];target=ref[:,:,:3][valid];start=base[:,:,:3][valid]
    responses=[]
    for i,lamp in enumerate(lamps):
        lamp.data.color=(1,1,1);lamp.data.energy=powers[i]
        frame=read_pass(scene,out/(f"neutral-card-{i}.exr"))
        responses.append(np.maximum(frame[:,:,:3][valid]-start,0));lamp.data.energy=0
    transform=display_transform(scene)
    def error(scales,colors):
        rgb=start.copy()
        for scale,color,response in zip(scales,colors,responses):rgb+=scale*color*response
        transform.applyRGB(rgb)
        delta=rgb-target
        loss=(np.sqrt(delta*delta+.04**2)-.04+.48*delta**2).mean(1)
        return float(np.average(loss,weights=weight))
    foot_color=np.asarray(prior_colors[2],np.float32)
    def colors(t):return [warmth(t),warmth(t),foot_color]
    original=error(np.ones(3),np.asarray(prior_colors,np.float32))
    values=np.array([1.,1.,1.,.76]);best=error(values[:3],colors(values[3]))
    for steps in [(.45,.25),(.16,.10),(.05,.04),(.015,.012)]:
        for _ in range(22):
            before=best
            for i in range(4):
                for sgn in (-1,1):
                    v=values.copy();v[i]+=sgn*steps[int(i==3)]
                    if np.any(v[:3]<0) or np.any(v[:3]>4) or not 0<=v[3]<=1:continue
                    loss=error(v[:3],colors(v[3]))
                    if loss<best-1e-8:best=loss;values=v
            if before==best:break
    if best>=original:
        new_colors=prior_colors;scales=np.ones(3);best=original
    else:
        new_colors=colors(values[3]);scales=values[:3]
    final=[]
    for i,lamp in enumerate(lamps):
        lamp.data.color=new_colors[i];lamp.data.energy=float(powers[i]*scales[i])
        final.append({"name":lamp.name,"watts":float(lamp.data.energy),"color":list(lamp.data.color)})
    scene.render.use_border=False;scene.render.use_crop_to_border=False
    configure_render(scene,144);scene.cycles.use_light_tree=True
    cfg={"source_sha256":sha(opt.source),"samples":144,"measured_samples":192,"prior_powers":powers,
         "prior_colors":prior_colors,"original_loss":original,"fitted_loss":best,"cards":final,
         "method":"Measure neutral-light response for the three retained physical cards. Fit their nonnegative powers and a shared warm spectrum for the collar in the scene's real display transform."}
    scene["knight_warm_turning"]=json.dumps(cfg);save_model(scene,out/"knight.blend")
    bpy.ops.wm.open_mainfile(filepath=str(out/"knight.blend"),load_ui=False);scene=bpy.context.scene
    configure_render(scene,144);render(scene,out/"wood.png");use_side_camera(scene);render(scene,out/"wood-side.png")
    shutil.copyfile(opt.source.parent/"pigment.png",out/"pigment.png")
    json_file(out/"parameters.json",cfg);print("KNIGHT_CALIBRATED_CARD_COLOR",original,best,final,flush=True)


if __name__=="__main__":main()

"""Compare actual fine highlights at several sample counts and two independent seeds."""
import argparse
import sys
from pathlib import Path

import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,BUILD,control,fixed_camera,render,setup,sha,save_json


def run(source,out):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;control(scene);fixed_camera(scene)
    out.mkdir(parents=True,exist_ok=True)
    original_seed=scene.cycles.seed
    boxes={"head":[421,401,548,529],"flare":[349,835,633,927]}
    results={}
    for label,(x0,y0,x1,y1) in boxes.items():
        scene.render.use_border=True
        scene.render.use_crop_to_border=True
        scene.render.border_min_x=x0/1254;scene.render.border_max_x=x1/1254
        scene.render.border_min_y=1-y1/1254;scene.render.border_max_y=1-y0/1254
        for samples,denoise,seed in [(128,True,original_seed),(512,True,original_seed),(768,True,original_seed),(768,True,original_seed+31),(768,False,original_seed)]:
            setup(scene,samples)
            scene.cycles.use_denoising=denoise
            scene.cycles.seed=seed
            name=f"{label}-{samples}-{'clean' if denoise else 'raw'}-{seed}.png"
            render(scene,out/name)
            results[name]=sha(out/name)
    save_json(out/"sampling.json",{"source_sha256":sha(source),"original_seed":original_seed,"bounds_top_left":boxes,"renders":results})


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("directory")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(ROOT/a.source,BUILD/a.directory)

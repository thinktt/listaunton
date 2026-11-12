"""Compare actual fine highlights at several sample counts and two independent seeds."""
import argparse
import sys
from pathlib import Path

import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,BUILD,control,fixed_camera,render,setup,sha,save_json


def run(source,out,boxes=None,light_tree=None):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene;control(scene);fixed_camera(scene)
    if light_tree is not None:scene.cycles.use_light_tree=light_tree
    out.mkdir(parents=True,exist_ok=True)
    original_seed=scene.cycles.seed
    boxes=boxes or {"head":[421,401,548,529],"flare":[349,835,633,927]}
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
    save_json(out/"sampling.json",{"source_sha256":sha(source),"original_seed":original_seed,"light_tree":scene.cycles.use_light_tree,"bounds_top_left":boxes,"renders":results})


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("directory")
    p.add_argument("--regions",type=Path)
    p.add_argument("--no-light-tree",action="store_true")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    import json
    run(ROOT/a.source,BUILD/a.directory,json.loads(a.regions.read_text(encoding="utf-8")) if a.regions else None,False if a.no_light_tree else None)

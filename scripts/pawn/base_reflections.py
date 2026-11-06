"""Measure the base reflectors separately from the rest of the accepted studio."""
import argparse
import json
import sys
from pathlib import Path

import bpy
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,BUILD,control,fixed_camera,render,setup,save_json,sha


def measure(source,out):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    scene=bpy.context.scene
    fixed_camera(scene)
    setup(scene,128)
    body=control(scene)
    lamps=[o for o in scene.objects if o.type=="LIGHT" and o.name.startswith("Base ")]
    assert len(lamps)>=4
    out.mkdir(parents=True,exist_ok=True)
    report={o.name:o.data.energy for o in lamps}
    for lamp in lamps:
        lamp.data.energy=0
    render(scene,out/"without-base-panels.png")
    save_json(out/"base-lights.json",{"source_sha256":sha(source),"rest_render_sha256":sha(out/"without-base-panels.png"),"removed_light_powers":report,"kept_reflectors":[o.name for o in scene.objects if o.type=="LIGHT" and not o.visible_diffuse and o.visible_glossy and o not in lamps]})


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("source",type=Path);p.add_argument("out")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    measure(ROOT/a.source,BUILD/a.out)

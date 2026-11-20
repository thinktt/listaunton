"""Refit specified existing real reflectors while preserving the rest of the rig."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,save_json
from polish_trial import open_source
from fit_lighting import run as fit

def run(cfg):
    scene,_=open_source(cfg)
    names=cfg["refit"]
    rows=[]
    for name in names:
        o=scene.objects[name];d=o.data
        assert o.type=="LIGHT" and d.type=="AREA" and d.shape=="ELLIPSE"
        assert not o.visible_diffuse and o.visible_glossy
        rows.append({"name":name,"position":list(o.location),"rotation":list(o.rotation_euler),
                     "size":d.size,"size_y":d.size_y,"spread":float(d.spread*180/3.141592653589793),
                     "color":list(d.color),"energy":d.energy})
    actual=dict(cfg);actual.pop("refit")
    actual["probe_lights"]=rows
    actual["keep_reflectors"]=[o.name for o in scene.objects if o.type=="LIGHT" and o.name not in names and not o.visible_diffuse and o.visible_glossy]
    if "edge_source" in actual:
        p=ROOT/actual.pop("edge_source")
        actual["contact_edge"]=json.loads(p.read_text())["edge_xy"]["031-lower-cheek"]
    save_json(ROOT/cfg["expanded_config"],actual)
    fit(actual)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path);a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(a.config.read_text()))

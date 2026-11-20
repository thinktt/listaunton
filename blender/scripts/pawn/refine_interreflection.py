"""Test bounded secondary-ray depth, with optional reproducible finish inputs."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from apply_finish import apply
from polish_trial import open_source,save_trial

def run(cfg):
    scene,body=open_source(cfg)
    if "finish" in cfg:
        apply(scene,body,cfg["finish"])
    depths=cfg["ray_depth"]
    assert set(depths).issubset({"glossy_bounces","diffuse_bounces"})
    previous={}
    for key,value in depths.items():
        assert type(value) is int and 0<=value<=4
        previous[key]=getattr(scene.cycles,key)
        setattr(scene.cycles,key,value)
    scene["pawn_secondary_rays"]=json.dumps({"before":previous,"after":depths})
    save_trial(scene,cfg)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(a.config.read_text()))

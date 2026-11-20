"""Save an explicit sampling configuration and render the unchanged pawn scene."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source,save_trial

def run(cfg):
    scene,_=open_source(cfg)
    before={"light_tree":scene.cycles.use_light_tree,"seed":scene.cycles.seed}
    scene.cycles.use_light_tree=cfg["light_tree"]
    scene.cycles.seed=cfg.get("seed",scene.cycles.seed)
    scene["pawn_sampling"]=json.dumps({"samples":cfg["samples"],"light_tree":cfg["light_tree"],"seed":scene.cycles.seed},sort_keys=True)
    print("PAWN_SAMPLING_BEFORE",before,flush=True)
    save_trial(scene,cfg)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path)
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:]);run(json.loads(a.config.read_text(encoding="utf-8")))

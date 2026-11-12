"""Fit thin physical reflectors following the inner groove's curved ray field."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import BUILD,Surface,save_json
from fit_lighting import shape,run as fit

def run(cfg):
    scene,body=open_source(cfg);surface=Surface(scene,body);rows=[]
    for spec in cfg['arc_lights']:
        row=shape(surface,spec['landmark']);row.update(spec['physical']);rows.append(row)
    delivery=dict(cfg);delivery.pop('arc_lights');delivery['probe_lights']=rows
    out=BUILD/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    save_json(out/'measured-light-input.json',delivery);fit(delivery)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(json.loads(a.config.read_text(encoding='utf8')))

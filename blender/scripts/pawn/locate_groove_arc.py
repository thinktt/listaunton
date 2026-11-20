"""Locate the inner-foot meridian at several horizontal image positions."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from polish_trial import open_source
from mission_render import ROOT,Surface,save_json

def run(cfg,out):
    scene,body=open_source(cfg);surface=Surface(scene,body);rows=[]
    for x in cfg['columns']:
        samples=[]
        for j in range(895*4,980*4):
            y=j/4
            try:p,n=surface.hit(x,y)
            except ValueError:continue
            r=(p.x*p.x+p.y*p.y)**.5
            if .72<r<.78:samples.append((abs(p.z-cfg['height']),y,p,n))
        error,y,p,n=min(samples,key=lambda row:row[0])
        rows.append({'pixel':[x,y],'position':list(p),'normal':list(n),'height_error':error})
    save_json(ROOT/out,{'config':cfg,'points':rows});print(json.dumps(rows),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);run(json.loads(a.config.read_text(encoding='utf8')),a.output)

"""Inspect geometric reflection paths in a saved king; never modify the file."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from focused_reflections import target
from render_regions import clear_light_path

def main(source,output):
    source=ROOT/source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
    probes=[]
    for x in (474,554):
        for y in range(416,445):
            ob,p,d,n=target(s,x,y)
            probes.append(dict(pixel=[x,y],receiver=ob.get('king_render_region'),point=list(p),normal=list(n),reflection=list(d),clear=clear_light_path(s,p,n,d,.8)))
    output=ROOT/output;output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(dict(source=str(source.relative_to(ROOT)),source_sha256=digest,probes=probes),indent=2)+'\n',encoding='utf-8')
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    print('COLLAR_NORMAL_PROBES_COMPLETE')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.source,a.output)

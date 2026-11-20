"""Compare evaluated collar sections without editing either source scene."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from check_collar_turning import collar_crossings
p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);report={}
for label,path in [('baseline',a.before),('trial',a.after)]:
    source=ROOT/path;digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    report[label]=collar_crossings();report[label].update(source=path,source_sha256=digest)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
    print(label,json.dumps(report[label]),flush=True)
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

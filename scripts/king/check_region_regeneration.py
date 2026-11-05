"""Ensure editing/regeneration preserves the accepted four-receiver light routes."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import regenerate
from validate_render_regions import check
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;before=check(s);regenerate(s);after=check(s)
assert before['receiverCount']==after['receiverCount']==4 and before['lightRoutes']==after['lightRoutes']
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(dict(source_sha256=digest,source_unchanged=True,regenerated_exact_surfaces=True,routes_preserved=True,before=before,after=after),indent=2)+'\n',encoding='utf-8');print('KING_REGION_REGENERATION_PASS')

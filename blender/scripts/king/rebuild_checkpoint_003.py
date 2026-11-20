"""Reproduce king checkpoint 003 from preserved checkpoint 002.

Run in Blender with -- LABEL. All outputs stay in a fresh build directory;
the accepted model, atlas and review page are not overwritten.
"""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
import curve_cross,focused_reflections,fit_cross_lights,recover_pigment,bake_pigment
p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
assert Path(a.label).name==a.label and a.label not in ('.','..')
base='build/king-mission/'+a.label;assert not (ROOT/base).exists(),'Use a fresh reproduction label.'
evidence=ROOT/'docs/king-mission/iteration-003'
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def config(number):return json.loads((evidence/(number+'-config.json')).read_text())
def step(module,number,name,source):
    cfg=config(number);cfg.update(variant=a.label+'/'+name,source=source,source_sha256=sha(source),neutral=False,profile=False)
    module.main(cfg);return base+'/'+name+'/king.blend'
source='history/king-mission-002/king-rebuilt.blend'
assert sha(source)=='26eeb9b02aae56ebe6057237c4c618ed2a1576679f2d8eea70c9812ed879faf1'
source=step(curve_cross,'024','01-curve',source)
source=step(focused_reflections,'025','02-reflectors',source)
source=step(fit_cross_lights,'026','03-fit',source)
response=base+'/04-response';saved_argv=sys.argv
try:
    sys.argv=['blender','--',source,response,'--object-part','cross']
    runpy.run_path(str(ROOT/'scripts/king/capture_pigment_response.py'),run_name='__main__')
finally:sys.argv=saved_argv
cfg=config('027');cfg.update(variant=a.label+'/05-pigment',response=response,neutral=False,profile=False);recover_pigment.main(cfg)
source=base+'/05-pigment/king.blend';cfg=config('028');cfg.update(variant=a.label+'/06-final',source=source,source_sha256=sha(source),texture=base+'/pigment.png');bake_pigment.main(cfg)
print('KING_CHECKPOINT_003_REPRODUCED',base+'/06-final/king.blend',flush=True)

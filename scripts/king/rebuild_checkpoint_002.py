"""Reproduce king checkpoint 002 from the archived first checkpoint.

Run in Blender with -- LABEL (one directory name). Outputs stay under build;
this does not replace the accepted model, atlas, or review pages.
"""
from pathlib import Path
import argparse,hashlib,runpy,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
import focused_reflections,recover_pigment,polish_relief,bake_pigment
p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
assert Path(a.label).name==a.label and a.label not in ('.','..')
base='build/king-mission/'+a.label
assert not (ROOT/base).exists(),'Use a fresh reproduction label.'
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
source='history/king-mission-001/king-rebuilt.blend'
assert sha(source)=='c0c9a186a39548a6750126a9383d0b6742d52646536bedc7a27a0cfe5a0f37a3'
focused_reflections.main(dict(variant=a.label+'/01-crown',source=source,source_sha256=sha(source),samples=96,neutral=False,profile=False,reflectors=[dict(name='Platter front-right glint',pixel=[580,296],energy=2200,degrees=6,radius=.18),dict(name='Cross arm glint',pixel=[570,85],energy=1400,degrees=14,radius=.18)]))
source=base+'/01-crown/king.blend';response=base+'/02-response'
saved_argv=sys.argv;sys.argv=['blender','--',source,response]
runpy.run_path(str(ROOT/'scripts/king/capture_pigment_response.py'),run_name='__main__');sys.argv=saved_argv
recover_pigment.main(dict(variant=a.label+'/03-pigment',response=response,samples=96,neutral=False,profile=False,strength=.9))
source=base+'/03-pigment/king.blend'
polish_relief.main(dict(variant=a.label+'/04-varnish',source=source,source_sha256=sha(source),samples=128,neutral=False,profile=False,strength=.25,distance=.006))
source=base+'/04-varnish/king.blend'
bake_pigment.main(dict(variant=a.label+'/05-final',source=source,source_sha256=sha(source),texture=base+'/pigment.png',samples=128,neutral=True,profile=True))
print('KING_CHECKPOINT_002_REPRODUCED',base+'/05-final/king.blend',flush=True)

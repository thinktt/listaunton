"""Rebuild checkpoint004 from archived003; never overwrite accepted assets."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
import mission_trial,base_reflection_trial,fit_cross_lights,recover_pigment,base_finish_trial,bake_registered_pigment

def main(label):
    assert Path(label).name==label and label not in ('.','..')
    base='build/king-mission/'+label;assert not (ROOT/base).exists(),'Use a fresh output label.'
    evidence=ROOT/'docs/king-mission/iteration-004'
    def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    def config(number):return json.loads((evidence/(number+'-config.json')).read_text(encoding='utf-8-sig'))
    def step(module,number,name,source):
        cfg=config(number);cfg.update(variant=label+'/'+name,source=source,source_sha256=sha(source),neutral=False,profile=False)
        (module.run if module is mission_trial else module.main)(cfg);return base+'/'+name+'/king.blend'
    source='history/king-mission-003/king-rebuilt.blend';assert sha(source)=='db6167327c1ba4e0073059182bc5aa984dd1e744115557a90bb6cded2766a2b3'
    source=step(mission_trial,'031','01-foot',source)
    source=step(base_reflection_trial,'032','02-receivers',source)
    source=step(fit_cross_lights,'033','03-broad-fit',source)
    source=step(base_reflection_trial,'034','04-focused-glints',source)
    source=step(fit_cross_lights,'035','05-focused-fit',source)
    response=base+'/06-response';saved=sys.argv
    try:
        sys.argv=['blender','--',source,response,'--object-part','body'];runpy.run_path(str(ROOT/'scripts/king/capture_pigment_response.py'),run_name='__main__')
    finally:sys.argv=saved
    cfg=config('036');cfg.update(variant=label+'/07-pigment',response=response,neutral=False,profile=False);recover_pigment.main(cfg)
    source=step(base_finish_trial,'037','08-polish',base+'/07-pigment/king.blend')
    source=step(fit_cross_lights,'038','09-polish-fit',source)
    cfg=config('039');cfg.update(variant=label+'/10-final',source=source,source_sha256=sha(source),texture=base+'/pigment.png',neutral=False,profile=False);bake_registered_pigment.main(cfg)
    print('KING_CHECKPOINT_004_REPRODUCED',base+'/10-final/king.blend',flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.label)

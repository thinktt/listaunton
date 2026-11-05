"""Reproduce the accepted base-reflection refinement from archived checkpoint004."""
from pathlib import Path
import argparse,hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
import base_reflection_trial,local_finish_trial,fit_reflections_display,split_base_receivers

def main(label):
    assert Path(label).name==label and label not in ('.','..')
    base='build/king-mission/'+label;assert not (ROOT/base).exists(),'Use a fresh output label.'
    evidence=ROOT/'docs/king-mission/iteration-005';source='history/king-mission-004/king-rebuilt.blend'
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    assert sha(source)=='a8420d9101f555daadc52a8ae983b0b15cd9ea653097afdeaa0f5fc30972aad6'
    for number,name,module in [('067','01-lower-reflectors',base_reflection_trial),('068','02-local-relief',local_finish_trial),('069','03-initial-fit',fit_reflections_display),('074','04-separated-receivers',split_base_receivers),('075','05-final',fit_reflections_display)]:
        cfg=json.loads((evidence/(number+'-config.json')).read_text(encoding='utf-8-sig'));cfg.update(variant=label+'/'+name,source=source,source_sha256=sha(source),neutral=False,profile=False);module.main(cfg);source=base+'/'+name+'/king.blend'
    print('KING_CHECKPOINT005_REPRODUCED',source,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.label)

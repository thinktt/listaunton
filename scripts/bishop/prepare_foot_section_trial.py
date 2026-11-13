"""Test a flatter foot wall with a tighter upper rollover at fixed framing."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'history/bishop-mission-018/bishop-rebuilt.blend'
out=ROOT/'build/bishop-mission/152-foot-section';out.mkdir(exist_ok=True)
cfg={'variant':'152-foot-wall','source':source.relative_to(ROOT).as_posix(),
     'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
     'profile':'history/bishop-mission-018/profile.json','samples':64,
     'body_rings':{'6':[60.4,202.1],'7':[60.35,201.25],'8':[59.8,200.15],'9':[58.3,199.3]},
     'interpretation':'Unaccepted foot-wall hypothesis: carry the existing maximum radius farther up the vertical wall and tighten its upper rollover. Preserve foot underside, groove, flare, all upper anatomy, camera, references, materials, UVs and lights.'}
(out/'trial.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('Prepared foot-wall trial from unchanged checkpoint 018.')

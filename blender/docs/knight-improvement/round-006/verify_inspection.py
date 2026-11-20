"""Check the fixed, side and bilateral evidence against the exact three judged files."""
from pathlib import Path
from hashlib import sha256
import json,sys
r=Path(sys.argv[1]).resolve()
n=int(sys.argv[2])
b=r/'build/knight-mission'
j=b/f'round-{n:03}-judge'
models={'parent':r/'models/knight/knight-rebuilt.blend'}
for c in ('A','B'):
    t=b/f'improvement-{n:03}-{c}'
    models[c]=t/'knight.blend'
def sha(path):return sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
for k,model in models.items():
    h=sha(model)
    clay=read(j/f'clay-{k}'/'scene.json')
    assert h==clay['model']==read(j/f'eyes-{k}.json')['source_sha256'],k
    for v,f in clay['views'].items():assert sha(j/f'clay-{k}'/(v+'.png'))==f,(k,v)
    if k=='parent':continue
    t=model.parent
    a=read(t/'metrics.json')
    assert a['model_sha256']==h and a['render_sha256']==sha(t/'wood.png')
    assert a['previous_render_sha256']==sha(r/'assets/knight/render.png')
    assert sha(t/'parent.blend')==sha(models['parent']),k
    print(k,'scene',h,'fixed',a['render_sha256'],'side',sha(t/'wood-side.png'))

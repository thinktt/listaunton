"""Check the fixed, side and bilateral evidence against the exact three judged files."""
from pathlib import Path
from hashlib import sha256
import json,sys
r=Path(sys.argv[1]).resolve()
n=int(sys.argv[2])
study=sys.argv[3] if len(sys.argv)>3 else 'eyes'
source_key={'eyes':'source_sha256','ear':'model','chest':'source_sha256','crest':'source_sha256','poll':'source_sha256'}[study]
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
    series='crest' if study=='poll' else study
    assert h==clay['model']==read(j/f'{series}-{k}.json')[source_key],k
    for v,f in clay['views'].items():assert sha(j/f'clay-{k}'/(v+'.png'))==f,(k,v)
    if study in ('chest','crest','poll'):
        wood_dir=j/f'wood-{k}'
        wood=read(wood_dir/'source.json')
        assert h==wood['source_sha256'],k
        for view,digest in wood['outputs'].items():
            assert sha(wood_dir/(view+'.png'))==digest,(k,view)
    if study=='poll':
        assert h==read(j/f'ear-{k}.json')['model'],k
        assert {'front-poll','back-poll'}<=clay['views'].keys(),k
    if study=='crest':
        for label in ('eyes','fixed-eye'):
            assert read(j/f'{label}-{k}.json')['source_sha256']==h,(k,label)
        mat_dir=j/f'passes-{k}'
        mat=read(mat_dir/'source.json')
        assert mat['source_sha256']==h,k
        for view,digest in mat['views'].items():
            assert sha(mat_dir/(view+'.png'))==digest,(k,view)
    if k=='parent':continue
    t=model.parent
    a=read(t/'metrics.json')
    assert a['model_sha256']==h and a['render_sha256']==sha(t/'wood.png')
    assert a['previous_render_sha256']==sha(r/'assets/knight/render.png')
    assert sha(t/'parent.blend')==sha(models['parent']),k
    print(k,'scene',h,'fixed',a['render_sha256'],'side',sha(t/'wood-side.png'))

"""Check the fixed, side and bilateral evidence against the exact three judged files."""
from pathlib import Path
from hashlib import sha256
import json,sys
r=Path(sys.argv[1]).resolve()
n=int(sys.argv[2])
study=sys.argv[3] if len(sys.argv)>3 else 'eyes'
source_key={'eyes':'source_sha256','ear':'model','chest':'source_sha256','crest':'source_sha256','poll':'source_sha256','lids':'source_sha256','brow':'source_sha256','mane':'source_sha256','pigment':'source_sha256','sweep':'source_sha256'}[study]
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
    series={'poll':'crest','lids':'eyes','brow':'eyes','mane':'mane-depth','pigment':'mane-uv','sweep':'eyes'}.get(study,study)
    assert h==clay['model']==read(j/f'{series}-{k}.json')[source_key],k
    for v,f in clay['views'].items():assert sha(j/f'clay-{k}'/(v+'.png'))==f,(k,v)
    if study in ('chest','crest','poll','lids','brow','mane','pigment','sweep'):
        wood_dir=j/f'wood-{k}'
        wood=read(wood_dir/'source.json')
        assert h==wood['source_sha256'],k
        for view,digest in wood['outputs'].items():
            assert sha(wood_dir/(view+'.png'))==digest,(k,view)
    if study=='pigment':
        uv=read(j/f'mane-uv-{k}.json')
        assert uv['physical_uv_pairs_sha256']==sha(j/f'mane-uv-{k}.npz')
        run=read(j/'uv-continuity.json')['models'][k]
        assert run['scene']==h and run['studio_identical'] and len(uv['parts'])==7,k
        for part,changes in run['component_changes'].items():
            assert not changes or (part.endswith('swept rounded mane') and changes==['uv']), (k,part,changes)
        for label,expected in [('mane-passes',{'pigment.png','polish.png'}),('pigment-orbit',
              {f'pigment-{angle}.png' for angle in ('back','near-quarter','far-quarter')})]:
            folder=j/f'{label}-{k}'
            record=read(folder/'source.json')
            files={name if name.endswith('.png') else name+'.png':digest for name,digest in record['views'].items()}
            assert record['source_sha256']==h and set(files)==expected,(k,label)
            for filename,digest in files.items():assert sha(folder/filename)==digest,(k,filename)
    if study=='mane':
        for suffix,key in [('mane-edge','model'),('flanks','source_sha256'),('mane-occlusion','model')]:
            assert h==read(j/f'{suffix}-{k}.json')[key],(suffix,k)
    if study in ('mane','pigment','sweep'):
        folder=j/f'back-{k}'
        record=read(folder/'source.json')
        assert h==record['source_sha256'],k
        expected={f'{finish}-{angle}.png' for finish in ('clay','walnut') for angle in ('back','near-quarter','far-quarter')}
        assert set(record['views'])==expected,k
        for filename,digest in record['views'].items():
            assert sha(folder/filename)==digest,(k,filename)
    if study=='poll':
        assert h==read(j/f'ear-{k}.json')['model'],k
        assert {'front-poll','back-poll'}<=clay['views'].keys(),k
    if study in ('lids','brow','sweep'):
        assert read(j/f'fixed-eye-{k}.json')['source_sha256']==h,k
        directory=j/f'portraits-{k}'
        portraits=read(directory/'source.json')
        assert portraits['model']==h,k
        assert set(portraits['views'])=={f'{finish}-{side}.png' for finish in ('clay','walnut') for side in ('near','far')},k
        for filename,digest in portraits['views'].items():
            assert sha(directory/filename)==digest,(k,filename)
        turns=j/f'turn-eye-{k}'
        turn=read(turns/'source.json')
        assert turn['model']==h and len(turn['views'])==6,k
        for filename,digest in turn['views'].items():
            assert sha(turns/filename)==digest,(k,filename)
        passes=j/f'passes-{k}'
        finish=read(passes/'source.json')
        assert finish['source_sha256']==h,k
        for name,digest in finish['views'].items():
            assert sha(passes/(name+'.png'))==digest,(k,name)
        studio=j/f'studio-{k}'
        source=read(studio/'source.json')
        assert source['model']==h and source['parent_studio']==sha(models['parent']),k
        assert source['render']==sha(studio/'fixed.png'),k
        control=read(j/'eye-studio-comparison.json')['results']['reloaded_identical_scene_mae']
        assert control<.01,control
        if study in ('brow','sweep'):
            exported=read(j/f'exported-faces-{k}.json')
            assert exported['model']==h and len(exported['parts'])==7,k
            assert all(row['double_area_below_1e-10']==0 for row in exported['parts'].values()),k
            trace=read(j/f'brow-native-{k}.json')
            assert trace['model']==h and trace['trace']==sha(b/'round-012-judge/brow-to-nose.json'),k
            baseline=read(j/'studio-parent/source.json')
            assert source['lights']==baseline['lights'] and source['light_groups']==baseline['light_groups'],k
            if study=='brow' and k=='parent':
                for evidence in ('mane-passes-parent','mane-pigment-before'):
                    folder=j/evidence
                    before=read(folder/'source.json')
                    assert before['source_sha256']==h
                    for name,digest in before['views'].items():assert sha(folder/(name+'.png'))==digest
    if study=='sweep':
        owners=read(j/f'brow-owners-{k}.json')
        assert owners['model']==h and owners['reference_trace_sha256']==sha(b/'round-014-judge/upper-eye-sweep.json'),k
        folder=j/f'rake-{k}'
        record=read(folder/'source.json')
        assert record['model']==h and record['framing_model']==sha(models['parent']),k
        assert record['rig']==read(j/'rake-parent/source.json')['rig'],k
        expected={f'{side}-{angle}.png' for side in ('near','far') for angle in ('from-poll','across','from-nose')}
        assert set(record['views'])==expected,k
        for filename,digest in record['views'].items():assert sha(folder/filename)==digest,(k,filename)
        if k=='parent':
            lamps=j/'poll-lights-parent'
            control=read(lamps/'source.json')
            assert control['model']==h and len(control['shots'])==7
            for name,digest in control['shots'].items():assert sha(lamps/(name+'.png'))==digest,name
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

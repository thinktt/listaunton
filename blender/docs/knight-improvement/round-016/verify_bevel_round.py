"""Verify actual three-way review evidence against the unchanged parent and two proposals."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
number = int(sys.argv[2])
build = root / 'build/knight-mission'
judge = build / f'round-{number:03}-judge'
assets = root / 'assets/knight'
def read(path): return json.loads(path.read_bytes())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

parent = root / 'models/knight/knight-rebuilt.blend'
parent_sha = sha(parent)
check = read(assets/'mission-checkpoint.json')
assert parent_sha == check['source_sha256']
assert sha(assets/'ref.png') == read(judge/'crest-anchors.json')['reference_sha256']
control = read(judge/'studio-poll-control/source.json')
assert parent_sha == control['model'] == control['parent_studio']
assert control['render'] == sha(judge/'studio-poll-control/fixed.png')
assert read(judge/'poll-studio-comparison.json')['results']['reloaded_identical_scene_mae'] < .01
trials = {'parent':parent}
for label in ('A','B'):
    trials[label] = build / f'improvement-{number:03}-{label}/knight.blend'
proof = {}
wood_ends = {f'{side}-{place}' for side in ('near','far') for place in ('from-nose','across','from-poll')}
back_ends = {f'{kind}-{angle}' for kind in ('walnut','clay') for angle in ('back','near-quarter','far-quarter')}
for label, model in trials.items():
    sig = sha(model)
    fixed = assets/'render.png' if label=='parent' else model.with_name('wood.png')
    side = assets/'guide-render.png' if label=='parent' else model.with_name('wood-side.png')
    includes = {}
    for prefix, manifest, field, images, names in [
        ('wood','source.json','source_sha256','outputs',{'near','far'}),
        ('clay','scene.json','model','views',{'fixed','side','far-side','rear-quarter','front-poll','back-poll'}),
        ('back','source.json','source_sha256','views',back_ends),
        ('passes','source.json','source_sha256','views',{'pigment','polish'}),
        ('poll-rake','source.json','model','views',wood_ends)]:
        folder = judge/f'{prefix}-{label}'
        doc = read(folder/manifest)
        assert doc[field] == sig,(label,prefix)
        records = {Path(name).stem:digest for name,digest in doc[images].items()}
        assert set(records) == names,(label,prefix)
        for name,digest in records.items():assert sha(folder/(name+'.png')) == digest,(label,prefix,name)
        includes[prefix] = sha(folder/manifest)
        if prefix=='poll-rake':
            assert doc['framing_model']==parent_sha and doc['rig']==read(judge/'poll-rake-parent/source.json')['rig']
    common_folder = judge/f'studio-poll-{label}'
    common = read(common_folder/'source.json')
    assert common['model']==sig and common['parent_studio']==parent_sha and common['render']==sha(common_folder/'fixed.png')
    assert common['lights']==control['lights'] and common['light_groups']==control['light_groups'] and common['crop']==control['crop']
    includes['common_studio'] = sha(common_folder/'source.json')
    native = read(judge/f'crest-{label}.json')
    trace = read(judge/f'poll-trace-{label}.json')
    assert native['source_sha256']==sig and trace['model']==sig and trace['trace']==sha(judge/'crest-anchors.json')
    exported = read(judge/f'exported-faces-{label}.json')
    bevel = read(judge/f'bevel-{label}.json')
    assert exported['model']==bevel['model']==sig and exported['mesh']==bevel['mesh']
    assert len(exported['parts'])==7 and all(row['double_area_below_1e-10']==0 for row in exported['parts'].values())
    uv = read(judge/f'mane-uv-{label}.json')
    assert uv['source_sha256']==sig and uv['physical_uv_pairs_sha256']==sha(judge/f'mane-uv-{label}.npz')
    assert read(judge/'uv-continuity.json')['models'][label]['scene']==sig
    if label!='parent':
        audit = read(model.with_name('metrics.json'))
        assert sha(model.with_name('parent.blend'))==parent_sha
        assert audit['model_sha256']==sig and audit['render_sha256']==sha(fixed)
        assert audit['previous_render_sha256']==sha(assets/'render.png')
        for key,val in audit['source_sha256'].items():assert sha(assets/key)==val
    proof[label] = {'model':sig,'fixed':sha(fixed),'side':sha(side),'mesh':exported['mesh'],'view_manifests':includes}
out={'parent':parent_sha,'models':proof,'source_anchors':sha(judge/'crest-anchors.json'),
     'method':'Each Blender turn, camera crop and moving light is tied to its saved scene. The three common studios use matching transforms and light links. The reference and export checks precede release.'}
(judge/'judge-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print({k:v['model'] for k,v in proof.items()})

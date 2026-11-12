"""Record the rejected iteration-011 finish study without promoting a model."""
import ast,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'docs/bishop-mission/iteration-011';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline='3abfaa8a0980478e095599bcfa3681d51b32fbe742100409ca3586840df33260'
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==baseline
assert sha(ROOT/'history/bishop-mission-010/bishop-rebuilt.blend')==baseline
baseline_scores=json.loads((ROOT/'docs/bishop-mission/iteration-010/scores.json').read_text())
assert sha(ROOT/'assets/bishop/render.png')==baseline_scores['render_sha256']
assert sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png')==baseline_scores['texture_sha256']
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for folder,label in [('087-socket-finish-probe','finish-probe'),('088-socket-emitter-probe','emitter-probe')]:
    src=ROOT/'build/bishop-mission'/folder
    manifest=json.loads((src/'manifest.json').read_text())
    assert manifest['source_unchanged'] and manifest['source_sha256']==baseline
    for path in src.iterdir():
        if path.suffix in {'.png','.json'}:copy(path,out/label/path.name)
copy(ROOT/'build/bishop-mission/finish-details-011.png',out/'finish-details.png')
ratings={89:(84,84,76,75),90:(84,83,76,74),91:(84,84,77,76),92:(84,84,77,75),93:(84,83,76,74)}
reasons={89:'Pore slopes weaken and the finish becomes smoother; no better match.',
90:'Coarse pebbled surface and extra glints worsen the reference finish.',
91:'Relief uses the matching pigment atlas, but no convincing visual improvement is established.',
92:'The reference varnish pattern remains absent; foot and socket regress.',
93:'Overemphasized pigment relief embosses the foot and worsens the socket.'}
trials=[];commands=[]
for number in range(89,94):
    config_path=ROOT/f'scripts/bishop/material-{number:03}.json'
    cfg=json.loads(config_path.read_text());src=ROOT/'build/bishop-mission'/cfg['variant'];dest=out/f'trial-{number:03}'
    params=json.loads((src/'parameters.json').read_text());scope=json.loads((src/'material-scope.json').read_text())
    assert params['source_unchanged'] and params['reopened_before_render'] and params['source_sha256']==baseline
    assert scope['passed'] and scope['source_sha256']==baseline
    assert sha(src/'bishop.blend')==scope['model_sha256']==params['saved_model_sha256']
    assert sha(src/'wood.png')==params['render_sha256']
    for name in ['wood.png','parameters.json','material-scope.json','material-statistics.json']:
        copy(src/name,dest/name)
    for path in (src/'comparison').iterdir():
        if path.suffix in {'.png','.json'}:copy(path,dest/'comparison'/path.name)
    copy(config_path,out/config_path.name)
    metrics=json.loads((src/'comparison/metrics.json').read_text())
    scores=dict(zip(['interior','color','texture','lighting'],ratings[number]))
    scores['silhouette']=100*metrics['images']['selected']['silhouette_iou']
    trials.append({'trial':number,'variant':cfg['variant'],'decision':'Rejected for promotion','reason':reasons[number],
      'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85] if number in {89,91,92} else [74,83],
      'measured_overlap':metrics['images'],'material_scope_passed':True,'source_sha256':baseline,
      'model_sha256':params['saved_model_sha256'],'render_sha256':params['render_sha256']})
    commands += [f'blender --background --python-exit-code 1 --python scripts/bishop/material_input_trial.py -- scripts/bishop/material-{number:03}.json',
      f'blender --background --python-exit-code 1 --python scripts/bishop/validate_material_input_trial.py -- --config scripts/bishop/material-{number:03}.json --model build/bishop-mission/{cfg["variant"]}/bishop.blend --out build/bishop-mission/{cfg["variant"]}/material-scope.json']
views=ROOT/'build/bishop-mission/093-strong-registered-grain/views'
for name in ['head-side.png','side-profile.png','rear-oblique.png','diagnostic-cameras.json']:
    copy(views/name,out/'trial-093/views'/name)
assert sha(ROOT/'build/bishop-mission/093-strong-registered-grain/bishop.blend')==trials[-1]['model_sha256']
for path in (ROOT/'scripts/bishop').glob('*.py'):ast.parse(path.read_text(encoding='utf-8-sig'),filename=str(path))
record={'status':'Research checkpoint; no model promoted; goal remains active.',
 'accepted_checkpoint':10,'accepted_model_sha256':baseline,'render_sha256':baseline_scores['render_sha256'],
 'texture_sha256':baseline_scores['texture_sha256'],'accepted_scores':baseline_scores,
 'full_candidates':trials,'cropped_diagnostics':'Four finish isolations plus four emitter studies, with a control; no whole-model scores assigned.',
 'score_convention':'Silhouette IoU is measured; interior/color/texture/lighting are subjective. Same registration and mission mask. Screening renders: 256 fixed samples; accepted beauty: 512. No rating gain is inferred from a small numerical change.',
 'python_sources_parsed':True,'model_replacement':False,'quota_monitoring':False}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
repro={'source':'history/bishop-mission-010/bishop-rebuilt.blend','source_sha256':baseline,
 'software':'Blender 5.2.2 LTS, Cycles/OptiX; Python with Pillow and NumPy.',
 'probes':[
 'blender --background --python-exit-code 1 --python scripts/bishop/probe_socket_finish.py -- --source history/bishop-mission-010/bishop-rebuilt.blend --samples 256',
 'blender --background --python-exit-code 1 --python scripts/bishop/probe_socket_emitters.py -- --samples 256'],
 'probe_note':'The finish probe originally opened the byte-identical current checkpoint-010 model; use its archive for subsequent reproduction.',
 'full_trials':commands,
 'comparison':'Use mission_compare.py, material_statistics.py, compare_socket_study.py and compare_finish_details.py with the recorded trial paths. No image fitting, color grading or reference modification.',
 'off_axis_diagnostic':'blender --background --python-exit-code 1 --python scripts/bishop/render_diagnostics.py -- --model build/bishop-mission/093-strong-registered-grain/bishop.blend --out build/bishop-mission/093-strong-registered-grain/views',
 'promotion':'None. Preserve checkpoint 010. No viewer or accepted render is rebuilt from these rejected experiments.'}
(out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
print(json.dumps({'accepted_model_unchanged':baseline,'full_material_scope_checks':len(trials),'research_directory':str(out)},indent=2))

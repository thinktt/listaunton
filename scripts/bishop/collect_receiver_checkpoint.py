"""Collect iteration 012 evidence after the saved model and page checks pass."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];build=ROOT/'build/bishop-mission'
out=ROOT/'docs/bishop-mission/iteration-012';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
def write(name,value):
    (out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
def copy(source,target):
    dest=out/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
log=(build/'012-validation.log').read_text(encoding='utf-8-sig')
for script in ['export_mission.py','validate.py','validate_mission.py','check_join_regression.py']:
    assert 'BISHOP_CHECKPOINT_CHECK_PASSED '+script in log,script
model=ROOT/'models/bishop/bishop-rebuilt.blend';render=ROOT/'assets/bishop/render.png'
assert load(ROOT/'assets/bishop/mission-validation.json')['model_sha256']==sha(model)
assert load(ROOT/'assets/bishop/receiver-validation.json')['model_sha256']==sha(model)
viewer=load(build/'012-viewer-check.log');assert viewer['passed'] and viewer['sourceSha256']==sha(model)
assert 'PASS: bishop' in (build/'012-review-check.log').read_text()
final=build/'098-socket-checkpoint';metrics=load(final/'comparison/metrics.json')
assert metrics['render_sha256']==sha(render)
scores={'silhouette':metrics['images']['selected']['silhouette_iou']*100,'interior':84,'color':84,'texture':77,'lighting':77}
write('scores.json',{'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
 'original_white_iou':metrics['images']['original_white']['silhouette_iou'],
 'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
 'silhouette_is_measured_other_scores_are_visual_estimates':True,
 'accepted_model_sha256':sha(model),'render_sha256':sha(render),
 'texture_sha256':sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png'),
 'starting_model_sha256':sha(ROOT/'history/bishop-mission-010/bishop-rebuilt.blend'),
 'status':'Accepted small socket-lighting improvement; full reconstruction remains incomplete.'})
for folder in ['comparison','socket']:
    for p in (final/folder).iterdir():
        if p.is_file():copy(p,Path(folder)/p.name)
for name in ['reopen-validation.json','rgb-statistics.json','export-comparison.json']:
    copy(final/name,name)
for name in ['receiver-validation.json','mission-validation.json','validation.json','base-validation.json','slit-validation.json','join-regression.json']:
    copy(ROOT/'assets/bishop'/name,Path('validation')/name)
for name in ['render-clay.png','side-profile.png','head-side.png','rear-oblique.png','diagnostic-cameras.json']:
    copy(ROOT/'assets/bishop'/name,Path('views')/name)
for name in ['012-viewer-check.log','012-review-check.log','096-material-inspection.log']:
    copy(build/name,Path('validation')/name)
for folder in ['094-socket-receiver-probe','095-socket-spill-probe']:
    for p in (build/folder).iterdir():
        if p.suffix in {'.png','.json'}:copy(p,Path('studies')/folder/p.name)
draft=build/'097-socket-receivers-persistent'
for name in ['parameters.json','receiver-validation.json','rgb-statistics.json']:
    copy(draft/name,Path('studies/097')/name)
for p in (draft/'comparison').iterdir():
    if p.is_file():copy(p,Path('studies/097/comparison')/p.name)
copy(ROOT/'scripts/bishop/receiver-097.json','receiver-097.json')
copy(build/'socket-012-points.json','measured-points.json')
copy(build/'socket-012-landmarks.json','measured-landmarks.json')
write('trials.json',{
 '094':{'kind':'Unsaved cropped BSDF diagnostics','variants':['partition control','confined control','1.4 degree cone','2 degree cone','larger source'],
        'finding':'Exact regions allow wider beams without the false upper-stem arc. Two degrees and radius .024 are the useful draft; larger radius adds no clear benefit.'},
 '095':{'kind':'Unsaved cropped BSDF diagnostics','variants':['socket control','exclude collar reflection','exclude head and collar reflection'],
        'finding':'Collar reflection produces most of the unwanted lower glint. Keep the head lamp unchanged; removing it too adds no convincing benefit.'},
 '096':{'kind':'Invalid save/reopen pipeline test','accepted':False,
        'finding':'Evaluated temporary material pointers became null slots after reopening. This white render is a pipeline failure, not a visual candidate. Persistent control material slots fix the cause; reopened slot assertions prevent recurrence.'},
 '097':{'kind':'Saved/reopened 256-sample full candidate','scores_percent':dict(scores,silhouette=96.10972184363037),'decision':'Promoted for final 512-sample examination, after independent receiver/light-scope checks.'},
 '098':{'kind':'Saved/reopened 512-sample full candidate','scores_percent':scores,'decision':'Accepted with the documented lower-socket tone tradeoff.'}})
write('reproduction.json',{'source':'history/bishop-mission-010/bishop-rebuilt.blend',
 'source_sha256':sha(ROOT/'history/bishop-mission-010/bishop-rebuilt.blend'),
 'config':'docs/bishop-mission/iteration-012/receiver-097.json',
 'commands':[
 'blender --background --python-exit-code 1 --python scripts/bishop/socket_receiver_trial.py -- docs/bishop-mission/iteration-012/receiver-097.json',
 'blender --background --python-exit-code 1 --python scripts/bishop/validate_render_receivers.py -- --config docs/bishop-mission/iteration-012/receiver-097.json --model build/bishop-mission/097-socket-receivers-persistent/bishop.blend --out build/bishop-mission/097-socket-receivers-persistent/receiver-validation.json',
 'blender --background --python-exit-code 1 --python scripts/bishop/finalize_render.py -- --source build/bishop-mission/097-socket-receivers-persistent/bishop.blend --out build/bishop-mission/098-socket-checkpoint --samples 512 --fixed-samples'],
 'follow_up':'In an isolated copy, stage the checked model/render while retaining the profile and atlas. Run validate_checkpoint.py, render_diagnostics.py, render_clay.py, compare.py, mission_compare.py, refresh_review.py and the bishop viewer/review checks before canonical synchronization.',
 'accepted_model_sha256':sha(model),
 'note':'No changes to closed control geometry, UVs, pigment, world, camera, light power/color/position, or four glossy bounces. Derived receivers use the persistent control materials. The renderer uses two exact body surface partitions plus the unchanged button; export retains the two closed editable controls.'})
print('Collected checked bishop checkpoint 012:',sha(model))

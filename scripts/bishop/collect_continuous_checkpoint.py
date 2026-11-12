"""Collect the checked bishop lower-body pigment checkpoint and rejected studies."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];build=ROOT/'build/bishop-mission';out=ROOT/'docs/bishop-mission/iteration-015'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
baseline='df30b53e02c46d75342d6adc88c3fd4ca5889c8f9d7e336bb28a0ca2f40552fb'
assert sha(ROOT/'history/bishop-mission-013/bishop-rebuilt.blend')==baseline
final=build/'125-final';reopen=json.loads((final/'reopen-validation.json').read_text())
assert reopen['samples']==512 and not reopen['adaptive_sampling'] and reopen['camera_preserved']
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==reopen['saved_model_sha256']
assert sha(ROOT/'assets/bishop/render.png')==reopen['render_sha256']
assert sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png')==reopen['texture_sha256']
for name in ['mission-validation.json','receiver-validation.json','pigment-validation.json']:
    report=json.loads((ROOT/'assets/bishop'/name).read_text())
    assert report['passed'] and report['model_sha256']==reopen['saved_model_sha256'],name
def copy(src,dest):
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
specs=[
 ('116-height-pigment',[84,77,75,73],'Height-dependent mean color improves rear continuity but loses too much fixed-view contrast.'),
 ('117-height-pigment-half',[84,82,76,75],'Half blending reduces the regression while retaining a visible side patch; no overall improvement.'),
 ('118-harmonic-pigment',[84,73,73,71],'Smooth angular color further improves the rear but washes out collar and foot details. Retained only as an inferred fallback, not a public model.'),
 ('120-visible-pigment',[84,83,76,75],'Actual visibility and measured pigment improve the base, but uncertain reflective areas are replaced with inappropriate inferred detail.'),
 ('122-visible-feedback',[84,83,76,75],'A second response iteration improves base loss but cannot repair the missing contrast at collars and foot.'),
 ('123-preserved-visible',[84,84,77,76],'Preserving uncertain visible pigment restores some grain. The narrow log-detail bounds still flatten the rings.'),
 ('124-visible-range',[84,85,78,77],'Removing the detail truncation restores the rings and improves the lower body; reject the whole-body version because the upper head regresses.'),
 ('125-final',[84,86,78,77],'Accept the lower-body material after restoring the better upper head/button. Fixed-view tone and rear continuity improve; unresolved side seams and finish remain.')
]
trials=[]
for variant,ratings,reason in specs:
    src=build/variant;dest=out/'trials'/variant
    metrics=json.loads((src/'comparison/metrics.json').read_text())
    scope=json.loads((src/'atlas-scope.json').read_text())
    assert scope['passed'] and scope['source_sha256']==baseline and scope['model_sha256']==sha(src/'bishop.blend')
    assert scope['geometry_uvs_material_graph_relief_camera_lights_world_and_render_path_preserved']
    scores={'silhouette':metrics['images']['selected']['silhouette_iou']*100,**dict(zip(['interior','color','texture','lighting'],ratings))}
    item=dict(trial=variant,decision='accepted' if variant=='125-final' else 'rejected',reason=reason,
        scores_percent=scores,mean_percent=sum(scores.values())/5,
        holistic_range_percent=[70,80] if variant[:3] in ['116','118'] else [75,85],
        silhouette_measured_other_scores_visual_estimates=True,samples=512 if variant=='125-final' else 256,
        fixed_camera_degrees=54,model_sha256=sha(src/'bishop.blend'),render_sha256=sha(src/'wood.png'),
        source_model_sha256=baseline,metrics=metrics['images'])
    for name in ['wood.png','pigment.json','trial-validation.json','atlas-scope.json','statistics.json','atlas-comparison.png','reopen-validation.json']:
        if (src/name).is_file():copy(src/name,dest/name)
    for subdir in ['comparison','views']:
        for path in (src/subdir).glob('*'):
            if path.suffix in ['.png','.json']:copy(path,dest/subdir/path.name)
    (dest/'assessment.json').write_text(json.dumps(item,indent=2)+'\n',newline='\n');trials.append(item)
for name in ['119-current-response','121-response120']:
    copy(build/name/'manifest.json',out/'response-studies'/f'{name}.json')
copy(build/'125-turned-body-pigment/pigment.json',out/'lower-body-blend.json')
copy(build/'125-turned-body-pigment/trial-validation.json',out/'initial-scene-validation.json')
copy(final/'reopen-validation.json',out/'reopen-validation.json')
copy(final/'statistics.json',out/'rgb-statistics.json')
for path in (final/'comparison').iterdir():
    if path.suffix in ['.png','.json']:copy(path,out/'comparison'/path.name)
for name in ['render-clay.png','head-side.png','side-profile.png','rear-oblique.png','diagnostic-cameras.json']:
    copy(ROOT/'assets/bishop'/name,out/'views'/name)
for name in ['validation.json','mission-validation.json','receiver-validation.json','pigment-validation.json','base-validation.json','slit-validation.json','join-regression.json']:
    data=json.loads((ROOT/'assets/bishop'/name).read_text());assert data.get('passed',True)
    copy(ROOT/'assets/bishop'/name,out/'validation'/name)
scores=dict(trials[-1],status='Accepted lower-body pigment improvement; full reconstruction remains incomplete.',
    accepted_model_sha256=reopen['saved_model_sha256'],texture_sha256=reopen['texture_sha256'])
(out/'scores.json').write_text(json.dumps(scores,indent=2)+'\n',newline='\n')
(out/'trials.json').write_text(json.dumps(trials,indent=2)+'\n',newline='\n')
print('BISHOP_CONTINUITY_CHECKPOINT_COLLECTED',json.dumps(scores['scores_percent']),flush=True)

"""Collect checked checkpoint 010 without changing references or shared pages."""
import ast, hashlib, json, shutil
from pathlib import Path
root=Path(__file__).resolve().parents[2]
build=root/'build/bishop-mission'
final=build/'086-final-socket-arc'
out=root/'docs/bishop-mission/iteration-010'
out.mkdir(parents=True,exist_ok=True)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
prior=json.loads((root/'docs/bishop-mission/iteration-009/checkpoint.json').read_text())
reopen=json.loads((final/'reopen-validation.json').read_text())
scope=json.loads((final/'light-scope.json').read_text())
model_hash=sha(root/'models/bishop/bishop-rebuilt.blend')
assert model_hash==reopen['saved_model_sha256']==scope['model_sha256']
assert scope['passed'] and scope['source_sha256']==prior['model_sha256']
assert sha(root/'assets/bishop/render.png')==reopen['render_sha256']
assert sha(root/'assets/bishop/bishop-boxwood-albedo.png')==prior['texture_sha256']
for name,digest in prior['reference_hashes'].items():assert sha(root/'assets/bishop'/name)==digest
assert json.loads((root/'scripts/bishop/profile.json').read_text())==json.loads((root/'history/bishop-mission-009/profile.json').read_text())
for name in ['mission-validation.json','base-validation.json','slit-validation.json','join-regression.json','viewer-validation.json']:
    assert json.loads((root/'assets/bishop'/name).read_text())['passed'],name
mesh=json.loads((root/'assets/bishop/mesh.json').read_text())
assert mesh['sourceSha256']==model_hash
assert json.loads((root/'assets/bishop/camera.json').read_text())==json.loads((root/'history/bishop-mission-009/camera.json').read_text())
log=(build/'validation010.log').read_text()
for name in ['export_mission.py','validate.py','validate_mission.py','check_join_regression.py']:
    assert 'BISHOP_CHECKPOINT_CHECK_PASSED '+name in log
assert 'DIAGNOSTIC_VIEWS_COMPLETE' in (build/'diagnostics010.log').read_text()
assert 'Saved:' in (build/'clay010.log').read_text() and 'Traceback' not in (build/'clay010.log').read_text()
for script in (root/'scripts/bishop').glob('*.py'):ast.parse(script.read_text(encoding='utf-8-sig'))

def copy(source,destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,destination)
for path in (final/'comparison').iterdir():
    if path.is_file():copy(path,out/path.name)
for name in ['wood.png','reopen-validation.json','light-scope.json','material-statistics.json']:
    copy(final/name,out/name)
for path in (final/'socket').iterdir():copy(path,out/'socket'/path.name)
for name in ['validation.json','mission-validation.json','base-validation.json','slit-validation.json','join-regression.json','viewer-validation.json','diagnostic-cameras.json','qa.json','render-clay.png','head-side.png','side-profile.png','rear-oblique.png']:
    copy(root/'assets/bishop'/name,out/name)
copy(root/'scripts/bishop/lighting-085.json',out/'lighting-085.json')
for name in ['points.json','landmarks.json','arc-points.json','arc-landmarks.json','dense-points.json','dense-landmarks.json','light-rig.json','shadow-flags.json']:
    copy(build/'socket-010'/name,out/'measurements'/name)
for folder in ['shading','arc-shading','dense-shading']:
    copy(build/'socket-010'/folder/'manifest.json',out/'measurements'/folder/'manifest.json')
for folder in ['responses-077','responses-079','responses-081','responses-084']:
    for name in ['manifest.json','fit-prediction.png']:
        copy(build/'socket-010'/folder/name,out/'measurements'/folder/name)
copy(build/'socket-010/body-responses/manifest.json',out/'measurements/body-responses/manifest.json')
copy(build/'socket-010/body-responses/socket-isolation.png',out/'measurements/body-responses/socket-isolation.png')
copy(build/'socket-010/mask-baseline/metrics.json',out/'baseline-mask.json')

specs=[
 ('075-aligned-socket-reflection',84,74,'Rejected: pale reflection and extra bright streak on lower socket.'),
 ('078-fitted-socket-spots',84,75,'Rejected: isolated glints and a false stem reflection.'),
 ('080-fitted-narrow-socket-arc',84,76,'Rejected: better lip core but a false upper reflected arc.'),
 ('082-fitted-dense-socket-arc',84,76,'Rejected: requested half-degree cone was clamped to one degree; unwanted stem arc persists.'),
 ('083-no-secondary-socket-gloss',83,74,'Rejected: removing secondary glossy bounces does not remove the stem arc and darkens other details.'),
 ('085-fitted-close-socket-arc',84,76,'Selected for saved/reopened 512-sample confirmation; small improvement with remaining limitations.')]
trials=[]
for folder,color,lighting,decision in specs:
    trial=build/folder
    metrics=json.loads((trial/'comparison/metrics.json').read_text())
    scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'],'interior':84,'color':color,'texture':77,'lighting':lighting}
    for name in ['parameters.json','wood.png']:copy(trial/name,out/'trials'/folder/name)
    for name in ['metrics.json','stem-socket.png','comparison.png']:copy(trial/'comparison'/name,out/'trials'/folder/name)
    trials.append({'trial':folder,'scores_percent':scores,'mean_percent':sum(scores.values())/5,
                   'holistic_range_percent':[75,85],'reference_iou':metrics['images'],
                   'render_sha256':sha(trial/'wood.png'),'model_sha256':sha(trial/'bishop.blend'),
                   'samples':96 if folder.startswith('075') else 128,'decision':decision})
for number in range(75,86):
    config=root/f'scripts/bishop/lighting-{number:03}.json'
    if config.exists():copy(config,out/'trials'/config.name)
(out/'trials.json').write_text(json.dumps(trials,indent=2)+'\n')
metrics=json.loads((out/'metrics.json').read_text())
scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'],'interior':84,'color':84,'texture':77,'lighting':76}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
        'original_white_iou':metrics['images']['original_white']['silhouette_iou'],
        'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
        'silhouette_is_measured_other_scores_are_visual_estimates':True,
        'accepted_model_sha256':model_hash,'render_sha256':reopen['render_sha256'],
        'texture_sha256':prior['texture_sha256'],'starting_model_sha256':prior['model_sha256'],
        'status':'Accepted small socket-lighting improvement; full reconstruction remains incomplete.'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
checkpoint={'date':'2026-11-12','model_sha256':model_hash,'render_sha256':reopen['render_sha256'],
            'starting_model_sha256':prior['model_sha256'],'texture_sha256':prior['texture_sha256'],
            'reference_hashes':prior['reference_hashes'],'camera_elevation_degrees':54,'camera_exactly_unchanged':True,
            'all_piece_checks_passed':True,'declared_light_scope_passed':True,'geometry_uvs_material_pixels_world_preserved':True,
            'existing_socket_light_disabled':True,'added_local_spotlights':17,'glossy_bounces':reopen['glossy_bounces'],
            'beauty_samples':512,'adaptive_sampling':False,'beauty_resolution':reopen['resolution'],
            'saved_and_reopened_before_render':True,'packed_texture_pixel_error':0,
            'site_and_preview_checks':'Awaiting canonical synchronization and actual check results.',
            'render_provenance':{name:sha(root/'assets/bishop'/name) for name in ['render-clay.png','head-side.png','side-profile.png','rear-oblique.png']}}
(out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
repro={'source':'history/bishop-mission-009/bishop-rebuilt.blend','source_sha256':prior['model_sha256'],
       'lighting_config':'docs/bishop-mission/iteration-010/lighting-085.json',
       'commands':[
       'blender --background --python-exit-code 1 --python scripts/bishop/lighting_trial.py -- docs/bishop-mission/iteration-010/lighting-085.json',
       'blender --background --python-exit-code 1 --python scripts/bishop/finalize_render.py -- --source build/bishop-mission/085-fitted-close-socket-arc/bishop.blend --out build/bishop-mission/086-final-socket-arc --samples 512 --fixed-samples',
       'blender --background --python-exit-code 1 --python scripts/bishop/validate_added_reflector.py -- --config docs/bishop-mission/iteration-010/lighting-085.json --model build/bishop-mission/086-final-socket-arc/bishop.blend --disabled-existing "socket reflection" --out build/bishop-mission/086-final-socket-arc/light-scope.json'],
       'follow_up':'After visual inspection, stage the saved model/render in an isolated copy; retain the exact profile and atlas. Run validate_checkpoint.py, render_diagnostics.py, render_clay.py, compare.py, mission_compare.py, refresh_review.py and bishop viewer/review checks before canonical synchronization.',
       'measurement_reproduction':'The archived measured points/normals and prepare_socket_lights.py reproduce the 3-unit, 1-degree spots. capture_socket_reflections.py and fit_socket_reflections.py guide powers; their predictions are not accepted beauty renders.',
       'accepted_model_sha256':model_hash,'note':'No geometry or texture edits. Source references stay unchanged. Blender file serialization need not be byte-identical on another machine.'}
(out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
print(json.dumps(record,indent=2))

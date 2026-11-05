"""Collect evidence for the accepted slit checkpoint; guard against later models."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/bishop-mission/iteration-006'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='319c43917d2084ffd5a0d378a3dec2d5e8cbb803d368730009a79d763aa6d2b3'
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==expected
scope=json.loads((out/'slit-scope-validation.json').read_text());assert scope['passed'] and scope['lights_world_and_materials_preserved']
metrics=json.loads((out/'metrics.json').read_text());assert metrics['render_sha256']==sha(ROOT/'assets/bishop/render.png')
previous=json.loads((ROOT/'docs/bishop-mission/iteration-005/metrics.json').read_text())
assert metrics['images']==previous['images']
prior_checkpoint=json.loads((ROOT/'docs/bishop-mission/iteration-005/checkpoint.json').read_text())
assert sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png')==prior_checkpoint['texture_sha256']
for name,value in prior_checkpoint['reference_hashes'].items():assert sha(ROOT/'assets/bishop'/name)==value
scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'],'interior':83,'color':85,'texture':77,'lighting':72}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
 'original_white_iou':metrics['images']['original_white']['silhouette_iou'],'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
 'silhouette_is_measured_other_scores_are_visual_estimates':True,'accepted_model_sha256':expected,
 'render_sha256':metrics['render_sha256'],'texture_sha256':sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png'),
 'starting_model_sha256':scope['source_sha256'],'status':'accepted local slit improvement; mission incomplete'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
for name in ['validation.json','mission-validation.json','slit-validation.json','join-regression.json','diagnostic-cameras.json','qa.json','viewer-validation.json',
             'render-clay.png','head-side.png','side-profile.png','rear-oblique.png']:
    shutil.copy2(ROOT/'assets/bishop'/name,out/name)
viewer=json.loads((out/'viewer-validation.json').read_text());assert viewer['sourceSha256']==expected and viewer['passed']
assert json.loads((out/'mission-validation.json').read_text())['declared_slit_revision_validated']
for num,folder in [('042','042-rounded-slit-floor'),('043','043-soft-cut-edge'),('044','044-round-floor-only')]:
    trial=ROOT/'build/bishop-mission'/folder
    for source,target in [('parameters.json',f'trial-{num}.json'),('slit-crops.png',f'slit-{num}.png'),('comparison/metrics.json',f'metrics-{num}.json')]:
        shutil.copy2(trial/source,out/target)
repro={'starting_commit':'361fb05','source':scope['config']['source'],'source_sha256':scope['source_sha256'],
      'config':'docs/bishop-mission/iteration-006/slit-044.json','commands':[
       'blender --background --python-exit-code 1 --python scripts/bishop/slit_trial.py -- docs/bishop-mission/iteration-006/slit-044.json',
       'blender --background --python-exit-code 1 --python scripts/bishop/validate_slit_trial.py -- --model build/bishop-mission/044-round-floor-only/bishop.blend --config docs/bishop-mission/iteration-006/slit-044.json --out build/bishop-mission/044-round-floor-only/scope-validation.json'],
       'promotion':'After inspection and scope validation, copy the trial model/render to the bishop model and assets, retain the mission_slit_geometry declaration from scripts/bishop/profile.json, then run validate_checkpoint.py, render_diagnostics.py, render_clay.py, mission_compare.py and refresh_review.py with the ordinary checks.',
       'accepted_model_sha256':expected,'material_and_lighting':'Exactly retained from checkpoint 005; no pigment rebake or camera change.'}
(out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
checkpoint={'starting_commit':'361fb05','model_sha256':expected,'render_sha256':record['render_sha256'],'texture_sha256':record['texture_sha256'],
 'camera_elevation_degrees':54,'camera_exactly_unchanged':True,'geometry_edit':'Rounded termination of the editable saw cutter; no visible control-mesh or UV changes.',
 'declared_cut_scope_passed':True,'all_piece_checks_passed':True,'materials_lights_world_and_packed_images_preserved':True,
 'beauty_samples':96,'beauty_resolution':[1254,1254],'saved_and_reopened_before_render':True,'display_view':'Standard','display_look':'None',
 'silhouette_ious_equal_checkpoint_005':True,'site_and_preview_checks':'Pending canonical synchronization; record actual results before commit.',
 'reference_hashes':{name:sha(ROOT/'assets/bishop'/name) for name in ['reference.png','original.png','black-original.png']},
 'ui_validation':'Simulated DOM/WebGL harness; native browser not inspected.'}
(out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
print(json.dumps(record,indent=2))

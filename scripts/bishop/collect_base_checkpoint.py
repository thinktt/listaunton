"""Collect the inspected, validated bishop base-curvature checkpoint (009)."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/bishop-mission/iteration-009';out.mkdir(parents=True,exist_ok=True)
build=ROOT/'build/bishop-mission';final=build/'074-final-confined-base'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='7308af7e5f82b8747d2db77c8c50d0cbae94b68585b687e74804867ce6ed12fa'
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==expected
assert sha(ROOT/'assets/bishop/render.png')==sha(final/'wood.png')
prior=json.loads((ROOT/'docs/bishop-mission/iteration-007/checkpoint.json').read_text())
for name,value in prior['reference_hashes'].items():assert sha(ROOT/'assets/bishop'/name)==value
assert sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png')==prior['texture_sha256']
for name in ['mission-validation.json','base-validation.json','slit-validation.json','join-regression.json','viewer-validation.json']:
    assert json.loads((ROOT/'assets/bishop'/name).read_text())['passed'],name
mesh=json.loads((ROOT/'assets/bishop/mesh.json').read_text());assert mesh['sourceSha256']==expected
assert json.loads((ROOT/'assets/bishop/camera.json').read_text())==json.loads((ROOT/'history/bishop-mission-007/camera.json').read_text())
scope=json.loads((final/'light-scope.json').read_text());assert scope['passed'] and scope['model_sha256']==expected
reopen=json.loads((final/'reopen-validation.json').read_text());assert reopen['samples']==512 and not reopen['adaptive_sampling']
assert max(reopen['reopened_packed_pixel_max_errors'].values())==0
def copy(src,dest):
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
for source in (final/'comparison').iterdir():
    if source.is_file():copy(source,out/source.name)
for name in ['wood.png','light-scope.json','reopen-validation.json','material-statistics.json','base-statistics.json']:
    copy(final/name,out/name)
for name in ['validation.json','mission-validation.json','base-validation.json','slit-validation.json','join-regression.json','viewer-validation.json','diagnostic-cameras.json','qa.json','render-clay.png','head-side.png','side-profile.png','rear-oblique.png']:
    copy(ROOT/'assets/bishop'/name,out/name)
for name in ['geometry-067.json','lighting-073.json']:copy(ROOT/'scripts/bishop'/name,out/name)
for source,dest in [('base-curvature-007/base-surface.json','base-surface-before.json'),('base-curvature-067/base-surface.json','base-surface-after.json'),
 ('067-smooth-base-curvature/curvature-comparison.json','curvature-comparison.json'),('067-smooth-base-curvature/base-scope.json','isolated-geometry-scope.json'),
 ('lower-glint-landmarks-067.json','reflection-landmarks.json'),('lower-shading-normals-067/manifest.json','shading-normal-manifest.json'),('base-light-power-fit.json','power-fit.json')]:copy(build/source,out/dest)
trials=[]
specs=[('067-smooth-base-curvature',84,84,77,72,'Geometry used later, but the unchanged lighting leaves the core too dim and misplaced.'),
 ('068-smooth-base-reflection',84,84,77,73,'Reject this lighting: better core position, excessive foot reflection.'),
 ('069-final-base-curvature',84,84,77,73,'512-sample check of 068; not accepted because the broader base and foot regress.'),
 ('070-broader-base-reflection',84,84,77,72,'Reject: widened pale light causes an obvious white foot streak.'),
 ('071-confined-base-reflection',84,84,77,74,'Foot spill controlled, core too weak; continue with a power-only fit.'),
 ('073-fitted-confined-reflection',84,84,77,75,'Draft selected for reopened high-sample verification.')]
for folder,interior,color,texture,lighting,decision in specs:
    directory=build/folder;target=out/'trials'/folder;target.mkdir(parents=True,exist_ok=True)
    metrics=json.loads((directory/'comparison/metrics.json').read_text())
    scores={'silhouette':metrics['images']['selected']['silhouette_iou']*100,'interior':interior,'color':color,'texture':texture,'lighting':lighting}
    for name in ['parameters.json','reopen-validation.json','base-statistics.json','light-scope.json']:
        if (directory/name).exists():copy(directory/name,target/name)
    for name in ['base.png','comparison.png','metrics.json']:copy(directory/'comparison'/name,target/name)
    trials.append({'trial':folder,'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
      'reference_iou':metrics['images'],'render_sha256':sha(directory/'wood.png'),'model_sha256':sha(directory/'bishop.blend'),
      'samples':512 if folder.startswith('069') else 96,'decision':decision})
for number in ['068','070','071','072','073']:
    copy(ROOT/f'scripts/bishop/lighting-{number}.json',out/f'trials/lighting-{number}.json')
copy(build/'072-base-light-off-control/parameters.json',out/'trials/072-control.json')
trials.append({'trial':'072-base-light-off-control','role':'Actual lamp-off BSDF control for power fitting; not a beauty candidate.','scored':False})
(out/'trials.json').write_text(json.dumps(trials,indent=2)+'\n')
metrics=json.loads((out/'metrics.json').read_text());assert metrics['render_sha256']==sha(ROOT/'assets/bishop/render.png')
scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'],'interior':84,'color':84,'texture':77,'lighting':75}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
 'original_white_iou':metrics['images']['original_white']['silhouette_iou'],'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
 'silhouette_is_measured_other_scores_are_visual_estimates':True,'accepted_model_sha256':expected,
 'render_sha256':metrics['render_sha256'],'texture_sha256':prior['texture_sha256'],
 'starting_model_sha256':sha(ROOT/'history/bishop-mission-007/bishop-rebuilt.blend'),
 'status':'accepted small base-curve and highlight improvement with recorded tonal tradeoff; mission incomplete'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
repro={'source':'history/bishop-mission-007/bishop-rebuilt.blend','source_sha256':record['starting_model_sha256'],
 'geometry_config':'docs/bishop-mission/iteration-009/geometry-067.json','lighting_config':'docs/bishop-mission/iteration-009/lighting-073.json',
 'commands':[
 'blender --background --python-exit-code 1 --python scripts/bishop/geometry_trial.py -- docs/bishop-mission/iteration-009/geometry-067.json --no-render',
 'blender --background --python-exit-code 1 --python scripts/bishop/lighting_trial.py -- docs/bishop-mission/iteration-009/lighting-073.json',
 'blender --background --python-exit-code 1 --python scripts/bishop/finalize_render.py -- --source build/bishop-mission/073-fitted-confined-reflection/bishop.blend --out build/bishop-mission/074-final-confined-base --samples 512 --fixed-samples'],
 'promotion':'Reproduce in an isolated copy. After actual render inspection, copy final model/render and the generated 067 profile to bishop paths. Retain atlas and existing slit/foot declarations. Run validate_checkpoint.py, render_diagnostics.py, render_clay.py, compare.py, mission_compare.py and refresh_review.py; check pages before synchronizing the owner preview.',
 'accepted_model_sha256':expected,'note':'Hashes identify accepted files, not a promise of byte-identical Blender serialization on another machine. Two radii and one existing light change. No pigment, UV or material-node changes.'}
(out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
checkpoint={'starting_commit':'4044ea2','model_sha256':expected,'render_sha256':record['render_sha256'],'texture_sha256':prior['texture_sha256'],
 'camera_elevation_degrees':54,'camera_exactly_unchanged':True,'all_piece_checks_passed':True,'declared_base_scope_passed':True,
 'declared_light_scope_passed':True,'material_nodes_pixels_uvs_world_preserved':True,'beauty_samples':512,'adaptive_sampling':False,
 'beauty_resolution':[1254,1254],'saved_and_reopened_before_render':True,'display_view':'Standard','display_look':'None',
 'packed_texture_pixel_error':0,'reference_hashes':prior['reference_hashes'],'site_and_preview_checks':'Pending canonical synchronization; fill with actual check results before commit.',
 'ui_validation':'Simulated DOM/WebGL harness; native browser not inspected.'}
(out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
print(json.dumps(record,indent=2))

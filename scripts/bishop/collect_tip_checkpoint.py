"""Collect checked evidence for bishop checkpoint 007 without accepting other trials."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/bishop-mission/iteration-007';out.mkdir(parents=True,exist_ok=True)
build=ROOT/'build/bishop-mission';final=build/'057-final-tip'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='46e8b302ab6340bfddebdc765cd14658eb1fb29185aedab683524e7c008d59d3'
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==expected
assert sha(ROOT/'assets/bishop/render.png')==sha(final/'wood.png')
current_meta=json.loads((ROOT/'assets/bishop/mesh.json').read_text());old_meta=json.loads((ROOT/'history/bishop-mission-006/mesh.json').read_text())
current_bytes=(ROOT/'assets/bishop/mesh.bin').read_bytes();old_bytes=(ROOT/'history/bishop-mission-006/mesh.bin').read_bytes()
assert current_meta['vertexCount']==old_meta['vertexCount']
count=current_meta['vertexCount'];current_vertices=np.frombuffer(current_bytes,dtype='<f4',count=count*8).reshape(-1,8);old_vertices=np.frombuffer(old_bytes,dtype='<f4',count=count*8).reshape(-1,8)
assert np.array_equal(current_vertices[:,:6],old_vertices[:,:6])
assert current_bytes[current_meta['indexByteOffset']:]==old_bytes[old_meta['indexByteOffset']:]
uv_error=float(np.max(np.abs(current_vertices[:,6:]-old_vertices[:,6:])));assert uv_error<1e-7
mesh_check={'positions_normals_and_indices_exactly_unchanged':True,'control_uvs_exactly_unchanged':True,
 'max_evaluated_uv_difference':uv_error,'evaluated_uv_rows_with_rounding_difference':int(np.any(current_vertices[:,6:]!=old_vertices[:,6:],axis=1).sum()),
 'note':'Re-evaluated Boolean UV interpolation differs by at most one float32 rounding step; accepted control UVs are exact in the separate scope audit.'}
assert json.loads((ROOT/'assets/bishop/camera.json').read_text())==json.loads((ROOT/'history/bishop-mission-006/camera.json').read_text())
for name in ['mission-validation.json','slit-validation.json','join-regression.json','viewer-validation.json']:
    assert json.loads((ROOT/'assets/bishop'/name).read_text())['passed'],name
scope=json.loads((final/'light-scope.json').read_text());assert scope['passed'] and scope['model_sha256']==expected
assert scope['camera_controls_uvs_material_pixels_world_and_original_lights_unchanged']
prior=json.loads((ROOT/'docs/bishop-mission/iteration-006/checkpoint.json').read_text())
for name,value in prior['reference_hashes'].items():assert sha(ROOT/'assets/bishop'/name)==value
assert sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png')==prior['texture_sha256']
for source in (final/'comparison').iterdir():
    if source.is_file():shutil.copy2(source,out/source.name)
for name in ['light-scope.json','reopen-validation.json','material-statistics.json','tip-statistics.json','equal-sample-statistics.json','slit-crops.png']:
    shutil.copy2(final/name,out/name)
shutil.copy2(build/'lighting-056.json',out/'lighting-056.json')
for name in ['validation.json','mission-validation.json','slit-validation.json','join-regression.json','viewer-validation.json','diagnostic-cameras.json','qa.json','render-clay.png','head-side.png','side-profile.png','rear-oblique.png']:
    shutil.copy2(ROOT/'assets/bishop'/name,out/name)
for number in ['048','052','056']:
    directory=build/f'tip-convergence-{number}'
    for name in ['manifest.json','statistics.json','comparison.png']:
        if (directory/name).exists():shutil.copy2(directory/name,out/f'convergence-{number}-{name}')
trials=out/'trials';trials.mkdir(exist_ok=True)
for folder in ['047-fitted-bumped-tip','048-white-tip-reflection','049-final-tip-reflection','052-fitted-strong-spot','053-near-soft-spot','054-pigment-boundary','055-brighter-soft-spot','056-aligned-soft-spot']:
    directory=build/folder;target=trials/folder;target.mkdir(exist_ok=True)
    for name in ['parameters.json','lighting-config.json','reopen-validation.json','fit.json','tip-statistics.json','trial-validation.json','extension.json']:
        if (directory/name).exists():shutil.copy2(directory/name,target/name)
    if folder=='054-pigment-boundary':
        for name in ['rear-oblique.png','atlas-comparison.png']:shutil.copy2(directory/name,target/name)
for n in ['045','046','047','051','052','053','055','056']:
    path=build/f'lighting-{n}.json'
    if path.exists():shutil.copy2(path,trials/path.name)
for source,dest in [('pigment-coverage-006/manifest.json','pigment-coverage-manifest.json'),('baseline-006-512/reopen-validation.json','equal-sample-baseline.json')]:shutil.copy2(build/source,out/dest)
metrics=json.loads((out/'metrics.json').read_text());assert metrics['render_sha256']==sha(ROOT/'assets/bishop/render.png')
scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'],'interior':83,'color':85,'texture':77,'lighting':73}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
 'original_white_iou':metrics['images']['original_white']['silhouette_iou'],'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
 'silhouette_is_measured_other_scores_are_visual_estimates':True,'accepted_model_sha256':expected,
 'render_sha256':metrics['render_sha256'],'texture_sha256':prior['texture_sha256'],
 'starting_model_sha256':scope['source_sha256'],'status':'accepted localized slit-tip reflection; mission incomplete'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
repro={'starting_commit':'953d3a9','source':scope['source'],'source_sha256':scope['source_sha256'],
 'config':'docs/bishop-mission/iteration-007/lighting-056.json','commands':[
 'blender --background --python-exit-code 1 --python scripts/bishop/lighting_trial.py -- docs/bishop-mission/iteration-007/lighting-056.json',
 'blender --background --python-exit-code 1 --python scripts/bishop/finalize_render.py -- --source build/bishop-mission/056-aligned-soft-spot/bishop.blend --out build/bishop-mission/057-final-tip --samples 512 --fixed-samples',
 'blender --background --python-exit-code 1 --python scripts/bishop/validate_added_reflector.py -- --config docs/bishop-mission/iteration-007/lighting-056.json --model build/bishop-mission/057-final-tip/bishop.blend --out build/bishop-mission/057-final-tip/light-scope.json'],
 'promotion':'After inspection, copy only the final model/render into the bishop model and assets. Keep the existing atlas and geometry declarations. Run validate_checkpoint.py, render_diagnostics.py, render_clay.py, compare.py, mission_compare.py, refresh_review.py and the affected page checks; synchronize the existing preview.',
 'accepted_model_sha256':expected,'material_and_geometry':'Unchanged from checkpoint 006. One glossy-only body spot added to the unchanged rig.'}
(out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
checkpoint={'starting_commit':'953d3a9','model_sha256':expected,'render_sha256':record['render_sha256'],'texture_sha256':prior['texture_sha256'],
 'camera_elevation_degrees':54,'camera_exactly_unchanged':True,'mesh_preservation':mesh_check,
 'all_piece_checks_passed':True,'declared_light_scope_passed':True,'materials_world_and_original_lights_preserved':True,
 'beauty_samples':512,'adaptive_sampling':False,'beauty_resolution':[1254,1254],'saved_and_reopened_before_render':True,
 'display_view':'Standard','display_look':'None','packed_texture_pixel_error':0,
 'site_and_preview_checks':'Pending canonical synchronization; record actual results before commit.',
 'reference_hashes':prior['reference_hashes'],'ui_validation':'Simulated DOM/WebGL harness; native browser not inspected.'}
(out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
print(json.dumps(record,indent=2))

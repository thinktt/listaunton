"""Collect iteration 004 evidence; refuse to overwrite it from any later model."""
import hashlib,json,shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/bishop-mission/iteration-004'
expected='8e33d8a3855a1cf46ee06f45f7a082840459edaa6e3e6207169fdade99c54a1c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==expected
metrics=json.loads((out/'metrics.json').read_text());assert metrics['render_sha256']==sha(ROOT/'assets/bishop/render.png')
mission=json.loads((ROOT/'assets/bishop/mission-validation.json').read_text())
join=json.loads((ROOT/'assets/bishop/join-regression.json').read_text())
viewer=json.loads((ROOT/'assets/bishop/viewer-validation.json').read_text())
reopen=json.loads((ROOT/'build/bishop-mission/035-clean-button/reopen-validation.json').read_text())
proof=json.loads((ROOT/'build/bishop-mission/034-neutral-shaped-button/parameters.json').read_text())
assert mission['passed'] and join['passed'] and viewer['passed']
assert mission['model_sha256']==viewer['sourceSha256']==reopen['saved_model_sha256']==expected
assert all(error==0 for error in reopen['reopened_packed_pixel_max_errors'].values())
assert proof['geometry_uvs_material_and_camera_unchanged']
assert proof['source_sha256']=='adba4ba0d09952c262c847d8bec79d33eb20df6a128c28b44f3be4556c9aaeb3'
meshes=[];indices=[]
for path in [ROOT/'history/bishop-mission-003',ROOT/'assets/bishop']:
    meta=json.loads((path/'mesh.json').read_text());raw=(path/'mesh.bin').read_bytes()
    meshes.append(np.frombuffer(raw,dtype='<f4',count=meta['vertexCount']*8).reshape(-1,8));indices.append(raw[meta['indexByteOffset']:])
assert np.array_equal(meshes[0][:,:6],meshes[1][:,:6]) and indices[0]==indices[1]
uv_error=float(np.max(np.abs(meshes[0][:,6:]-meshes[1][:,6:])))
assert uv_error<1e-7, 'Evaluated UVs changed beyond the established single-precision export tolerance.'
assert (ROOT/'history/bishop-mission-003/bishop-boxwood-albedo.png').read_bytes()==(ROOT/'assets/bishop/bishop-boxwood-albedo.png').read_bytes()
assert json.loads((ROOT/'history/bishop-mission-003/camera.json').read_text())==json.loads((ROOT/'assets/bishop/camera.json').read_text())
scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'],'interior':81,'color':84,'texture':77,'lighting':66}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
    'original_white_iou':metrics['images']['original_white']['silhouette_iou'],'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
    'silhouette_is_measured_other_scores_are_visual_estimates':True,'accepted_model_sha256':expected,'render_sha256':metrics['render_sha256'],
    'texture_sha256':sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png'),'starting_model_sha256':proof['source_sha256'],
    'status':'Accepted modest button-reflection improvement; mission incomplete. Rear pigment boundary and other reflections remain unresolved.'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
copies={
    'reopen-validation.json':'build/bishop-mission/035-clean-button/reopen-validation.json',
    'lighting-config.json':'build/bishop-mission/034-neutral-shaped-button/lighting-config.json',
    'lighting-trial-validation.json':'build/bishop-mission/034-neutral-shaped-button/parameters.json',
    'button-fit.json':'build/bishop-mission/034-neutral-shaped-button/fit.json',
    'button-prediction.png':'build/bishop-mission/034-neutral-shaped-button/prediction.png',
    'button-response-manifest.json':'build/bishop-mission/button-response-shaped-003/manifest.json',
    'shape-config.json':'build/bishop-mission/033-shaped-button/shape-config.json',
    'shape-points.json':'build/bishop-mission/button-shape-points.json',
    'shape-landmarks.json':'build/bishop-mission/button-shape-landmarks.json',
    'rejected-hidden-continuation.png':'build/bishop-mission/031-global-hidden/rear-comparison.png',
    'rejected-power-only.png':'build/bishop-mission/032-fitted-button/comparison/head.png',
    'rejected-power-only-config.json':'build/bishop-mission/032-fitted-button/lighting-config.json',
    'rejected-power-only-fit.json':'build/bishop-mission/032-fitted-button/fit.json',
    'rejected-unconstrained-prediction.png':'build/bishop-mission/033-shaped-button/prediction.png',
    'hidden-profile-parameters.json':'build/bishop-mission/029-hidden-continuation/parameters.json',
    'hidden-global-parameters.json':'build/bishop-mission/031-global-hidden/parameters.json',
}
for name in ['validation.json','mission-validation.json','join-regression.json','viewer-validation.json','diagnostic-cameras.json','qa.json','side-profile.png','head-side.png','rear-oblique.png','render-clay.png']:
    copies[name]='assets/bishop/'+name
for name,relative in copies.items():shutil.copy2(ROOT/relative,out/name)
checkpoint={'starting_commit':'10fb56b','model_sha256':expected,'render_sha256':metrics['render_sha256'],
    'texture_sha256':record['texture_sha256'],'camera_elevation_degrees':54,'display_view':'Standard','display_look':'None',
    'beauty_samples':96,'beauty_resolution':[1254,1254],'geometry_positions_normals_and_indices_exactly_unchanged_from_checkpoint_003':True,
    'maximum_exported_uv_difference':uv_error,'control_uvs_unchanged':True,
    'pigment_bytes_exactly_unchanged':True,'camera_exactly_unchanged':True,'piece_checks_passed':True,'packed_pixels_equal_after_reopen':True,
    'changed_light_names':['button reflection','Button second glint'],
    'ui_validation':'Simulated DOM/WebGL harness; native browser not inspected.',
    'site_and_preview_checks':'Pending canonical synchronization; record actual results before commit.',
    'reference_hashes':{name:sha(ROOT/'assets/bishop'/name) for name in ['reference.png','original.png','black-original.png']}}
(out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
print(json.dumps(record,indent=2))

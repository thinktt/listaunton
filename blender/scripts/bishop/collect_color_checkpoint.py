"""Record bishop iteration 003; refuse to rewrite this evidence from a later model."""
import hashlib,json,shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'docs/bishop-mission/iteration-003'
expected='adba4ba0d09952c262c847d8bec79d33eb20df6a128c28b44f3be4556c9aaeb3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==expected
metrics=json.loads((out/'metrics.json').read_text());assert metrics['render_sha256']==sha(ROOT/'assets/bishop/render.png')
mission=json.loads((ROOT/'assets/bishop/mission-validation.json').read_text())
join=json.loads((ROOT/'assets/bishop/join-regression.json').read_text())
viewer=json.loads((ROOT/'assets/bishop/viewer-validation.json').read_text())
bake=json.loads((out/'bake-validation.json').read_text())
assert mission['passed'] and join['passed'] and viewer['passed']
assert mission['model_sha256']==viewer['sourceSha256']==bake['saved_model_sha256']==expected
assert bake['input_image_pixels_preserved'] and bake['reopened_packed_pixel_max_error']==0
meshes=[];indices=[]
for path in [ROOT/'history/bishop-mission-002',ROOT/'assets/bishop']:
    meta=json.loads((path/'mesh.json').read_text());raw=(path/'mesh.bin').read_bytes()
    meshes.append(np.frombuffer(raw,dtype='<f4',count=meta['vertexCount']*8).reshape(-1,8))
    indices.append(raw[meta['indexByteOffset']:])
old,new=meshes;assert old.shape==new.shape and np.array_equal(old[:,:6],new[:,:6]) and indices[0]==indices[1]
uv_error=float(np.max(np.abs(old[:,6:]-new[:,6:])));assert uv_error<1e-7
assert json.loads((ROOT/'history/bishop-mission-002/camera.json').read_text())==json.loads((ROOT/'assets/bishop/camera.json').read_text())
scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'],'interior':81,'color':84,'texture':77,'lighting':64}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
    'original_white_iou':metrics['images']['original_white']['silhouette_iou'],'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
    'silhouette_is_measured_other_scores_are_visual_estimates':True,'accepted_model_sha256':expected,'render_sha256':metrics['render_sha256'],
    'texture_sha256':sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png'),'starting_model_sha256':sha(ROOT/'history/bishop-mission-002/bishop-rebuilt.blend'),
    'status':'accepted fixed-view material improvement, mission incomplete; rear pigment transition and reflections still need work'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
for name in ['validation.json','mission-validation.json','join-regression.json','viewer-validation.json','diagnostic-cameras.json','qa.json']:
    shutil.copy2(ROOT/'assets/bishop'/name,out/name)
for name in ['side-profile.png','head-side.png','rear-oblique.png','render-clay.png']:
    shutil.copy2(ROOT/'assets/bishop'/name,out/name)
checkpoint={'starting_commit':'4c3188f','model_sha256':expected,'render_sha256':metrics['render_sha256'],
    'texture_sha256':record['texture_sha256'],'camera_elevation_degrees':54,'display_view':'Standard','display_look':'None',
    'beauty_samples':96,'beauty_resolution':[1254,1254],'geometry_positions_normals_and_indices_exactly_unchanged_from_checkpoint_002':True,
    'maximum_exported_uv_difference':uv_error,'camera_exactly_unchanged':True,'piece_checks_passed':True,
    'input_images_unchanged_during_bake':True,'packed_pixels_equal_after_reopen':True,
    'raw_to_baked_mean_absolute_rgb_difference_8bit':.9099,
    'ui_validation':'Simulated DOM/WebGL harness; native browser not inspected.',
    'site_and_preview_checks':'Pending canonical synchronization; record actual results before commit.',
    'reference_hashes':{name:sha(ROOT/'assets/bishop'/name) for name in ['reference.png','original.png','black-original.png']}}
(out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
print(json.dumps(record,indent=2))

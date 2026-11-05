"""Collect bishop checkpoint 005, guarded against reuse with another model."""
import hashlib,json,math,shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/bishop-mission/iteration-005'
expected='f16145ddeaa44988403e18dddc41bffefc4e4751b2e6417422080ec4bf94fd32'
start='8e33d8a3855a1cf46ee06f45f7a082840459edaa6e3e6207169fdade99c54a1c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads((ROOT/p).read_text())
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==expected
metrics=read('docs/bishop-mission/iteration-005/metrics.json');assert metrics['render_sha256']==sha(ROOT/'assets/bishop/render.png')
mission=read('assets/bishop/mission-validation.json');join=read('assets/bishop/join-regression.json');viewer=read('assets/bishop/viewer-validation.json')
bake=read('build/bishop-mission/040-baked-rebalance/bake-validation.json')
p36=read('build/bishop-mission/036-dark-environment-reflection/parameters.json')
p37=read('build/bishop-mission/037-confined-lower-reflectors/parameters.json')
p38=read('build/bishop-mission/038-rebalanced-pigment/parameters.json')
assert mission['passed'] and join['passed'] and viewer['passed']
assert mission['model_sha256']==viewer['sourceSha256']==bake['saved_model_sha256']==expected
assert p36['source_sha256']==start and p37['source_sha256']==p36['saved_model_sha256']
assert p38['source_sha256']==p37['saved_model_sha256'] and bake['source_sha256']==p38['saved_model_sha256']
assert p36['geometry_uvs_material_and_camera_unchanged'] and p37['geometry_uvs_material_and_camera_unchanged']
assert bake['input_image_pixels_preserved'] and bake['reopened_packed_pixel_max_error']==0
assert bake['texture_sha256']==sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png')
arrays=[];indices=[]
for folder in ['history/bishop-mission-004','assets/bishop']:
    meta=read(folder+'/mesh.json');raw=(ROOT/folder/'mesh.bin').read_bytes()
    arrays.append(np.frombuffer(raw,dtype='<f4',count=meta['vertexCount']*8).reshape(-1,8));indices.append(raw[meta['indexByteOffset']:])
assert np.array_equal(arrays[0][:,:6],arrays[1][:,:6]) and indices[0]==indices[1]
uv_error=float(np.max(np.abs(arrays[0][:,6:]-arrays[1][:,6:])));assert uv_error<1e-7
assert read('history/bishop-mission-004/camera.json')==read('assets/bishop/camera.json')
old_rig=read('build/bishop-mission/light-rig-004.json');new_rig=read('build/bishop-mission/light-rig-005.json')
old_lights={x['name']:x for x in old_rig['lights']};new_lights={x['name']:x for x in new_rig['lights']}
assert old_lights.keys()==new_lights.keys()
changes={x['name']:x for x in p37['config']['lights']}
for name,old in old_lights.items():
    new=new_lights[name]
    for key,value in old.items():
        if name in changes and key in ['energy','spread']:continue
        assert new[key]==value,(name,key)
    if name in changes:
        assert abs(new['energy']-changes[name]['energy'])<1e-5
        assert abs(new['spread']-math.radians(changes[name]['spread_degrees']))<1e-6
world={n['name']:n for n in new_rig['world_nodes']}
assert world['Background']==next(n for n in old_rig['world_nodes'] if n['name']=='Background')
assert world['Bishop glossy environment']['inputs']['Strength']==0
assert ['Bishop environment ray type','Is Glossy Ray','Bishop diffuse and glossy environment','Factor'] in new_rig['world_links']
assert ['Bishop diffuse and glossy environment','Shader','World Output','Surface'] in new_rig['world_links']
branches={(l['to_socket_index'],l['from_node']) for l in new_rig['world_link_details'] if l['to_node']=='Bishop diffuse and glossy environment'}
assert branches=={(0,'Bishop environment ray type'),(1,'Background'),(2,'Bishop glossy environment')}
scores={'silhouette':metrics['images']['selected']['silhouette_iou']*100,'interior':81,'color':85,'texture':77,'lighting':72}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
    'original_white_iou':metrics['images']['original_white']['silhouette_iou'],'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
    'silhouette_is_measured_other_scores_are_visual_estimates':True,'accepted_model_sha256':expected,'render_sha256':metrics['render_sha256'],
    'texture_sha256':bake['texture_sha256'],'starting_model_sha256':start,
    'status':'Accepted lighting/color improvement; mission incomplete. Slit termination, fine reflections and rear pigment continuity remain unresolved.'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
copies={
    'lighting-036.json':'build/bishop-mission/lighting-036.json',
    'lighting-037.json':'build/bishop-mission/037-confined-lower-reflectors/lighting-config.json',
    'normalization.json':'build/bishop-mission/037-confined-lower-reflectors/normalization.json',
    'light-rig-before.json':'build/bishop-mission/light-rig-004.json',
    'light-rig-after.json':'build/bishop-mission/light-rig-005.json',
    'body-response-manifest.json':'build/bishop-mission/body-response-004/manifest.json',
    'body-response-analysis.json':'build/bishop-mission/body-response-004/analysis.json',
    'diagnostic-head-subtractions.png':'build/bishop-mission/body-response-004/head-subtractions.png',
    'confined-response-manifest.json':'build/bishop-mission/body-response-confined-036/manifest.json',
    'material-response-manifest.json':'build/bishop-mission/material-response-037/manifest.json',
    'pigment-fit.json':'build/bishop-mission/038-rebalanced-pigment/parameters.json',
    'bake-validation.json':'build/bishop-mission/040-baked-rebalance/bake-validation.json',
    'rejected-grazing-extension.json':'build/bishop-mission/041-grazing-continuity/extension.json',
    'rejected-grazing-model.json':'build/bishop-mission/041-grazing-continuity/trial-validation.json',
    'rejected-grazing-metrics.json':'build/bishop-mission/041-grazing-continuity/comparison/metrics.json',
    'rejected-grazing-rear.png':'build/bishop-mission/041-grazing-continuity/diagnostics/rear-oblique.png',
    'rejected-grazing-atlas.png':'build/bishop-mission/041-grazing-continuity/atlas-comparison.png',
    'facing-visibility-manifest.json':'build/bishop-mission/facing-visibility-040/manifest.json',
    'conservative-extension.json':'build/bishop-mission/039-harmonic-probe/extension.json',
    'conservative-extension-atlas.png':'build/bishop-mission/039-harmonic-probe/atlas-comparison.png',
}
for name in ['validation.json','mission-validation.json','join-regression.json','viewer-validation.json','diagnostic-cameras.json','qa.json','side-profile.png','head-side.png','rear-oblique.png','render-clay.png']:
    copies[name]='assets/bishop/'+name
for name,path in copies.items():shutil.copy2(ROOT/path,out/name)
checkpoint={'starting_commit':'612517d','model_sha256':expected,'render_sha256':record['render_sha256'],'texture_sha256':record['texture_sha256'],
    'camera_elevation_degrees':54,'camera_exactly_unchanged':True,'geometry_positions_normals_and_indices_exactly_unchanged_from_checkpoint_004':True,
    'maximum_exported_uv_difference':uv_error,'piece_checks_passed':True,'input_image_pixels_preserved_during_bake':True,'packed_pixels_equal_after_reopen':True,
    'beauty_samples':96,'beauty_resolution':[1254,1254],'display_view':'Standard','display_look':'None',
    'lighting_scope_validated':True,'changed_area_lights':list(changes),'glossy_environment_strength':0,'diffuse_environment_unchanged':True,
    'reference_hashes':{name:sha(ROOT/'assets/bishop'/name) for name in ['reference.png','original.png','black-original.png']},
    'ui_validation':'Simulated DOM/WebGL harness; native browser not inspected.',
    'site_and_preview_checks':'Pending canonical synchronization; record actual results before commit.'}
(out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n');print(json.dumps(record,indent=2))

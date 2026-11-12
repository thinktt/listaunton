"""Record rejected bishop base-finish studies without changing the public model."""
import hashlib, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
build=ROOT/'build/bishop-mission'
out=ROOT/'docs/bishop-mission/iteration-016'
out.mkdir(parents=True,exist_ok=True)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
prior=json.loads((ROOT/'docs/bishop-mission/iteration-015/checkpoint.json').read_text())
baseline=prior['accepted_model_sha256']
assert sha(ROOT/'history/bishop-mission-015/bishop-rebuilt.blend')==baseline
for relative,digest in prior['public_stage_canonical_preview_identical_files'].items():
    assert sha(ROOT/relative)==digest,('Public artifact changed',relative)

def copy(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,dest)

for folder in ['126-polish-fields','127-polish-probe','128-base-receiver-probe',
               '129-base-receiver-probe','130-base-material-isolation','131-base-response']:
    source=build/folder
    manifest=json.loads((source/'manifest.json').read_text())
    assert manifest.get('source_sha256',baseline)==baseline
    if 'source_unchanged' in manifest:assert manifest['source_unchanged']
    for path in source.iterdir():
        if path.suffix in {'.json','.png'}:copy(path,out/'studies'/folder/path.name)
copy(build/'129-base-probes.json',out/'studies/129-base-probes.json')
copy(build/'129-original-power-fit.json',out/'studies/129-original-power-fit.json')
trials=[]
for folder in ['132-base-pigment','133-base-channel-balance']:
    source=build/folder
    validation=json.loads((source/'trial-validation.json').read_text())
    pigment=json.loads((source/'pigment.json').read_text())
    metrics=json.loads((source/'comparison/metrics.json').read_text())
    assert validation['source_sha256']==baseline and validation['reopened_before_render']
    assert validation['packed_pixel_max_error']==0
    assert validation['atlas_sha256']==sha(source/'albedo.png')==pigment['output_sha256']
    assert pigment['source_sha256']==baseline and pigment['alpha_and_outside_scope_exact']
    assert metrics['render_sha256']==sha(source/'wood.png')
    for path in source.iterdir():
        if path.suffix in {'.json','.png'}:copy(path,out/'trials'/folder/path.name)
    for path in (source/'comparison').iterdir():
        if path.suffix in {'.json','.png'}:copy(path,out/'trials'/folder/'comparison'/path.name)
    scores=dict(silhouette=metrics['images']['selected']['silhouette_iou']*100,
                interior=84,color=85,texture=78,lighting=77)
    trials.append(dict(trial=folder,decision='rejected',samples=512,
        source_model_sha256=baseline,model_sha256=validation['saved_model_sha256'],
        render_sha256=sha(source/'wood.png'),atlas_sha256=sha(source/'albedo.png'),
        scores_percent=scores,mean_percent=sum(scores.values())/5,
        silhouette_measured_other_ratings_subjective=True,
        reason='Lower pixel error does not remove the local green/yellow patch or recover the reference glint structure. Retain checkpoint 015.',
        saved_and_reopened=True,packed_pixel_max_error=0,
        full_promotion_audit_run=False,
        validation_limit='Rejected by visual comparison before the independent whole-scene promotion audit; never synchronized as current.'))
scripts=['prepare_spatial_polish.py','probe_spatial_polish.py','analyze_spatial_polish.py',
         'probe_base_receiver.py','analyze_base_reflection.py','render_material_diagnostics.py',
         'fit_base_light_power.py','capture_material_response.py','refine_base_pigment.py',
         'record_base_finish_study.py']
commands=[
 'python scripts/bishop/prepare_spatial_polish.py',
 'blender --background --python-exit-code 1 --python scripts/bishop/probe_spatial_polish.py',
 'python scripts/bishop/analyze_spatial_polish.py',
 'blender --background --python-exit-code 1 --python scripts/bishop/probe_base_receiver.py',
 'python scripts/bishop/analyze_base_reflection.py --probe build/bishop-mission/128-base-receiver-probe',
 'blender --background --python-exit-code 1 --python scripts/bishop/probe_base_receiver.py -- --config docs/bishop-mission/iteration-016/studies/129-base-probes.json --out build/bishop-mission/129-base-receiver-probe',
 'python scripts/bishop/analyze_base_reflection.py --probe build/bishop-mission/129-base-receiver-probe',
 'blender --background --python-exit-code 1 --python scripts/bishop/render_material_diagnostics.py -- --source history/bishop-mission-015/bishop-rebuilt.blend --out build/bishop-mission/130-base-material-isolation --fixed-view --crop 460 920 690 1090 --samples 256',
 'blender --background --python-exit-code 1 --python scripts/bishop/capture_material_response.py -- --source history/bishop-mission-015/bishop-rebuilt.blend --out build/bishop-mission/131-base-response --crop 430 860 740 1060 --samples 512',
 'python scripts/bishop/refine_base_pigment.py',
 'python scripts/bishop/refine_base_pigment.py --out build/bishop-mission/133-base-channel-balance --clipped-bound-weight 1 --max-gain 2',
]
for folder in ['132-base-pigment','133-base-channel-balance']:
    commands.extend([
        f'blender --background --python-exit-code 1 --python scripts/bishop/apply_atlas_trial.py -- --source history/bishop-mission-015/bishop-rebuilt.blend --atlas build/bishop-mission/{folder}/albedo.png --variant {folder} --samples 512',
        f'python scripts/bishop/mission_compare.py --render build/bishop-mission/{folder}/wood.png --previous history/bishop-mission-015/render.png --out build/bishop-mission/{folder}/comparison',
        f'python scripts/bishop/material_statistics.py history/bishop-mission-015/render.png build/bishop-mission/{folder}/wood.png --out build/bishop-mission/{folder}/material-statistics.json'
    ])
reproduction=dict(source='history/bishop-mission-015/bishop-rebuilt.blend',source_sha256=baseline,
    prerequisite='Recreate build/bishop-mission/099-atlas-surface and visibility using the first two commands in iteration-015/reproduction.json. The immutable 013 and 015 atlas audits establish unchanged geometry.',
    commands=commands,environment='Blender 5.2.2 Cycles OPTIX; ordinary Python with NumPy and Pillow.',
    scripts={f'scripts/bishop/{name}':sha(ROOT/'scripts/bishop'/name) for name in scripts},
    note='Rejected diagnostics and trials only. Do not overwrite accepted model/review assets. EXR/NumPy working arrays are reproducible scratch data and are not repository assets.')
(out/'reproduction.json').write_text(json.dumps(reproduction,indent=2)+'\n',newline='\n')
(out/'trials.json').write_text(json.dumps(trials,indent=2)+'\n',newline='\n')
scores=dict(accepted_checkpoint='015',accepted_model_sha256=baseline,
    scores_percent=prior['scores_percent'],mean_percent=prior['mean_percent'],
    holistic_fixed_view_range_percent=[75,85],silhouette_measured_other_ratings_subjective=True,
    unchanged_from_accepted_checkpoint=True,mission_complete=False)
(out/'scores.json').write_text(json.dumps(scores,indent=2)+'\n',newline='\n')
print('BISHOP_BASE_FINISH_STUDY_RECORDED',json.dumps(scores),flush=True)

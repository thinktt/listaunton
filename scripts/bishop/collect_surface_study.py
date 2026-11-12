"""Collect iteration 014 research without replacing the accepted bishop."""
import ast,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
build=ROOT/'build/bishop-mission';out=ROOT/'docs/bishop-mission/iteration-014'
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
accepted=json.loads((ROOT/'docs/bishop-mission/iteration-013/checkpoint.json').read_text())
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==accepted['model_sha256']
assert sha(ROOT/'assets/bishop/render.png')==accepted['render_sha256']
assert sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png')==accepted['atlas_sha256']
assert sha(ROOT/'history/bishop-mission-013/bishop-rebuilt.blend')==accepted['model_sha256']
files=[]
def copy(source,destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,destination)
    files.append(dict(source=source.relative_to(ROOT).as_posix(),
                      archived=destination.relative_to(ROOT).as_posix(),sha256=sha(destination)))
for folder in ['107-collar-isolation','108-collar-normals','109-collar-basis','111-collar-spots','113-cool-collar-fit']:
    for path in sorted((build/folder).glob('*')):
        if path.suffix in {'.json','.png'}:copy(path,out/'diagnostics'/folder/path.name)
copy(build/'107-collar-light-rig.json',out/'diagnostics/107-collar-light-rig.json')
copy(build/'114-115-detail-comparison.png',out/'details.png')
trials={}
for folder,score in [('112-collar-spots',[96.11,84,85,77,77]),
                     ('114-fine-relief',[96.11,84,85,77,77]),
                     ('115-fine-relief-stronger',[96.11,84,85,76,76])]:
    source=build/folder
    validation=source/('light-scope.json' if folder.startswith('112') else 'material-scope.json')
    assert json.loads(validation.read_text())['passed']
    for path in sorted(source.rglob('*')):
        if path.is_file() and path.suffix in {'.png','.json'}:
            copy(path,out/'trials'/folder/path.relative_to(source))
    stat=json.loads((source/'statistics.json').read_text())['renders']
    rendered=stat[(source/'wood.png').relative_to(ROOT).as_posix()]
    metrics=json.loads((source/'comparison/metrics.json').read_text())
    trials[folder]=dict(decision='reject',model_sha256=sha(source/'bishop.blend'),render_sha256=sha(source/'wood.png'),
         samples=128 if folder.startswith('112') else 256,
         scores=dict(zip(['silhouette_and_placement','interior_form','wood_color','grain_and_surface','lighting_and_reflections'],score)),
         measured_silhouette=metrics['images'],regional_rgb=rendered,
         independent_reopened_scope_passed=True,public_assets_changed=False)
logs=['107-light-rig.log','107-probe.log','108-landmarks.log','108-normals.log','109-collar-basis.log',
      '111-collar-spots.log','112-collar-trial.log','112-light-scope.log','114-fine-relief.log',
      '114-material-scope.log','114-views.log','115-fine-relief.log','115-material-scope.log','115-views.log']
for name in logs:copy(build/name,out/'logs'/name)
(out/'trials.json').write_text(json.dumps(dict(category_order=list(next(iter(trials.values()))['scores']),trials=trials,
 note='Subjective scores accompany measured overlap, not derived from RGB error. 128/256-sample studies are not directly equivalent to the 512-sample accepted render; tiny differences include sampling and denoising. No trial is accepted.'),indent=2)+'\n',newline='\n')
scripts=['probe_collar_reflections.py','assess_collar_isolation.py','capture_collar_basis.py','fit_collar_basis.py',
         'capture_collar_spots.py','fit_collar_spots.py','validate_collar_lights.py','prepare_fine_relief.py',
         'fine_relief_trial.py','validate_fine_relief.py','compare_fine_relief_details.py','collect_surface_study.py']
for name in scripts:ast.parse((ROOT/'scripts/bishop'/name).read_text(encoding='utf-8'))
for path in out.rglob('*.json'):json.loads(path.read_text())
record=dict(iteration='014',date='2026-11-12',classification='research; no accepted model change',
 goal='active and incomplete; owner confirmed no pause requested',accepted_checkpoint='013',
 model_sha256=accepted['model_sha256'],render_sha256=accepted['render_sha256'],atlas_sha256=accepted['atlas_sha256'],
 fixed_camera_degrees=54,accepted_scores=[96.10946013611408,84,85,77,77],accepted_mean=83.82189202722282,
 accepted_holistic_range=[75,85],python_syntax_checked=scripts,source_and_model_preserved=True,
 note='All observations are local renders and file audits. No new browser inspection, quota monitoring, push or publication.',files=files)
(out/'research.json').write_text(json.dumps(record,indent=2)+'\n',newline='\n')
print('COLLECTED_BISHOP_014',len(files),'evidence files; public checkpoint remains 013')

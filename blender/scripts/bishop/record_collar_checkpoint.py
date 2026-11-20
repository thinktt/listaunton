"""Collect the independent surface diagnosis and reproduction for geometry 018."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/bishop-mission/iteration-018'
analysis=ROOT/'build/bishop-mission/144-surface-audit'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def copy(source,relative):
    target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
for name in ['slit-boundary.json','slit-boundary-comparison.png','geometry-rows.json','turning-edges.json',
             'upper-collar-neck-fit.json','upper-collar-neck-fit-report.json','middle-collar-neck-fit.json','middle-collar-neck-fit-report.json']:
    copy(analysis/name,'diagnosis/'+name)
for name in ['white-head-contour.png','selected-head-contour.png']:
    copy(analysis/name,'diagnosis/'+name)
trial=ROOT/'build/bishop-mission/146-middle-collar-neck';final=ROOT/'build/bishop-mission/147-middle-collar-checkpoint'
copy(trial/'independent-scope.json','validation/trial-independent-scope.json')
copy(trial/'anatomy.json','validation/trial-anatomy.json')
copy(final/'independent-scope.json','validation/final-independent-scope.json')
before=json.loads((analysis/'turning-edges.json').read_text())
after=json.loads((out/'geometry/turning-edges.json').read_text())
old_rows=json.loads((analysis/'geometry-rows.json').read_text())
new_rows=json.loads((out/'geometry/geometry-rows.json').read_text())
front=lambda j:j['front_bands']['middle_collar']['front_band_lowest_projected_point']['y']
assert after['source_sha256']==sha(ROOT/'models/bishop/bishop-rebuilt.blend')
evidence={'source_checkpoint':'017','current_model_sha256':after['source_sha256'],
    'middle_collar_front_extent_before':front(before),'middle_collar_front_extent_after':front(after),
    'front_extent_displacement_px':front(after)-front(before),
    'lower_head_image_rows_before':old_rows['results']['white']['lower_head'],
    'lower_head_image_rows_after':new_rows['results']['white']['lower_head'],
    'outline_surface_identity':'First-hit surface rays locate the former bulge on middle-collar control ring 54, behind the head.',
    'first_hypothesis_rejected':'An upper-collar-only fit selected zero displacement. Do not infer which 3D part causes an image-space outline just from its image position.',
    'cut_result':'The ray-projected interior boundary closely follows selected white 3 and the blurred white original. Its broader-looking lower end is largely shading; cutter/head/button unchanged.',
    'remaining':'This does not prove every other internal shape correct. Socket lip, lower-collar underside and button/foot edge residuals need separate examination.'}
(out/'surface-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
metrics=json.loads((out/'comparison/metrics.json').read_text())
entries=[]
for variant,decision,percent in [
    ('145-upper-collar-neck','No-op control: the optimizer selected zero displacement; no geometry improvement or public promotion.',96.81388324257657),
    ('146-middle-collar-neck','Accepted shape for final rendering: coupled middle-collar radius and height correction.',100*json.loads((trial/'comparison/metrics.json').read_text())['images']['selected']['silhouette_iou']),
    ('147-middle-collar-checkpoint','Accepted saved/reopened 512-sample checkpoint; same physical geometry as 146.',100*metrics['images']['selected']['silhouette_iou'])]:
    folder=ROOT/'build/bishop-mission'/variant;audit=json.loads((folder/'trial-audit.json').read_text())
    scores={'silhouette':percent,'interior':86 if variant.startswith('145') else 87,'color':83,'texture':77,'lighting':72}
    entries.append({'variant':variant,'model_sha256':sha(folder/'bishop.blend'),'render_sha256':sha(folder/'wood.png'),
        'config':audit['config'],'scores_percent':scores,'mean_percent':sum(scores.values())/5,'decision':decision})
(out/'trials.json').write_text(json.dumps({'note':'Outline overlap measured; other ratings are subjective. The no-op shares the baseline geometry score. No finish improvement is claimed.','trials':entries},indent=2)+'\n')
repro={'source':'history/bishop-mission-017/bishop-rebuilt.blend','source_sha256':before['source_sha256'],
    'config':'docs/bishop-mission/iteration-018/profile-fit.json','config_sha256':sha(out/'profile-fit.json'),
    'commands':['blender --background --python-exit-code 1 --python scripts/bishop/profile_shape_trial.py -- docs/bishop-mission/iteration-018/profile-fit.json',
        'blender --background --python-exit-code 1 --python scripts/bishop/validate_profile_shape.py -- --model build/bishop-mission/147-middle-collar-checkpoint/bishop.blend --config docs/bishop-mission/iteration-018/profile-fit.json --profile build/bishop-mission/147-middle-collar-checkpoint/profile.json --out build/bishop-mission/147-middle-collar-checkpoint/independent-scope.json'],
    'promotion':'After inspecting the saved/reopened trial, copy bishop.blend/profile.json/wood.png/neutral.png to the current model, profile, render.png and render-clay.png. Preserve the atlas.',
    'refresh':['blender --background --python-exit-code 1 --python scripts/bishop/validate_checkpoint.py',
        'blender --background --python-exit-code 1 --python scripts/bishop/render_diagnostics.py',
        'python scripts/bishop/compare.py','python scripts/bishop/mission_compare.py --render assets/bishop/render.png --previous history/bishop-mission-017/render.png --out docs/bishop-mission/iteration-018/comparison',
        'python scripts/bishop/refresh_review.py','node scripts/bishop/check_viewer.cjs','node scripts/bishop/check_review.cjs'],
    'environment':'Blender 5.2.2 Cycles/OPTIX; Python with NumPy/Pillow. Use an isolated working copy.',
    'limits':'Blender saved-file bytes and evaluated Boolean UV hashes can vary; geometry, shader, camera and light snapshots match. Exact receiver checks retain the existing 1e-7 UV tolerance. No source pixel, alignment or mission change.'}
(out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
print(json.dumps(evidence,indent=2))

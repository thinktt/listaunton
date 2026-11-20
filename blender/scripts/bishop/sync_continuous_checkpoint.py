"""Deliver the checked bishop checkpoint to the owner's existing repo and preview.

Explicitly scoped to bishop artifacts. Run from WSL with the canonical and
preview paths supplied; no Git stage/commit/push or site publication occurs.
"""
import argparse,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--canonical',type=Path,required=True);p.add_argument('--preview',type=Path,required=True)
a=p.parse_args();canonical=a.canonical.resolve();preview=a.preview.resolve()
assert canonical==Path('/home/toby/code/listaunton')
assert preview==Path('/mnt/c/Users/toby/Documents/Codex/2026-10-01/go-x20/outputs/queen-hires')
assert canonical!=ROOT and preview!=ROOT
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
prior=json.loads((ROOT/'docs/bishop-mission/iteration-014/checkpoint.json').read_text())
public=prior['public_stage_canonical_preview_identical_files']
# Refuse to overwrite independent bishop work since the last checkpoint.
for relative,digest in public.items():assert sha(canonical/relative)==digest,relative
old_log=(canonical/'docs/bishop-mission-log.md').read_text()
new_log=(ROOT/'docs/bishop-mission-log.md').read_text()
assert new_log.startswith(old_log.rstrip()+'\n'),'Concurrent bishop log change'
scores=json.loads((ROOT/'docs/bishop-mission/iteration-015/scores.json').read_text())
model_hash=scores['accepted_model_sha256']
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==model_hash
for name in ['mission-validation.json','receiver-validation.json','pigment-validation.json']:
    report=json.loads((ROOT/'assets/bishop'/name).read_text())
    assert report['passed'] and report['model_sha256']==model_hash,name
for name in ['validation.json','mission-validation.json','receiver-validation.json','pigment-validation.json','base-validation.json','slit-validation.json','join-regression.json']:
    assert sha(ROOT/'assets/bishop'/name)==sha(ROOT/'docs/bishop-mission/iteration-015/validation'/name),('Stale collected evidence',name)
validation_log=(ROOT/'build/bishop-mission/125-checkpoint-validation.log').read_text()
for script in ['export_mission.py','validate.py','validate_mission.py','check_join_regression.py']:
    assert 'BISHOP_CHECKPOINT_CHECK_PASSED '+script in validation_log,script
viewer=(ROOT/'build/bishop-mission/125-viewer-check.log').read_text()
review=(ROOT/'build/bishop-mission/125-review-check.log').read_text()
viewer_report=json.loads(viewer)
assert viewer_report['passed'] and viewer_report['sourceSha256']==model_hash and 'PASS: bishop' in review
protected=[
 'MISSION-BISHOP.md','MISSION-SET.md','assets/side-views/scale.json',
 'assets/side-views/defaults.json','assets/candidates/alignment.json',
 'references/lichess-staunton-3d/White-Bishop.png','references/lichess-staunton-3d/Black-Bishop.png',
 'assets/candidates/bishop/white-candidate-3.png'
]
protected_hashes={name:sha(canonical/name) for name in protected}
def copy(relative,destination):
    target=destination/relative
    assert target.resolve().is_relative_to(destination)
    mode=target.stat().st_mode & 0o777 if target.exists() else 0o644
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,target)
    if destination==canonical:target.chmod(mode)
for relative in public:
    assert relative.startswith(('assets/bishop/','models/bishop/')) or relative in ['bishop-model.html','bishop-review.html']
    copy(relative,canonical);copy(relative,preview)
scripts=[
 'height_continuous_pigment.py','infer_visible_pigment.py','blend_pigment_band.py',
 'pigment-125.json','prepare_continuous_checkpoint.py','collect_continuous_checkpoint.py',
 'validate_pigment_history.py','validate_mission.py','sync_continuous_checkpoint.py'
]
copied=[f'scripts/bishop/{name}' for name in scripts]+['docs/bishop-mission-log.md']
copied += [path.relative_to(ROOT).as_posix() for path in (ROOT/'docs/bishop-mission/iteration-015').rglob('*') if path.is_file()]
for relative in copied:copy(relative,canonical)
delivered={relative:sha(ROOT/relative) for relative in public}
for relative,digest in delivered.items():
    assert sha(canonical/relative)==digest and sha(preview/relative)==digest,relative
for relative,digest in protected_hashes.items():assert sha(canonical/relative)==digest,relative
checkpoint=dict(classification='accepted lower-body pigment checkpoint',
    accepted_model_sha256=model_hash,accepted_render_sha256=scores['render_sha256'],
    accepted_atlas_sha256=scores['texture_sha256'],public_stage_canonical_preview_identical_files=delivered,
    canonical_protected_file_hashes=protected_hashes,all_saved_model_checks_passed=True,
    viewer_and_review_checks_passed=True,native_browser_inspection=False,
    source_camera_degrees=54,scores_percent=scores['scores_percent'],mean_percent=scores['mean_percent'],
    mission_complete=False,goal_status='active',no_quota_monitoring=True,no_push=True,
    note='Only bishop files copied. Shared gallery scaling and other pieces stay untouched. Blender file, packed texture, fixed/side/clay images and exported geometry refer to the same checked model.')
relative='docs/bishop-mission/iteration-015/checkpoint.json'
(ROOT/relative).write_text(json.dumps(checkpoint,indent=2)+'\n',newline='\n');copy(relative,canonical)
print(json.dumps(dict(synchronized=True,public_files=len(delivered),evidence_and_script_files=len(copied)+1,model_sha256=model_hash),indent=2))

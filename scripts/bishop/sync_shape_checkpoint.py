"""Deliver checked bishop geometry 017 without touching other pieces or missions."""
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
prior=json.loads((ROOT/'docs/bishop-mission/iteration-016/checkpoint.json').read_text())
public=prior['public_stage_canonical_preview_identical_files']
for relative,digest in public.items():
    assert sha(canonical/relative) in (digest,sha(ROOT/relative)),('Concurrent bishop work',relative)
old_log=(canonical/'docs/bishop-mission-log.md').read_text()
assert (ROOT/'docs/bishop-mission-log.md').read_text().startswith(old_log.rstrip()+'\n')
out=ROOT/'docs/bishop-mission/iteration-017'
scores=json.loads((out/'scores.json').read_text());model_hash=scores['model_sha256']
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==model_hash
for name in ['mission-validation.json','receiver-validation.json','pigment-validation.json','base-validation.json','slit-validation.json']:
    report=json.loads((ROOT/'assets/bishop'/name).read_text())
    assert report['passed'] and report['model_sha256']==model_hash,name
for name in ['validation.json','mission-validation.json','receiver-validation.json','pigment-validation.json','base-validation.json','slit-validation.json','join-regression.json']:
    assert sha(ROOT/'assets/bishop'/name)==sha(out/'validation'/name),('Stale evidence',name)
viewer=json.loads((out/'validation/viewer.json').read_text(encoding='utf-8-sig'))
assert viewer['passed'] and viewer['sourceSha256']==model_hash
assert 'PASS: bishop' in (out/'validation/review.txt').read_text(encoding='utf-8-sig')
protected=['AGENTS.md','assets/side-views/scale.json','assets/side-views/defaults.json','assets/candidates/alignment.json',
    'references/lichess-staunton-3d/White-Bishop.png','references/lichess-staunton-3d/Black-Bishop.png',
    'assets/candidates/bishop/white-candidate-3.png']
protected += [path.name for path in canonical.glob('MISSION-*.md')]
protected_hashes={name:sha(canonical/name) for name in protected}
for name in ['MISSION-BISHOP.md','MISSION-SET.md']:
    assert protected_hashes[name]==prior['canonical_protected_file_hashes'][name]
def copy(relative,destination):
    target=destination/relative
    assert target.resolve().is_relative_to(destination)
    if target.exists() and sha(target)==sha(ROOT/relative):return
    mode=target.stat().st_mode & 0o777 if target.exists() else 0o644
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,target)
    if destination==canonical:target.chmod(mode)
for relative in public:
    assert relative.startswith(('assets/bishop/','models/bishop/')) or relative in ['bishop-model.html','bishop-review.html']
    copy(relative,canonical);copy(relative,preview)
scripts=['README.md','profile.json','inspect_profile_landmarks.py','fit_profile_outline.py','profile_shape_trial.py',
    'validate_profile_shape.py','measure_collar_geometry.py','collect_shape_checkpoint.py','sync_shape_checkpoint.py',
    'record_shape_trials.py','validate.py','validate_mission.py','validate_checkpoint.py','compare.py',
    'viewer-template.html','build_viewer.py','check_viewer.cjs']
copied=[f'scripts/bishop/{name}' for name in scripts]+['docs/bishop-mission-log.md']
copied += [path.relative_to(ROOT).as_posix() for path in out.rglob('*') if path.is_file()]
for relative in copied:copy(relative,canonical)
delivered={relative:sha(ROOT/relative) for relative in public}
for relative,digest in delivered.items():
    assert sha(canonical/relative)==digest and sha(preview/relative)==digest,relative
for relative,digest in protected_hashes.items():assert sha(canonical/relative)==digest,relative
checkpoint={'classification':'Accepted geometry checkpoint; inherited finish remains unfinished','accepted_checkpoint':'017',
    'accepted_model_sha256':model_hash,'accepted_render_sha256':scores['render_sha256'],
    'accepted_atlas_sha256':scores['atlas_sha256'],'public_stage_canonical_preview_identical_files':delivered,
    'canonical_protected_file_hashes':protected_hashes,'all_saved_model_checks_passed':True,
    'viewer_and_review_checks_passed':True,'native_browser_inspection':False,'source_camera_degrees':54,
    'scores_percent':scores['scores_percent'],'mean_percent':scores['mean_percent'],
    'geometry_phase_complete':False,'mission_complete':False,'goal_status':'active','no_quota_monitoring':True,'no_push':True,
    'note':'Only bishop files copied. Neutral is the review default. The old material/lights are retained without hiding their mismatch. Other pieces and shared gallery settings are untouched.'}
relative='docs/bishop-mission/iteration-017/checkpoint.json'
(ROOT/relative).write_text(json.dumps(checkpoint,indent=2)+'\n',newline='\n');copy(relative,canonical)
manifest=sorted(set(list(public)+copied+[relative]))
(ROOT/'build/bishop-mission/143-delivered-files.json').write_text(json.dumps({r:sha(ROOT/r) for r in manifest},indent=2)+'\n')
print(json.dumps({'synchronized':True,'public_files':len(public),'evidence_and_script_files':len(copied)+1,'model_sha256':model_hash},indent=2))

"""Deliver a checked bishop geometry checkpoint without touching other pieces."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--canonical',type=Path,required=True);p.add_argument('--preview',type=Path,required=True)
p.add_argument('--checkpoint',default='017');p.add_argument('--previous',default='016');p.add_argument('--log-prefix',default='143')
p.add_argument('--archive',help='Optional already-created bishop checkpoint archive to preserve in the repository.')
a=p.parse_args();canonical=a.canonical.resolve();preview=a.preview.resolve()
assert a.checkpoint.isdigit() and a.previous.isdigit() and a.log_prefix.isdigit()
assert canonical==Path('/home/toby/code/listaunton')
assert preview==Path('/mnt/c/Users/toby/Documents/Codex/2026-10-01/go-x20/outputs/queen-hires')
assert canonical!=ROOT and preview!=ROOT
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
prior=json.loads((ROOT/f'docs/bishop-mission/iteration-{a.previous}/checkpoint.json').read_text())
public=prior['public_stage_canonical_preview_identical_files']
for relative,digest in public.items():
    assert sha(canonical/relative) in (digest,sha(ROOT/relative)),('Concurrent bishop work',relative)
old_log=(canonical/'docs/bishop-mission-log.md').read_text()
assert (ROOT/'docs/bishop-mission-log.md').read_text().startswith(old_log.rstrip()+'\n')
out=ROOT/f'docs/bishop-mission/iteration-{a.checkpoint}'
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
warp_rulers='assets/board-comparison/warp-rulers.json'
if (canonical/warp_rulers).is_file():protected.append(warp_rulers)
protected_hashes={name:sha(canonical/name) for name in protected}
for name in ['MISSION-BISHOP.md','MISSION-SET.md']:
    if protected_hashes[name]!=prior['canonical_protected_file_hashes'][name]:
        # The owner can revise a mission between checkpoints. Deliver against
        # that committed version and pin its current bytes across this copy.
        subprocess.run(['git','-C',str(canonical),'diff','--quiet','HEAD','--',name],check=True)
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
    'record_shape_trials.py','record_collar_checkpoint.py','capture_slit_boundary.py','compare_slit_boundary.py','analyze_geometry_rows.py',
    'fit_upper_collar_shape.py','capture_turning_edges.py','render_geometry_studio.py',
    'prepare_collar_section_trials.py','prepare_collar_shelf_trial.py','prepare_foot_section_trial.py',
    'prepare_button_rim_trial.py','prepare_button_lens_trial.py','validate_shape_trial.py','check_join_regression.py',
    'record_foot_checkpoint.py','record_button_checkpoint.py','validate.py','validate_mission.py','validate_checkpoint.py','compare.py',
    'prepare_local_curvature_trials.py','measure_socket_join.py','record_socket_checkpoint.py',
    'prepare_head_turn_trials.py','probe_opposite_slit_pose.py','measure_head_turn.py',
    'prepare_collar_neck_trial.py','measure_collar_occlusion.py','record_collar_occlusion_checkpoint.py',
    'capture_contour_meridians.py','fit_stem_shoulder.py','infer_contour_sections.py','measure_stem_profile.py',
    'prepare_stem_checkpoint.py','record_stem_checkpoint.py','compare_stem_trial.py',
    'viewer-template.html','build_viewer.py','check_viewer.cjs']
if (out/'turning.json').is_file():
    scripts+=['shared_turning.py','inspect_shared_turning.py','fit_shared_upper.py',
              'validate_shared_turning.py','compare_shared_turning.py','refresh_set_entry.py',
              'check_served_checkpoint.py']
if (out/'side-refit.json').is_file():
    scripts+=['shared_turning.py','side_refit.py','side_refit_profile.py','fit_side_refit.py','compare_side_refit.py',
              'validate_side_refit.py','render_diagnostics.py','review-template.html','build_review.py','check_served_checkpoint.py']
if (out/'cut-plane.json').is_file():
    scripts+=['fit_locked_height.py','fit_surface_slot.py','heal_slit_atlas.py','compare_locked_height.py']
copied=[f'scripts/bishop/{name}' for name in scripts]+['docs/bishop-mission-log.md']
copied += [path.relative_to(ROOT).as_posix() for path in out.rglob('*') if path.is_file()]
if a.archive:
    assert a.archive.isdigit()
    archive=ROOT/f'history/bishop-mission-{a.archive}'
    for path in archive.rglob('*'):
        if path.is_file():
            relative=path.relative_to(ROOT).as_posix()
            if (canonical/relative).exists():assert sha(canonical/relative)==sha(path),('Archive differs',relative)
            copied.append(relative)
for relative in copied:copy(relative,canonical)
delivered={relative:sha(ROOT/relative) for relative in public}
for relative,digest in delivered.items():
    assert sha(canonical/relative)==digest and sha(preview/relative)==digest,relative
for relative,digest in protected_hashes.items():assert sha(canonical/relative)==digest,relative
checkpoint={'classification':'Accepted geometry checkpoint; inherited finish remains unfinished','accepted_checkpoint':a.checkpoint,
    'accepted_model_sha256':model_hash,'accepted_render_sha256':scores['render_sha256'],
    'accepted_atlas_sha256':scores['atlas_sha256'],'public_stage_canonical_preview_identical_files':delivered,
    'canonical_protected_file_hashes':protected_hashes,'all_saved_model_checks_passed':True,
    'viewer_and_review_checks_passed':True,'native_browser_inspection':False,'source_camera_degrees':54,
    'scores_percent':scores['scores_percent'],'mean_percent':scores['mean_percent'],
    'geometry_phase_complete':False,'mission_complete':False,'goal_status':'active','no_quota_monitoring':True,'no_push':True,
    'note':'Only bishop files copied. Neutral is the review default. The old material/lights are retained without hiding their mismatch. Other pieces and shared gallery settings are untouched.'}
relative=f'docs/bishop-mission/iteration-{a.checkpoint}/checkpoint.json'
if (out/'side-refit.json').is_file():
    fit=json.loads((out/'side-refit.json').read_text())
    measured=json.loads((out/'measurements.json').read_text())
    row=measured[fit['accepted']]
    checkpoint.update(side_refit_complete=True,goal_status='accepted regional refit',
        frozen_king_percent=measured['side_calibration']['target_bishop_percent_on_fixed_king_ruler'],
        screenshot_side_iou=row['side_fit']['outline_iou'],registered_original_iou=row['registered']['original_white'],
        note='Owner-directed physical sizing on the 025 ruler. The unchanged 54-degree view records the reference-fit cost. Material and lighting work remains open.')
    if 'locked_height' in fit:
        checkpoint.update(goal_status='accepted fixed-height geometry checkpoint',
            locked_height_model_units=row['height'],foot_diameter_model_units=row['foot_diameter'],
            note='Same floor, measured height, 025 lineup ruler and 54-degree camera. Original-white contours, three collar arcs and the real slit are examined separately.')
(ROOT/relative).write_text(json.dumps(checkpoint,indent=2)+'\n',newline='\n');copy(relative,canonical)
manifest=sorted(set(list(public)+copied+[relative]))
(ROOT/f'build/bishop-mission/{a.log_prefix}-delivered-files.json').write_text(json.dumps({r:sha(ROOT/r) for r in manifest},indent=2)+'\n')
print(json.dumps({'synchronized':True,'public_files':len(public),'evidence_and_script_files':len(copied)+1,'model_sha256':model_hash},indent=2))

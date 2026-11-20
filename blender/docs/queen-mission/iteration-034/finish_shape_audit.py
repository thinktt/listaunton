"""Verify unchanged Queen delivery, sync the final audit, and run scoped checks.

Run inside Ubuntu-24.04 from the canonical repository. This does not render,
replace the model, create a commit, push, or change the goal state.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess

ROOT = Path('/home/toby/code/listaunton').resolve()
WORK = Path('/mnt/c/Users/toby/Documents/Codex/2026-10-01/go-x20')
STAGE = WORK / 'work/queen-241-viewer-stage'
PREVIEW = WORK / 'outputs/queen-hires'
EVIDENCE = Path('docs/queen-mission/iteration-034')
MODEL = '243844939937d0b753df253810f0e60d67b86a664f14b86dd678e7e22d348a68'
HEAD = '3980e37f32d6ae3943a5e5b3d5133e2ad49a286f'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def run(args):
    return subprocess.run(args, cwd=ROOT, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout

assert Path.cwd().resolve() == ROOT
assert run(['git', 'rev-parse', 'HEAD']).strip() == HEAD
assert not run(['git', 'status', '--porcelain']).strip(), 'Preserve other work'
original_modes = {}
for line in run(['git', 'ls-files', '--stage']).splitlines():
    meta, name = line.split('\t', 1)
    original_modes[name] = int(meta.split()[0], 8) & 0o777

hashes = read(ROOT / 'docs/queen-mission/iteration-033/source-hashes.json')
source_results = {}
for name, digest in hashes.items():
    assert sha(ROOT / name) == digest
    source_results[name] = digest

manifest = read(ROOT / 'docs/queen-mission/iteration-033/sync-manifest.json')
delivery_files = [name for name in manifest['files']
                  if name.startswith('assets/queen/') or
                  name in ['review.html', 'models/queen/queen-rebuilt.blend']]
delivery = {}
for name in delivery_files:
    triplet = {label: sha(folder / name) for label, folder in
               [('repository', ROOT), ('staging', STAGE), ('local_preview', PREVIEW)]}
    assert len(set(triplet.values())) == 1, (name, triplet)
    delivery[name] = triplet['repository']
assert delivery['models/queen/queen-rebuilt.blend'] == MODEL
assert MODEL in (ROOT / 'review.html').read_text()

report_specs = {
    'assets/queen/finish-validation.json': 'source_sha256',
    'assets/queen/model-validation.json': 'source_sha256',
    'assets/queen/viewer-camera-check.json': 'sourceSha256',
}
reports = {}
for name, key in report_specs.items():
    data = read(ROOT / name)
    assert data['passed'] and data[key] == MODEL
    reports[name] = {'passed': True, 'source_sha256': data[key], 'report_sha256': sha(ROOT / name)}
shape_name = str(EVIDENCE / 'current-side-shape-validation.json')
shape = read(STAGE / shape_name)
assert shape['passed'] and shape['model_sha256'] == MODEL
reports[shape_name] = {'passed': True, 'source_sha256': shape['model_sha256'],
                      'report_sha256': sha(STAGE / shape_name)}
side = read(ROOT / 'assets/queen/side-registration.json')
assert side['source_blend_sha256'] == MODEL
phase = read(STAGE / EVIDENCE / 'phase-audit/phase-measurements.json')
preservation = read(STAGE / EVIDENCE / 'phase-audit/profile-preservation.json')
assert phase['after']['sha256'] == MODEL and all(phase['preservation'].values())
assert preservation['passed'] and preservation['source_sha256'] == MODEL
assert preservation['all_packed_image_bytes_identical']
http = read(WORK / 'work/queen-socket-034/http-check.json')
assert http['review_status'] == http['side_status'] == 200
assert http['embedded_model_hash_matches'] and http['served_side_registration_matches']
assert http['source_sha256'] == MODEL

# Copy only the audit and supporting documentation/script. Current review,
# model, renders, reference files and other pieces are deliberately untouched.
relative_files = ['AGENTS.md', 'MISSION-QUEEN.md', 'docs/queen-mission-log.md',
                  'scripts/queen/audit_shape_phase.py']
relative_files += [str(p.relative_to(STAGE)) for p in (STAGE / EVIDENCE).rglob('*')
                   if p.is_file() and '__pycache__' not in p.parts]
for name in relative_files:
    destination = ROOT / name
    assert destination.resolve().is_relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(STAGE / name, destination)
    destination.chmod(original_modes.get(name, 0o644))

NODE = '/home/toby/.nvm/versions/node/v24.13.0/bin/node'
compile_files = ['scripts/queen/audit_shape_phase.py']
compile_files += [str(p.relative_to(ROOT)) for p in (ROOT / EVIDENCE).glob('*.py')]
commands = [
    ['python3', '-m', 'py_compile', *compile_files],
    ['python3', 'scripts/check_site.py'],
    ['python3', 'scripts/check_model_site.py'],
    [NODE, 'scripts/queen/check_viewer_camera.cjs'],
    [NODE, 'scripts/queen/check_review_reference.cjs'],
    ['git', 'diff', '--check'],
]
checks = []
for command in commands:
    output = run(command)
    checks.append({'command': command, 'passed': True, 'output': output.strip()})
    print('PASS', ' '.join(command[:3]), flush=True)

# The camera harness emits a fresh report under build, not into public assets.
fresh_camera = read(ROOT / 'build/queen/viewer-camera-check.json')
assert fresh_camera['passed'] and fresh_camera['sourceSha256'] == MODEL
for name, digest in delivery.items():
    assert sha(ROOT / name) == digest, 'Delivery changed while auditing: ' + name

old_checks = read(ROOT / 'docs/queen-mission/iteration-033/checks.json')
result = {
    'passed': True,
    'checked_at_utc': datetime.now(timezone.utc).isoformat(),
    'accepted_model_commit': HEAD,
    'accepted_model_sha256': MODEL,
    'model_and_public_review_unchanged_in_this_iteration': True,
    'repository_staging_preview_hashes_equal': delivery,
    'original_references_and_gallery_defaults': source_results,
    'current_model_reports': reports,
    'direct_phase_preservation': preservation,
    'current_http': http,
    'commands_run_this_iteration': checks,
    'current_camera_regression': fresh_camera,
    'native_review_inspection': {
        'performed_at': 'checkpoint 33; no new native review test in iteration 34',
        'valid_for_unchanged_review_sha256': delivery['review.html'],
        'observations': old_checks['native_browser'],
    },
    'native_study_inspection_this_iteration': ['German Knight queens', 'Chavet lineup'],
    'completion_scope': 'The four shape priorities in MISSION-QUEEN.md; see README requirement audit.',
    'shape_phase_visual_requirements_assessed_met': True,
    'full_visual_match_complete': False,
    'remaining': ['Socket and crown reflections', 'Grain and relief', 'Regional color',
                  'Unmatched white finish', 'Browser lighting approximation',
                  'Inferred unseen geometry and historical camera'],
    'rejected_trials': ['267-flatter-socket-seat-032', '268-flatter-socket-seat-050',
                        '269-flatter-socket-wood'],
    'no_push_or_publication': True,
    'no_watchers_or_subagents': True,
}
text = json.dumps(result, indent=2) + '\n'
for root in [ROOT, STAGE]:
    (root / EVIDENCE / 'completion-checks.json').write_text(text)
(ROOT / EVIDENCE / 'completion-checks.json').chmod(0o644)
shutil.copyfile(WORK / 'work/queen-socket-034/http-check.json', ROOT / EVIDENCE / 'http-check.json')
(ROOT / EVIDENCE / 'http-check.json').chmod(0o644)
run(['git', 'diff', '--check'])
print(json.dumps({'passed': True, 'model_sha256': MODEL,
                  'verified_delivery_files': len(delivery), 'synced_files': len(relative_files)}, indent=2))

"""Collect bishop iteration 008 while asserting checkpoint 007 is retained."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];build=ROOT/'build/bishop-mission';out=ROOT/'docs/bishop-mission/iteration-008'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected='46e8b302ab6340bfddebdc765cd14658eb1fb29185aedab683524e7c008d59d3'
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==expected
assert sha(ROOT/'history/bishop-mission-007/bishop-rebuilt.blend')==expected
prior=json.loads((ROOT/'docs/bishop-mission/iteration-007/checkpoint.json').read_text())
assert sha(ROOT/'assets/bishop/render.png')==prior['render_sha256']
assert sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png')==prior['texture_sha256']
for name,digest in prior['reference_hashes'].items():assert sha(ROOT/'assets/bishop'/name)==digest,name
subprocess.run([sys.executable,str(ROOT/'scripts/bishop/collect_pigment_research.py'),'--out','docs/bishop-mission/iteration-008/material-research'],check=True)
records=[]
for name,lighting,reason in [
 ('063-cream-lower-reflections',73,'Hue improves but misplaced glints become more conspicuous.'),
 ('064-aligned-base-reflection',73,'Reflection remains too tall/high after physical placement.'),
 ('065-shaped-base-reflection',68,'Overshoot creates a foot flash and spill.'),
 ('066-intermediate-base-reflection',71,'Foot flash reduced, but the main reference glint is missing.')]:
    src=build/name;dest=out/'lighting-research'/name;dest.mkdir(parents=True,exist_ok=True)
    metrics=json.loads((src/'comparison/metrics.json').read_text());scores={'silhouette':metrics['images']['selected']['silhouette_iou']*100,'interior':83,'color':85,'texture':77,'lighting':lighting}
    record={'trial':name,'decision':'rejected','reason':reason,'scores':scores,'mean':sum(scores.values())/5,
       'holistic_range_percent':[75,85],'metrics':metrics['images'],'model_sha256':sha(src/'bishop.blend'),'render_sha256':sha(src/'wood.png'),
       'samples':96,'adaptive_sampling':False,'source_model_sha256':expected}
    for path in ['parameters.json','statistics.json','comparison/metrics.json','comparison/base.png','comparison/head.png','comparison/stem-socket.png','light-scope.json']:
        if (src/path).exists():shutil.copy2(src/path,dest/Path(path).name)
    shutil.copy2(ROOT/f'scripts/bishop/lighting-{name[:3]}.json',dest/'lighting-config.json')
    (dest/'assessment.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
for src in ['lower-glint-points.json','lower-glint-landmarks.json','lower-glint-points-065.json','lower-glint-landmarks-065.json','lower-glint-grid.png','prepare-065.py','prepare-066.py','inspect-lower-glints.py']:
    shutil.copy2(build/src,out/src)
shutil.copy2(build/'lower-shading-normals/manifest.json',out/'lower-shading-normals.json')
scope=json.loads((build/'066-intermediate-base-reflection/light-scope.json').read_text());assert scope['passed']
assert scope['only_declared_existing_light_properties_changed'] and scope['source_sha256']==expected
shutil.copy2(build/'066-intermediate-base-reflection/light-scope.json',out/'light-scope.json')
shutil.copy2(build/'material-trials-058-062.json',out/'material-statistics.json')
(out/'lighting-research/manifest.json').write_text(json.dumps({'trials':records,'all_rejected':True},indent=2)+'\n')
current_scores=json.loads((ROOT/'docs/bishop-mission/iteration-007/scores.json').read_text())
current_scores['status']='Checkpoint 007 retained; iteration 008 contains rejected experiments only.'
(out/'scores.json').write_text(json.dumps(current_scores,indent=2)+'\n')
checkpoint={'date':'2026-11-05','starting_commit':'9b87e11','accepted_model_changed':False,'status':'research checkpoint; all model trials rejected',
 'retained_model_sha256':expected,'retained_render_sha256':prior['render_sha256'],'retained_texture_sha256':prior['texture_sha256'],
 'reference_hashes':prior['reference_hashes'],'references_unchanged':True,'source_camera_degrees':54,
 'reopened_existing_light_patch_audit_passed':True,'trial_066_scope':scope,
 'canonical_and_preview_preservation':'Pending byte comparison before commit; do not interpret as a completed site check.',
 'ui_changes':False,'native_browser_inspection':False,'mission_complete':False}
(out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
print(json.dumps({'status':'research evidence collected','model_retained':expected,'model_trials_rejected':9},indent=2))

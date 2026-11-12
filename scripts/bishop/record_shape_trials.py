"""Preserve the rendered geometry studies, explicit decisions and reproduction."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'docs/bishop-mission/iteration-017'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
studies=[
 ('135-lower-shoulder-fit',[84,85,78,75],'Reject: the first radial scope leaves the upper shoulder too broad.'),
 ('136-shoulder-height-fit',[85,83,77,73],'Reject: better outline but too angular a side profile.'),
 ('137-upper-collar-underside',[83,82,76,71],'Reject: actual collar rim moved into the photographic shadow; shadow location is not the rim.'),
 ('138-stem-taper-fit',[81,80,75,70],'Reject: unconstrained stem fit bulges near the socket and retains earlier problems.'),
 ('139-constrained-stem-fit',[84,82,76,71],'Reject as a complete model: constrained stem is better, but base and collar corrections remain too strong.'),
 ('142-rounded-shape-refinement',[86,83,77,72],'Accept geometry for final render: radius-only rounded base, half stem and collar corrections.'),
 ('143-geometry-checkpoint',[86,83,77,72],'Accept: same geometry as 142, saved/reopened final 512-sample render and current-model validation.')]
records=[];overview=Image.new('RGB',(900,340*len(studies)),'#14181c');draw=ImageDraw.Draw(overview)
for row,(name,judgments,decision) in enumerate(studies):
    trial=ROOT/'build/bishop-mission'/name
    comparison=trial/'comparison'
    if not (comparison/'metrics.json').exists():
        subprocess.run([sys.executable,str(ROOT/'scripts/bishop/mission_compare.py'),'--render',str((trial/'wood.png').relative_to(ROOT)),
            '--out',str(comparison.relative_to(ROOT))],check=True,stdout=subprocess.DEVNULL)
    metrics=json.loads((comparison/'metrics.json').read_text())
    assert metrics['render_sha256']==sha(trial/'wood.png')
    audit=json.loads((trial/'trial-audit.json').read_text())
    saved=out/'trials'/name;saved.mkdir(parents=True,exist_ok=True)
    (saved/'config.json').write_text(json.dumps(audit['config'],indent=2)+'\n')
    shutil.copy2(comparison/'metrics.json',saved/'metrics.json')
    scores=dict(zip(['silhouette','interior','color','texture','lighting'],[100*metrics['images']['selected']['silhouette_iou']]+judgments))
    records.append({'variant':name,'model_sha256':sha(trial/'bishop.blend'),'render_sha256':sha(trial/'wood.png'),
        'config':'trials/'+name+'/config.json','scores_percent':scores,'mean_percent':sum(scores.values())/5,
        'decision':decision,'subjective_ratings_are_retrospective_comparisons':True,
        'reopened_scope_check_passed':audit['saved_and_reopened'],'silhouette_masks':metrics['mask']})
    for col,key in enumerate(['reference','wood','neutral']):
        path=ROOT/'assets/bishop/reference.png' if key=='reference' else trial/(key+'.png')
        im=Image.open(path).convert('RGBA').resize((300,300),Image.Resampling.LANCZOS)
        overview.paste(im,(col*300,row*340+35),im)
        draw.text((col*300+5,row*340+10),('Selected white 3' if col==0 else name+' '+key),fill='white')
overview.save(out/'trial-overview.png')
(out/'trials.json').write_text(json.dumps({'phase':'geometry','ratings_note':'Silhouette is measured; the other four scores are subjective visual estimates, with no reward for better overlap alone.',
    'unrendered_proposals_not_scored':['141 radius-only optimizer proposal'], 'trials':records},indent=2)+'\n')
source=ROOT/'history/bishop-mission-015/bishop-rebuilt.blend';config=out/'profile-fit.json'
repro={'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'config':str(config.relative_to(ROOT)),
    'config_sha256':sha(config),'environment':'Blender 5.2.2, Cycles/OPTIX; Python with NumPy and Pillow. Use an isolated checkout.',
    'commands':['blender --background --python-exit-code 1 --python scripts/bishop/profile_shape_trial.py -- docs/bishop-mission/iteration-017/profile-fit.json',
        'blender --background --python-exit-code 1 --python scripts/bishop/validate_profile_shape.py -- --model build/bishop-mission/143-geometry-checkpoint/bishop.blend --config docs/bishop-mission/iteration-017/profile-fit.json --profile build/bishop-mission/143-geometry-checkpoint/profile.json --out build/bishop-mission/143-independent-scope.json'],
    'promotion':'After visual acceptance, copy trial bishop.blend to models/bishop/bishop-rebuilt.blend, profile.json to scripts/bishop/profile.json, wood.png to assets/bishop/render.png, and neutral.png to assets/bishop/render-clay.png. Keep the atlas exact.',
    'refresh':['blender --background --python-exit-code 1 --python scripts/bishop/validate_checkpoint.py',
        'blender --background --python-exit-code 1 --python scripts/bishop/render_diagnostics.py',
        'python scripts/bishop/compare.py','python scripts/bishop/mission_compare.py --render assets/bishop/render.png --previous history/bishop-mission-015/render.png --out docs/bishop-mission/iteration-017/comparison',
        'python scripts/bishop/refresh_review.py','node scripts/bishop/check_viewer.cjs','node scripts/bishop/check_review.cjs'],
    'preservation':'No reference, alignment, gallery, mission, camera, material, light, UV control, button or slit cutter change. Other pieces untouched.',
    'limitations':'Fixed GPU renders can have noise/platform variation. Geometry and source hashes, exact config, scope and anatomy checks govern reproducibility; Blender container bytes need not repeat.'}
(out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
print(json.dumps({'recorded_trials':len(records),'configs_preserved':True},indent=2))

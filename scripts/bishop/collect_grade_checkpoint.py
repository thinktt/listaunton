"""Collect the checked bishop color checkpoint and its rejected continuity studies."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];build=ROOT/'build/bishop-mission';out=ROOT/'docs/bishop-mission/iteration-013'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline='89ff709b7cb2bd3f931ee6acd083e0cb8f993e86d424c9784ec2006830b3b231'
assert sha(ROOT/'history/bishop-mission-012/bishop-rebuilt.blend')==baseline
final=build/'106-final';reopen=json.loads((final/'reopen-validation.json').read_text())
assert reopen['samples']==512 and not reopen['adaptive_sampling'] and reopen['camera_preserved']
assert sha(ROOT/'models/bishop/bishop-rebuilt.blend')==reopen['saved_model_sha256']
assert sha(ROOT/'assets/bishop/render.png')==reopen['render_sha256']
assert sha(ROOT/'assets/bishop/bishop-boxwood-albedo.png')==reopen['texture_sha256']
for name in ['mission-validation.json','receiver-validation.json','pigment-validation.json']:
    report=json.loads((ROOT/'assets/bishop'/name).read_text());assert report['passed']
    assert report['model_sha256']==reopen['saved_model_sha256']

def copy(src,dest):
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)

trials=[]
specs=[
 ('100-coherent-pigment',[84,68,68,67],'Removing broad pigment variation loses the fixed-view color and contrast; the retained high-pass carries false tonal bands.'),
 ('102-fitted-continuous-wood',[84,73,69,70],'Measured global diffuse lights improve the flat-pigment control but cannot restore regional color and contrast. Actual render confirms the rejection.'),
 ('103-continuous-wood-pore-relief',[84,73,69,70],'Removing pigment from relief barely changes fixed-view error. Rear color is more continuous but the reference view stays too flat and plastic.'),
 ('104-measured-hidden-continuation',[84,84,77,77],'Protecting measured visible texels preserves the front but leaves the conspicuous side/rear patch essentially unchanged; tiny error movement is not a visual improvement.'),
 ('105-bounded-regional-boxwood-grade',[84,84,77,77],'Socket, stem and collar color improve, but foot error increases and base error does not improve; reject the broad grade.'),
 ('106-middle-body-boxwood-grade',[84,85,77,77],'Restrict the grade to socket, stem and collars. Keep protected foot, lower-base, head and button atlas pixels exact. Accepted only after the full saved-file checks.')]
for name,scores,reason in specs:
    folder=build/name;target=out/'studies'/name
    metrics=json.loads((folder/'comparison/metrics.json').read_text())
    values=dict(zip(['interior','color','texture','lighting'],scores));values={'silhouette':metrics['images']['selected']['silhouette_iou']*100,**values}
    trial={'trial':name,'decision':'accepted after finalization' if name.startswith('106') else 'rejected',
      'reason':reason,'scores_percent':values,'mean_percent':sum(values.values())/5,
      'holistic_range_percent':[65,75] if name[:3] in ['100','102','103'] else [75,85],
      'silhouette_measured_other_scores_visual_estimates':True,'model_sha256':sha(folder/'bishop.blend'),
      'render_sha256':sha(folder/'wood.png'),'fixed_camera_degrees':54,'samples':128,
      'source_geometry_unchanged':True,'metrics':metrics['images']}
    for name2 in ['wood.png','pigment.json','extension.json','fit.json','prediction.png','prediction-check.json',
       'trial-validation.json','parameters.json','atlas-scope.json','diffuse-scope.json','material-scope.json',
       'statistics.json','head-side.png','side-profile.png','rear-oblique.png','diagnostic-cameras.json','atlas-comparison.png']:
        if (folder/name2).exists():copy(folder/name2,target/name2)
    copy(folder/'comparison/metrics.json',target/'metrics.json')
    (target/'assessment.json').write_text(json.dumps(trial,indent=2)+'\n');trials.append(trial)
for name in ['manifest.json','visibility.json','visibility-atlas.png']:
    copy(build/'099-atlas-surface'/name,out/'surface-study'/name)
copy(build/'101-diffuse-basis/manifest.json',out/'surface-study/diffuse-basis.json')
copy(final/'reopen-validation.json',out/'reopen-validation.json')
copy(final/'statistics.json',out/'rgb-statistics.json')
for p in (final/'comparison').iterdir():
    if p.is_file():copy(p,out/'comparison'/p.name)
for name in ['render-clay.png','head-side.png','side-profile.png','rear-oblique.png','diagnostic-cameras.json']:
    copy(ROOT/'assets/bishop'/name,out/'views'/name)
for name in ['validation.json','mission-validation.json','receiver-validation.json','pigment-validation.json','base-validation.json','slit-validation.json','join-regression.json']:
    copy(ROOT/'assets/bishop'/name,out/'validation'/name)
for name in ['102-validation.log','102-validation-corrected.log','102-validation-final.log']:
    copy(build/name,out/'validation'/name)
metrics=json.loads((final/'comparison/metrics.json').read_text())
scores={'silhouette':metrics['images']['selected']['silhouette_iou']*100,'interior':84,'color':85,'texture':77,'lighting':77}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
 'original_white_iou':metrics['images']['original_white']['silhouette_iou'],
 'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
 'silhouette_is_measured_other_scores_are_visual_estimates':True,'starting_model_sha256':baseline,
 'accepted_model_sha256':reopen['saved_model_sha256'],'render_sha256':reopen['render_sha256'],
 'texture_sha256':reopen['texture_sha256'],'status':'Accepted local middle-body wood color improvement; full reconstruction remains incomplete.'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
(out/'trials.json').write_text(json.dumps(trials,indent=2)+'\n')
print('BISHOP_GRADE_CHECKPOINT_COLLECTED',json.dumps(record),flush=True)

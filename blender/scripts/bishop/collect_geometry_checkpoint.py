"""Record the second bishop checkpoint; refuse to rewrite it from a later model."""
from pathlib import Path
import hashlib
import json
import shutil

root=Path(__file__).resolve().parents[2]
out=root/'docs/bishop-mission/iteration-002'
expected='cb3a77ba94cd336e015ce4f21493ade912ad3061727817be703efdd0581bbee6'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(root/'models/bishop/bishop-rebuilt.blend')==expected
metrics=json.loads((out/'metrics.json').read_text())
assert metrics['render_sha256']==sha(root/'assets/bishop/render.png')
scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'], 'interior':81, 'color':70, 'texture':64, 'lighting':54}
record={
    'scores_percent':scores, 'mean_percent':sum(scores.values())/5,
    'holistic_range_percent':[65,75],
    'original_white_iou':metrics['images']['original_white']['silhouette_iou'],
    'original_black_iou':metrics['images']['original_black']['silhouette_iou'],
    'silhouette_is_measured_other_scores_are_visual_estimates':True,
    'accepted_model_sha256':expected,
    'render_sha256':metrics['render_sha256'],
    'texture_sha256':sha(root/'assets/bishop/bishop-boxwood-albedo.png'),
    'starting_model_sha256':sha(root/'history/bishop-mission-001/bishop-rebuilt.blend'),
    'status':'accepted geometry improvement, mission incomplete'
}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
for name in ['validation.json','mission-validation.json','join-regression.json','diagnostic-cameras.json','qa.json']:
    shutil.copy2(root/'assets/bishop'/name,out/name)
shutil.copy2(root/'build/bishop-mission/015-baked-geometry/bake-validation.json',out/'bake-validation.json')
for name in ['geometry-012.json','geometry-013.json','mission-014.json']:
    shutil.copy2(root/'scripts/bishop'/name,out/name)
trials=[]
for name in ['012-wider-button','013-flatter-foot','015-baked-geometry']:
    data=json.loads((root/'build/bishop-mission'/name/'comparison/metrics.json').read_text())
    trials.append({'trial':name,'metrics':data,'decision':'Button-only improvement' if name.startswith('012') else 'Foot and button improvement' if name.startswith('013') else 'Accepted after pigment reprojection, bake and saved-scene render'})
(out/'trials.json').write_text(json.dumps(trials,indent=2)+'\n')
repro={
    'geometry_config':'docs/bishop-mission/iteration-002/geometry-013.json',
    'material_config':'docs/bishop-mission/iteration-002/mission-014.json',
    'commands':[
        'blender --background --python-exit-code 1 --python scripts/bishop/geometry_trial.py -- docs/bishop-mission/iteration-002/geometry-013.json --no-render',
        'blender --background --python-exit-code 1 --python scripts/bishop/mission_material.py -- docs/bishop-mission/iteration-002/mission-014.json --no-render',
        'blender --background --python-exit-code 1 --python scripts/bishop/bake_mission.py -- --source build/bishop-mission/014-reprojected-geometry/bishop.blend --out build/bishop-mission/015-baked-geometry'
    ],
    'note':'Bake writes the bishop atlas; reproduce in an isolated checkout before replacing accepted assets. References and the saved 54-degree camera remain unchanged.'
}
(out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
print(json.dumps(record,indent=2))

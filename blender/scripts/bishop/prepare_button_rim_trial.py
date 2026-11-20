"""Preserve 019 and test a shallower button rim with direct head contact."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--lift',type=float,default=1.8);a=p.parse_args()
assert 0<a.lift<=2.25
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
archive=ROOT/'history/bishop-mission-019';archive.mkdir(exist_ok=True)
for relative,name in [('models/bishop/bishop-rebuilt.blend','bishop-rebuilt.blend'),
                      ('scripts/bishop/profile.json','profile.json')]+[
                      ('assets/bishop/'+name,name) for name in ['render.png','render-clay.png','side-profile.png',
                      'head-side.png','rear-oblique.png','camera.json','mesh.json','mesh.bin','bishop-boxwood-albedo.png']]:
    src=ROOT/relative;dest=archive/name
    if dest.exists():assert sha(src)==sha(dest),name
    else:shutil.copy2(src,dest)
profile=json.loads((archive/'profile.json').read_text())
out=ROOT/'build/bishop-mission/154-button-audit';out.mkdir(exist_ok=True)
weights={0:.4,1:.4,2:.55,3:1,4:1,5:.75,6:.4,7:.15}
finial={str(i):[profile['finial']['profile'][i][0],profile['finial']['profile'][i][1]-a.lift*w] for i,w in weights.items()}
cap=55.0
weights_head={101:.03,102:.1,103:.25,104:.55,105:1,106:1}
delta=profile['head_button_join']['head_cap_axis_y']-cap
body={str(i):[profile['profile'][i][0],profile['profile'][i][1]-delta*w] for i,w in weights_head.items()}
label=str(a.lift).replace('.','p')
cfg={'variant':'155-button-rim-'+label,'source':'history/bishop-mission-019/bishop-rebuilt.blend',
     'source_sha256':sha(archive/'bishop-rebuilt.blend'),'profile':'history/bishop-mission-019/profile.json',
     'samples':64,'body_rings':body,'finial_rings':finial,'head_cap_axis_y':cap,
     'interpretation':'Unaccepted button-rim hypothesis from first-hit surface boundaries. Raise and soften the front/outer roll while preserving every radius and the physical highest point. Extend only the concealed head tip for direct broad contact. Keep all lower anatomy, slit, UVs, pigment, lights and fixed reference camera unchanged.',
     'rim_lift_original_axis_units':a.lift,
     'observations':{'baseline_first_hit_button_bounds':[425,162,558,278],
                     'selected_front_rim_center_y_estimate':270,'estimated_uncertainty_px':3,
                     'note':'The lower photographic boundary is manually interpreted, supported by the blurred original; not an exact segmentation or a fit to highlights.'}}
(out/('rim-'+label+'.json')).write_text(json.dumps(cfg,indent=2)+'\n')
print('Prepared',cfg['variant'])

"""Correct the rejected rim trial's cup underside with a shallow seated lens."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--start',type=float,default=0);a=p.parse_args()
assert 0<=a.start<=.6
archive=ROOT/'history/bishop-mission-019';profile=json.loads((archive/'profile.json').read_text())
cap=52.5;delta=profile['head_button_join']['head_cap_axis_y']-cap
# Extend the head's original Bezier endpoint smoothly. t^3 is the endpoint
# basis, so the lower end and its tangent remain unchanged. Radii are fixed.
body={}
for i in range(66,106):
    t=(i-65)/40;radius,y=profile['profile'][i]
    weight=(max(0,t-a.start)/(1-a.start))**3
    if weight:body[str(i)]=[radius,y-delta*weight]
body['106']=[profile['profile'][106][0],cap]
body['105'][1]=cap
heights=[53.7,53.7,53.65,53.45,53.05,52.3,51.98,51.33]
finial={str(i):[profile['finial']['profile'][i][0],height] for i,height in enumerate(heights)}
cfg={'variant':'156-button-lens' if a.start==0 else '157-button-lens-local','source':'history/bishop-mission-019/bishop-rebuilt.blend',
     'source_sha256':hashlib.sha256((archive/'bishop-rebuilt.blend').read_bytes()).hexdigest(),
     'profile':'history/bishop-mission-019/profile.json','samples':64,
     'body_rings':body,'finial_rings':finial,'head_cap_axis_y':cap,
     'interpretation':'Unaccepted shallow button-lens trial. Keep the fitted front rim while flattening the cup-like underside. Extend the continuous head endpoint smoothly inside the lens for broad direct contact. All radial controls, lower 66 body rings, physical highest point, slit cutter, source registration, UVs, pigment, lights and fixed camera are preserved.',
     'head_tip_extension_basis':'delta_axis_y * (max(0,t-start)/(1-start))^3; C2 at the start of the edit',
     'head_tip_extension_start_fraction':a.start}
name='lens.json' if a.start==0 else 'lens-local.json'
(ROOT/'build/bishop-mission/154-button-audit'/name).write_text(json.dumps(cfg,indent=2)+'\n')
print('Prepared shallow button lens with concealed continuous head tip.')

"""Place one existing base reflector from measured surface/shading normals."""
import argparse,json,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--landmarks',required=True);p.add_argument('--normals',required=True);p.add_argument('--out',required=True)
p.add_argument('--variant',default='064-aligned-base-reflection')
a=p.parse_args();geometry=json.loads((ROOT/a.landmarks).read_text());normals=json.loads((ROOT/a.normals).read_text())
assert geometry['_provenance']['source_sha256']==normals['source_sha256']
name='base peak';assert geometry[name]['pixel']==normals['points'][name]['pixel']
n=np.array(normals['points'][name]['normal']);n/=np.linalg.norm(n)
view=np.array(json.loads((ROOT/'assets/bishop/camera.json').read_text())['worldToCamera']).reshape(4,4)[2,:3];view/=np.linalg.norm(view)
point=np.array(geometry[name]['surface']);direction=2*np.dot(n,view)*n-view
cfg={'source':normals['source'],'variant':a.variant,'samples':96,'adaptive_sampling':False,
 'hypothesis':'Move the existing base reflection to the measured reference highlight center and reduce its yellow tint. Preserve its original energy, shape, spread and receiver, all other lights, texture, geometry and 54-degree camera.',
 'lights':[{'name':'base reflection','position':(point+7*direction).tolist(),'target':point.tolist(),'color':[1,.92,.65]}],
 'measurement':{'landmarks':a.landmarks,'normals':a.normals,'target_pixel':geometry[name]['pixel'],'mean_radius':normals['points'][name].get('mean_radius',0),
 'normal_difference_degrees':float(np.degrees(np.arccos(np.clip(np.dot(n,geometry[name]['normal']),-1,1))))}}
out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(cfg,indent=2)+'\n');print(json.dumps(cfg,indent=2))

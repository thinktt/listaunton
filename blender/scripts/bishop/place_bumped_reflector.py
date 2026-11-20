"""Use a measured BSDF normal to place an isolated slit-tip reflector."""
from pathlib import Path
import argparse,json,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--normals',required=True);p.add_argument('--landmarks',required=True);p.add_argument('--config',required=True);p.add_argument('--out',required=True)
a=p.parse_args();actual=json.loads((ROOT/a.normals).read_text());geometry=json.loads((ROOT/a.landmarks).read_text());cfg=json.loads((ROOT/a.config).read_text())
assert actual['source_sha256']==geometry['_provenance']['source_sha256']
name='tip peak';assert actual['points'][name]['pixel']==geometry[name]['pixel'] and actual['points'][name]['alpha']>.999
normal=np.array(actual['points'][name]['normal']);normal/=np.linalg.norm(normal)
view=np.array(json.loads((ROOT/'assets/bishop/camera.json').read_text())['worldToCamera']).reshape(4,4)[2,:3];view/=np.linalg.norm(view)
point=np.array(geometry[name]['surface']);direction=2*np.dot(normal,view)*normal-view
cfg['lights'][0]['position']=(point+7*direction).tolist();cfg['lights'][0]['target']=point.tolist();cfg['variant']='047-bumped-tip-reflection'
cfg['normal_measurement']={'manifest':a.normals,'pixel':geometry[name]['pixel'],'normal':normal.tolist(),
 'geometric_normal':geometry[name]['normal'],'difference_degrees':float(np.degrees(np.arccos(np.clip(np.dot(normal,geometry[name]['normal']),-1,1))))}
(ROOT/a.out).write_text(json.dumps(cfg,indent=2)+'\n');print(json.dumps(cfg,indent=2))

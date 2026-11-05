from pathlib import Path
import json,numpy as np
root=Path(__file__).resolve().parents[2]
g=json.loads((root/'build/bishop-mission/lower-glint-landmarks-065.json').read_text())
npy=np.load(root/'build/bishop-mission/lower-shading-normals/normals.npy');n=npy[1012:1019,587:594].mean((0,1));n/=np.linalg.norm(n)
view=np.array(json.loads((root/'assets/bishop/camera.json').read_text())['worldToCamera']).reshape(4,4)[2,:3];view/=np.linalg.norm(view)
point=np.array(g['base peak']['surface']);direction=2*np.dot(n,view)*n-view
cfg=json.loads((root/'scripts/bishop/lighting-064.json').read_text())
cfg['variant']='065-shaped-base-reflection'
cfg['lights'][0].update(position=(point+7*direction).tolist(),target=point.tolist(),shape='ELLIPSE',size=1.5,size_y=.35,energy=6.091302*1.5*.35/(.9*.9))
cfg['measurement']={'landmarks':'build/bishop-mission/lower-glint-landmarks-065.json','normal_capture':'build/bishop-mission/lower-shading-normals/normals.npy','pixel':[590,1015],'normal':n.tolist(),'mean_radius':3}
cfg['hypothesis']='The first physically placed light still creates an overly tall reflection above the reference center. Aim farther down the surface and flatten the emitter to broaden the glint laterally. Normalize power by area to retain approximate emitter radiance; validate in the actual render. Geometry, material, all other lights and camera stay fixed.'
(root/'scripts/bishop/lighting-065.json').write_text(json.dumps(cfg,indent=2)+'\n')

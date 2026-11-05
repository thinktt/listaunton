from pathlib import Path
import json,numpy as np
root=Path(__file__).resolve().parents[2]
first=json.loads((root/'scripts/bishop/lighting-064.json').read_text());second=json.loads((root/'scripts/bishop/lighting-065.json').read_text())
a=first['lights'][0];b=second['lights'][0];t=.4
target=(1-t)*np.array(a['target'])+t*np.array(b['target'])
position=(1-t)*np.array(a['position'])+t*np.array(b['position'])
direction=position-target;direction/=np.linalg.norm(direction)
second['variant']='066-intermediate-base-reflection';second['lights'][0].update(position=(target+7*direction).tolist(),target=target.tolist())
second['hypothesis']='The measured placement leaves the broad highlight too high; the lower flattened-emitter trial overshoots onto the foot. Interpolate its direction 40 percent toward the lower trial, retaining the flatter emitter and power, to test a centered glint without the foot flash. All other scene properties remain at accepted 007.'
second['measurement']={'upper_config':'scripts/bishop/lighting-064.json','lower_config':'scripts/bishop/lighting-065.json','lower_direction_fraction':t,'source_distance':7}
(root/'scripts/bishop/lighting-066.json').write_text(json.dumps(second,indent=2)+'\n')

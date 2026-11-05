"""Rank actual cached black-BSDF light contributions in the unwanted glint."""
from pathlib import Path
import json
import numpy as np
ROOT=Path(__file__).resolve().parents[2];basis=ROOT/'build/queen-mission/specular-expanded-039'
manifest=json.loads((basis/'manifest.json').read_text());specs={s['name']:s for s in manifest['specs']}
cfg=json.loads((ROOT/'docs/queen-mission/iteration-005/reproduction.json').read_text())['material_config']
regions={'unwanted_finial_tail':(165,72,170,79),'all_finial':(143,50,180,88),'base_reflection':(175,282,210,325)}
records={name:[] for name in regions}
for light in cfg['lights']:
 if not light['name'].startswith('Display fitted '):continue
 name=light['name'].removeprefix('Display fitted ');spec=specs[name]
 a=np.load(basis/(name+'.npy'))[:,:,:3]*(light['energy']/spec['energy'])*np.array(light.get('color',[1,1,1]))
 for region,(x0,y0,x1,y1) in regions.items():
  c=a[y0:y1,x0:x1];records[region].append({'light':name,'linear_rgb_sum':float(c.sum()),'peak':float(c.max())})
for values in records.values():values.sort(key=lambda v:-v['linear_rgb_sum'])
out=ROOT/'build/queen-mission/light-spill-005.json';out.write_text(json.dumps({'regions_at_418':regions,'source_manifest':manifest['source'],'caveat':'Cached response geometry, black BSDF and relief match the accepted material; color is excluded. A diagnostic ranking, not a new render or visual score.','rankings':records},indent=2)+'\n')
print(json.dumps({name:values[:8] for name,values in records.items()},indent=2))

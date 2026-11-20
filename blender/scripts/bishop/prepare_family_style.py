"""Apply the king/queen's turning style to the restored tall bishop."""
from pathlib import Path
import argparse,json,math
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/bishop-mission/iteration-030'
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--variant',choices=['a','b'],default='b')
args=p.parse_args()
d=json.loads((DOC/'style-sources.json').read_text())
pts=np.array(d['bishop']['control_rz']); old=pts.copy()
changes={
 8:(.9970,.295),9:(.980,.322),10:(.972,.350),11:(.977,.370),
 12:(.986,.398),13:(.990,.435),14:(.9828,.490),15:(.966,.543),
 16:(.940,.593),17:(.905,.647),18:(.836,.732),19:(.758,.823),
 20:(.684,.895),21:(.621,.940),22:(.562,.980),23:(.534,1.024),
 24:(.524,1.1175),25:(.520,1.1742),26:(.514,1.245),
 27:(.505,1.291),28:(.491,1.330),29:(.469,1.362),
 30:(.446,1.389),31:(.423,1.423),32:(.403,1.482),
 40:(.3834,2.745),41:(.5168,2.770),42:(.6002,2.797),
 43:(.643,2.820),44:(.659,2.844),45:(.658,2.870),
 46:(.641,2.901),47:(.610,2.924),48:(.575,2.936),49:(.546,2.941),
 50:(.544,2.967),51:(.574,3.002),52:(.599,3.023),53:(.603,3.045),
 54:(.592,3.067),55:(.565,3.084),56:(.537,3.098),57:(.501,3.121),
 58:(.4668,3.165),59:(.4585,3.225),60:(.4751,3.265),
 61:(.5085,3.278),62:(.524,3.293),63:(.519,3.312),
 64:(.5001,3.331),65:(.4751,3.346)
}
if args.variant=='b':
    changes.update({
      44:(.658,2.839),45:(.661,2.871),46:(.651,2.903),
      47:(.625,2.929),48:(.582,2.949),49:(.546,2.957),50:(.544,2.980),
      53:(.604,3.044),54:(.603,3.066),55:(.582,3.090),56:(.544,3.111),
      63:(.526,3.316),64:(.510,3.342),65:(.477,3.367)
    })
for i,rz in changes.items():pts[i]=rz
profile=json.loads((ROOT/'history/bishop-mission-024/profile.json').read_text())
al=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text())
f=1254/300/al['scale']/profile['scale'];c=math.cos(math.radians(54))
cfg={'variant':'186-family-style-'+args.variant,'source':'history/bishop-mission-024/bishop-rebuilt.blend',
     'source_sha256':d['bishop']['sha256'],'profile':'history/bishop-mission-024/profile.json',
     'samples':128 if args.variant=='b' else 64,'body_rings':{
         str(i):[round(float(pts[i,0]/f),7),round(float(profile['profile'][i][1]-(pts[i,1]-old[i,1])*c/f),7)]
         for i in changes},
     'intent':'Shape only: king/queen-style rolled base, curved socket-to-stem transition and thin stacked collar rims. Original tall height, camera, upper stem, head, button, material and lights retained.'}
(DOC/'family-style.json').write_text(json.dumps(cfg,indent=2)+'\n')
(DOC/'proposal-native.json').write_text(json.dumps({'control_rz':pts.tolist(),'changed_rings':list(changes)},indent=2)+'\n')
print('Prepared',cfg['variant'])

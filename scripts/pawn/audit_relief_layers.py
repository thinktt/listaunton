from pathlib import Path
import json,sys
import numpy as np
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'scripts/pawn'))
from audit_mission import sheet,rgba
from derive_wood import blur
out=r/'build/pawn-mission/076-stem-relief-isolation';m=json.loads((out/'measurement.json').read_text())
ref=rgba(r/'assets/pawn/reference.png')
items=[('Selected black 2',ref)]+[(k,rgba(out/v['file'])) for k,v in m['renders'].items()]
sheet(items,(376,598,439,683),250,out/'comparison.png')
stats={};roi=np.s_[615:650,390:425]
for key,image in items:
    rgb=np.asarray(image)[:,:,:3].astype(float);target=np.asarray(ref)[:,:,:3].astype(float)
    lum=rgb@np.array([.24,.53,.23]);a=(lum-blur(lum,r=2,passes=2))[roi].ravel()
    if key=='Selected black 2':hp=a
    stats[key]={'mae':float(abs(rgb-target)[roi].mean()),'fine_correlation':float(np.corrcoef(a,hp)[0,1]),'luma_p99':float(np.quantile(lum[roi],.99))}
(out/'analysis.json').write_text(json.dumps(stats,indent=2)+'\n',encoding='utf8')
print(json.dumps(stats,indent=2))

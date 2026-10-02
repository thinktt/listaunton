"""Measure collar spacing from exported, subdivided geometry, not control points."""
from pathlib import Path
import json
import numpy as np

work=Path(__file__).resolve().parent
meta=json.loads((work/'viewer-mesh.json').read_text())
verts=np.fromfile(work/'viewer-mesh.bin',dtype='<f4',count=meta['vertexByteLength']//4).reshape(-1,6)
body=meta['parts'][0]
p=verts[body['vertexOffset']:body['vertexOffset']+body['vertexCount'],:3].astype(float)
p=p[(np.abs(p[:,0])<1e-7)&(p[:,1]<0)]
zr=np.unique(np.round(np.column_stack((p[:,2],-p[:,1])),9),axis=0)
collars=[]
for name,low,high in [('lower',2.94,3.025),('middle',3.11,3.19),('upper',3.29,3.355)]:
    section=zr[(zr[:,0]>low)&(zr[:,0]<high)]
    peak=section[np.argmax(section[:,1])]
    closest=section[np.argsort(np.abs(section[:,0]-peak[0]))[:5]]
    origin=peak[0]
    coeff=np.polyfit(closest[:,0]-origin,closest[:,1],2)
    z=origin-coeff[1]/(2*coeff[0])
    assert coeff[0]<0 and low<z<high
    collars.append({'name':name,'evaluated_peak_z':float(z),
                    'evaluated_peak_radius':float(np.polyval(coeff,z-origin))})
gaps=np.diff([c['evaluated_peak_z'] for c in collars])
assert np.all(gaps>0) and abs(gaps[0]-gaps[1])<.005, gaps
taper=zr[(zr[:,0]>3.42)&(zr[:,0]<3.98)]
line=np.polyfit(taper[:,0],taper[:,1],1)
error=np.max(np.abs(taper[:,1]-np.polyval(line,taper[:,0])))
assert line[0]>0 and error<.002, (line,error)
report={'passed':True,'sourceSha256':meta['sourceSha256'],'collars':collars,
        'evaluated_peak_gaps':gaps.tolist(),'gap_difference':float(abs(gaps[0]-gaps[1])),
        'crown_body_taper_slope':float(line[0]),'max_taper_radius_deviation':float(error)}
(work/'even-collars-measurements.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

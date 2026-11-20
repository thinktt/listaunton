"""Single-turn flare proposals; retain all existing heights and upper geometry."""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import brentq
P=Path(__file__).resolve().parent
c=np.load(P/'controls-032.npy');r=np.linalg.norm(c[:,:,:2],axis=2).mean(1);z=c[:,:,2].mean(1)
source_sha='d58316454daad02fafaacbe7ff50215f042911cbd2e1609fbc8431f1c52ab0b4'
def bezier(points,t):
    return (1-t)**3*points[0]+3*(1-t)**2*t*points[1]+3*(1-t)*t*t*points[2]+t**3*points[3]
configs=[]
for tag,p1,p2,groove in [('263-continuous-flare-roll',1.031,1.059,0),('264-shallow-groove-roll',1.031,1.059,.006),('265-low-flare-roll',1.036,1.053,.006)]:
    rr=r.copy();zz=z.copy()
    # Fit a single continuous outer turn at the existing control heights.
    controls=np.array([[r[11]+groove,z[11]],[p1,.270],[p2,.365 if tag!='265-low-flare-roll' else .335],[r[22],z[22]]])
    for i in range(12,22):
        t=brentq(lambda t:bezier(controls,t)[1]-z[i],0,1)
        rr[i]=bezier(controls,t)[0]
    if groove:
        for i,w in [(9,.12),(10,.55),(11,1)]:rr[i]+=groove*w
    delta={str(i):float(rr[i]) for i in range(9,22) if abs(rr[i]-r[i])>1e-7}
    cfg={'variant':tag,'angle':54,'floor':860.223491056495,'source_sha256':source_sha,
        'scope':'Only radial controls 9-21; all heights, foot wall, socket and upper geometry exact.',
        'bezier_control_points':controls.tolist(),'groove_radial_fill':groove,
        'ring_radii':delta,'ring_z_offsets':{},
        'control_peak_radius':float(rr[11:23].max()),'control_peak_ring':int(np.argmax(rr[11:23]))+11}
    configs.append(cfg);(P/f'{tag}.json').write_text(json.dumps(cfg,indent=2)+'\n')
    print(tag,'peak',cfg['control_peak_ring'],cfg['control_peak_radius'],'radii',np.round(rr[11:23],5),flush=True)
(P/'flare-roll-studies.json').write_text(json.dumps(configs,indent=2)+'\n')

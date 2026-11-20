from pathlib import Path
import json
import numpy as np
from scipy.interpolate import BSpline
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
c=np.load(P/'controls-032.npy');r=np.linalg.norm(c[:,:,:2],axis=2).mean(1);z=c[:,:,2].mean(1)
configs=[{'variant':'baseline','ring_radii':{}}]+json.loads((P/'flare-roll-studies.json').read_text())
t=np.linspace(11,22,1000)-1
bz=BSpline(np.arange(-3,len(z)+1),z,3);zz=bz(t);dz=bz(t,1);d2z=bz(t,2)
canvas=Image.new('RGB',(920,740),(16,21,29));d=ImageDraw.Draw(canvas)
colors=['#d5d7dd','#f4ae70','#7ad3ed','#bd99ed']
report=[]
for j,(cfg,col) in enumerate(zip(configs,colors)):
    rr=r.copy()
    for key,rad in cfg['ring_radii'].items():rr[int(key)]=rad
    br=BSpline(np.arange(-3,len(rr)+1),rr,3);radius=br(t);dr=br(t,1);d2r=br(t,2)
    curvature=(d2r*dz-dr*d2z)/(dr*dr+dz*dz)**1.5
    x=65+(radius-.98)*6200;y=650-(zz-.22)*2000
    d.line(list(zip(x,y)),fill=col,width=3)
    # Signed curvature above the groove: a convex roll should not acquire a
    # secondary inward bend on its lower/outer face.
    take=(t+1>14)&(t+1<20)
    changes=int(np.count_nonzero(np.diff(np.sign(curvature[take]))))
    report.append({'variant':cfg['variant'],'outer_turn_curvature_sign_changes':changes,
       'positive_curvature_fraction_outer_turn':float((curvature[take]>0).mean()),
       'sampled_radius_peak':float(radius.max()),'peak_height':float(zz[radius.argmax()])})
    d.text((465,40+j*28),cfg['variant'],fill=col)
    d.text((465,180+j*80),f"Convex-turn curvature reversals: {changes}",fill=col)
for height in [.25,.30,.35,.40,.45,.50]:
    y=650-(height-.22)*2000;d.line([(45,y),(400,y)],fill=(38,44,54));d.text((5,y-5),f'{height:.2f}',fill='white')
d.text((35,15),'Cubic subdivision meridian approximation: lower flare / groove',fill='white')
d.text((465,570),'Horizontal: radius   Vertical: physical height',fill='white')
d.text((465,600),'Material and light settings remain fixed.',fill='white')
canvas.save(P/'flare-meridians.png')
(P/'curvature-analysis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

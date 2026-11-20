from pathlib import Path
from PIL import Image
import numpy as np,json
r=Path(__file__).resolve().parents[2];get=lambda p:np.asarray(Image.open(p).convert('RGB'),dtype=float)
a=get(r/'build/rook-mission/070-neck-wood/render.png');b=get(r/'build/rook-mission/071-neck-wood/render.png');ref=get(r/'assets/rook/ref.png');response=(b-a)/.2;mask=np.linalg.norm(response,axis=2)>3;mask[:595]=False;mask[800:]=False;mask[:,:330]=False;mask[:,650:]=False;step=float(np.sum(response[mask]*(ref-a)[mask])/np.sum(response[mask]**2));scale=.65+step;report={'predicted_srgb_donor_scale':scale,'fit_pixels':int(mask.sum()),'method':'Least-squares local display response from real renders at .65 and .85. Prediction only; nonlinear shading/clipping require a fresh render.','accepted_scale':None};(r/'build/rook-mission/070-neck-wood/next-tone-fit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

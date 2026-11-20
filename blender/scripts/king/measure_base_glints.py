"""Diagnostic highlight size/location at fixed image registration, not a score."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]

def measure(path,box,threshold):
    a=np.asarray(Image.open(path).convert('RGBA'),dtype=float);rgb=a[:,:,:3]*a[:,:,3:4]/255
    x0,y0,x1,y1=box;b=rgb[y0:y1,x0:x1];v=b.min(2);weights=np.maximum(v-threshold,0);yy,xx=np.indices(v.shape);mass=weights.sum()
    center=np.array([(weights*xx).sum()/mass,(weights*yy).sum()/mass]) if mass else np.array([0.,0.]);dx=xx-center[0];dy=yy-center[1]
    covariance=np.array([[(weights*dx*dx).sum(),(weights*dx*dy).sum()],[(weights*dx*dy).sum(),(weights*dy*dy).sum()]])/max(mass,1)
    return dict(pixels_over_threshold=int((weights>0).sum()),weighted_center_xy=(center+[x0,y0]).tolist(),weighted_sigma_xy=np.sqrt(covariance.diagonal()).tolist(),covariance=covariance.tolist(),threshold=threshold,box=box),b

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('variant');p.add_argument('--previous',default='history/king-mission-004/render.png');a=p.parse_args();out=ROOT/'build/king-mission'/a.variant;report={}
    for region,box,threshold in [('upper',[525,815,620,895],80),('lower',[545,910,665,995],65)]:
        rows={};reference=None
        for label,path in [('reference',ROOT/'assets/king/reference.png'),('previous',ROOT/a.previous),('trial',out/'wood.png')]:
            row,rgb=measure(path,box,threshold)
            if reference is None:reference=rgb
            else:row['region_rgb_rmse_255']=float(np.sqrt(np.mean((rgb-reference)**2)))
            rows[label]=row
        report[region]=rows
    report['caveat']='Brightness-threshold morphology is diagnostic only; hue, grain, reflected shape and full appearance still require visual assessment.'
    (out/'glint-shape.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))

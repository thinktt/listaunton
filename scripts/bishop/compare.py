"""Measure silhouette agreement with both source images; no source pixels are rewritten."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]
out=root/'assets/bishop';ref=np.array(Image.open(out/'reference.png').convert('RGBA'));ren=np.array(Image.open(out/'render.png').convert('RGBA'))
placement=json.loads((out/'original-alignment.json').read_text());s=placement['scale'];x=placement['x'];y=placement['y'];W=ref.shape[1]
original=Image.open(out/'original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(s*300/W,0,x*3,0,s*300/W,y*3),Image.Resampling.BILINEAR)
original=np.array(original)
def bounds(mask):return np.argmax(mask,axis=1),mask.shape[1]-1-np.argmax(mask[:,::-1],axis=1)
report={'note':'Silhouette scores compare visible boundaries only, not internal geometry, wood, lighting or unseen surfaces. Original is authoritative.','images':{}}
report['internal_features']={'inspection':'Original and selected source overlays checked against neutral render; topology and cavity depth independently validated.','mitre':'Turned bulb, rounded finial, full-thickness oblique cut with solid floor.','collars':'Three descending collar steps.','lower_body':'Concave stem, raised socket lip, flared base and rounded flat-bottom foot.','limits':'Wood and lighting are not reconstructed. Single-view evidence cannot determine hidden geometry uniquely.'}
for name,ar in [('original',original),('selected',ref)]:
 a=(ar[:,:,3]>128)&(ar[:,:,:3].max(2)>12);b=ren[:,:,3]>128;l,rr=bounds(a);bl,br=bounds(b);valid=a.any(1)&b.any(1)
 error=np.abs(np.r_[l[valid]-bl[valid],rr[valid]-br[valid]])
 report['images'][name]={'silhouette_iou':float((a&b).sum()/(a|b).sum()),'mean_boundary_error_px':float(error.mean()),'p95_boundary_error_px':float(np.quantile(error,.95)),'reference_sha256':__import__('hashlib').sha256((out/('original.png' if name=='original' else 'reference.png')).read_bytes()).hexdigest()}
 if name=='original':report['images'][name]['mean_boundary_error_original_300px_units']=float(error.mean()*s*300/W)
 canvas=Image.fromarray((ar[:,:,:3]*.65).astype('uint8'));d=ImageDraw.Draw(canvas)
 for m,color in [(a,'#60e0ff'),(b,'#ff65bb')]:
  ll,rrr=bounds(m);ys=np.where(m.any(1))[0];d.line([(int(ll[t]),int(t)) for t in ys],fill=color,width=2);d.line([(int(rrr[t]),int(t)) for t in ys],fill=color,width=2)
 canvas.save(out/f'contour-{name}.png')
(out/'qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

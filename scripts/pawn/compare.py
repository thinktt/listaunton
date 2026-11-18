"""Measure silhouette agreement with both source images; no source pixels are rewritten."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
from audit_mission import mask
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]
out=root/'assets/pawn';ref=np.array(Image.open(out/'reference.png').convert('RGBA'));ren=np.array(Image.open(out/'render.png').convert('RGBA'))
placement=json.loads((out/'original-alignment.json').read_text());s=placement['scale'];x=placement['x'];y=placement['y'];W=ref.shape[1]
original=Image.open(out/'original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(s*300/W,0,x*3,0,s*300/W,y*3),Image.Resampling.BILINEAR)
original=np.array(original)
registrations=json.loads((root/'assets/candidates/alignment.json').read_text())['pieces']['pawn']
wa=next(a for a in registrations if a['id']=='white')
white=Image.open(out/'white-original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(s/wa['scale']*300/W,0,(x-wa['x'])*3/wa['scale'],0,s/wa['scale']*300/W,(y-wa['y'])*3/wa['scale']),Image.Resampling.BILINEAR)
white=np.array(white)
def bounds(mask):return np.argmax(mask,axis=1),mask.shape[1]-1-np.argmax(mask[:,::-1],axis=1)
report={'note':'Silhouette scores compare visible boundaries only, not internal geometry, wood, lighting or unseen surfaces. Original is authoritative.','images':{}}
for name,ar in [('original',original),('original_white',white),('selected',ref)]:
 a=mask(Image.fromarray(ar),True);b=mask(Image.fromarray(ren),False);l,rr=bounds(a);bl,br=bounds(b);valid=a.any(1)&b.any(1)
 error=np.abs(np.r_[l[valid]-bl[valid],rr[valid]-br[valid]])
 report['images'][name]={'silhouette_iou':float((a&b).sum()/(a|b).sum()),'mean_boundary_error_px':float(error.mean()),'p95_boundary_error_px':float(np.quantile(error,.95)),'reference_sha256':__import__('hashlib').sha256((out/({'original':'original.png','original_white':'white-original.png','selected':'reference.png'}[name])).read_bytes()).hexdigest()}
 canvas=Image.fromarray((ar[:,:,:3]*.65).astype('uint8'));d=ImageDraw.Draw(canvas)
 for m,color in [(a,'#60e0ff'),(b,'#ff65bb')]:
  ll,rrr=bounds(m);ys=np.where(m.any(1))[0];d.line([(int(ll[t]),int(t)) for t in ys],fill=color,width=2);d.line([(int(rrr[t]),int(t)) for t in ys],fill=color,width=2)
 canvas.save(out/f'contour-{name}.png')
report['internal_feature_review']={
 'camera_elevation_degrees':54,
 'head':'Round head radius 28.25 original pixels; center y118.3. Original black silhouette wins over the slightly broader selected render.',
 'collar':'Rounded lip and broad inner seat support the ball without the exposed peg; head lowered four original pixels after owner side-view review.',
 'stem':'Curved narrow stem widens into an upper shoulder bead and a short lower wall; both original sprites inspected.',
 'base':'Two broad rolls separated by a continuous narrow groove. Base underside and back edge lowered after pass 1.',
 'limitations':'Single-view rotational reconstruction. Unseen underside and exact material are inferred. Neutral clay does not reproduce wood or its reflections. Selected Black 2 differs measurably from the original silhouette.'}
if (out/'mission-validation.json').is_file():
 report['internal_feature_review'].update(head='Round upper sphere with the widest latitude raised to fit both originals; original physical apex-to-floor height retained.',collar='The accepted broad seat radius and collar remain attached to the lower head; the lower spherical flank curves into the seat.',base='Compact turned base with a flatter sole edge; the existing front groove and upper flare remain inspection priorities.',limitations='The unseen surface, illumination and pigment are inferred. Compare fixed beauty, clay and rotating model separately.')
 report['mask_method']='Largest component with holes filled; reference max RGB >12 and alpha >127, model alpha >127.'
 accepted=json.loads((out/'mission-validation.json').read_text())
 if 'pawn-shared-base' in Path(accepted.get('variant','')).parts:
  report['internal_feature_review'].update(
   head='A shallow adjustment to the dome keeps the ball seated as the total pawn height decreases.',
   stem='The narrower waist curves into the upper collar and joins the first support above the shared socket.',
   base='The sole, foot, single groove, flare and socket share the queen and king turning at one uniform scale.')
(out/'qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

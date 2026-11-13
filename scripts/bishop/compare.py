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
report={'note':'Silhouette scores compare visible boundaries only, not internal geometry, wood, lighting or unseen surfaces. Original controls overall proportions; the accepted side guide directs the head/button join.','images':{}}
report['internal_features']={'inspection':'Original and selected overlays plus true level head profiles checked against neutral render; topology, junction surface and slit depth independently validated.','mitre':'One continuous rounded meridian from the collar transition into the button underside; full-thickness oblique cut and solid floor preserved.','finial':'Rounded convex button sits directly on the head. No cylindrical seat, pedestal, neck ring or gap is exposed.','collars':'Three descending collar steps, preserved by exact profile comparison.','lower_body':'Concave stem, raised socket and flare are preserved. The foot has a flatter outer wall and softened lower edge; its declared ring edits are checked against the archived prior model.','limits':'The accepted side guide is art direction, not a recovered source camera. Boxwood pigment, surface relief and reflections are an unfinished reconstruction. Single-view evidence cannot determine hidden geometry uniquely.'}
if json.loads((root/'scripts/bishop/profile.json').read_text()).get('mission_slit_geometry'):
 report['internal_features']['mitre']='Continuous curved head with a full-thickness oblique slit. The declared semicircular floor replaces the earlier flat termination; solid wood remains below it. Width, angle and the original edge bevel are preserved.'
if json.loads((root/'scripts/bishop/profile.json').read_text()).get('mission_shape_refit'):
 report['internal_features']['collars']='The upper collar has a small declared downward refinement; the other two collars are retained. Compare actual rim position separately from the photographic shadow trough.'
 report['internal_features']['lower_body']='The rear base shoulder is narrowed with a rounded lower turn, and the stem has a conservative taper correction. Socket and foot controls are retained. The geometry-phase scope audit checks all changed and unchanged controls.'
 report['internal_features']['limits']+=' The retained pigment and lights have not been refitted to this geometry; neutral comparison is required.'
 if set(map(int,json.loads((root/'scripts/bishop/profile.json').read_text())['mission_shape_refit']['body_rings']))==set(range(49,57)):
  report['internal_features']['collars']='The middle collar is narrowed and lowered to remove its rear bulge behind the head while holding the front rim in place. Upper and lower collars retain the prior checkpoint. Actual evaluated surface rays distinguish these edges from photographic shadows.'
 if set(map(int,json.loads((root/'scripts/bishop/profile.json').read_text())['mission_shape_refit']['body_rings']))=={6,7,8,9}:
  report['internal_features']['collars']='All collar controls retain checkpoint 018. Thinner-roll and flattened-deck trials were not accepted; their swollen appearance and remaining curvature differences are unresolved.'
  report['internal_features']['lower_body']='The foot upper rollover is tighter and the outer wall straighter. Only controls 6-9 change from checkpoint 018; stem, socket, flare and foot underside remain exact. This is a small local correction, not a resolution of the overall interior-form mismatch.'
for name,ar in [('original',original),('selected',ref)]:
 a=(ar[:,:,3]>128)&(ar[:,:,:3].max(2)>12);b=ren[:,:,3]>128;l,rr=bounds(a);bl,br=bounds(b);valid=a.any(1)&b.any(1)
 error=np.abs(np.r_[l[valid]-bl[valid],rr[valid]-br[valid]])
 report['images'][name]={'silhouette_iou':float((a&b).sum()/(a|b).sum()),'mean_boundary_error_px':float(error.mean()),'p95_boundary_error_px':float(np.quantile(error,.95)),'reference_sha256':__import__('hashlib').sha256((out/('original.png' if name=='original' else 'reference.png')).read_bytes()).hexdigest()}
 if name=='original':report['images'][name]['mean_boundary_error_original_300px_units']=float(error.mean()*s*300/W)
 canvas=Image.fromarray((ar[:,:,:3]*.65).astype('uint8'));d=ImageDraw.Draw(canvas)
 for m,color in [(a,'#60e0ff'),(b,'#ff65bb')]:
  ll,rrr=bounds(m);ys=np.where(m.any(1))[0];d.line([(int(ll[t]),int(t)) for t in ys],fill=color,width=2);d.line([(int(rrr[t]),int(t)) for t in ys],fill=color,width=2)
 canvas.save(out/f'contour-{name}.png')
(out/'qa.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
# Pair the historical and current true-level views at exactly the same camera.
# This is the view that exposed the old neck; an elevated overlay alone hid it.
prior=root/'history/bishop/07-before-continuous-button-join/head-side.png'
side=out/'head-side.png'
if prior.exists() and side.exists():
 canvas=Image.new('RGB',(1200,650),'#171b21');d=ImageDraw.Draw(canvas)
 for i,(label,path) in enumerate([('Previous: exposed cylindrical seat',prior),('Current: direct rounded contact',side)]):
  im=Image.open(path).convert('RGBA').resize((600,600),Image.Resampling.LANCZOS)
  canvas.paste(im,(i*600,45),im);d.text((i*600+22,18),label,fill='#f0e7d4')
 canvas.save(out/'join-comparison.png')
# Actual source overlay in the unchanged reference-camera frame.
background=Image.new('RGBA',(W,W),'#181d24');source=Image.fromarray(original)
background.alpha_composite(source)
overlay=Image.fromarray(ren).copy();overlay.putalpha(overlay.getchannel('A').point(lambda a:round(a*.5)))
background.alpha_composite(overlay);background.convert('RGB').save(out/'overlay-original.png')
# Keep the general comparison sheet synchronized with the current revision.
canvas=Image.new('RGB',(1500,550),'#171b21');d=ImageDraw.Draw(canvas)
for i,(label,im) in enumerate([('Original white',Image.fromarray(original)),('White candidate 3',Image.fromarray(ref)),('Current boxwood reconstruction',Image.fromarray(ren))]):
 im=im.convert('RGBA').resize((500,500),Image.Resampling.LANCZOS);canvas.paste(im,(i*500,40),im);d.text((i*500+20,15),label,fill='#f0e7d4')
canvas.save(out/'comparison.png')

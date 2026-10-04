"""Measure silhouette agreement with both source images; no source pixels are rewritten."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[2]
out=root/'assets/rook';ref=np.array(Image.open(out/'ref.png').convert('RGBA'));ren=np.array(Image.open(out/'render.png').convert('RGBA'))
placement=json.loads((out/'original-alignment.json').read_text());s=placement['scale'];x=placement['x'];y=placement['y'];W=ref.shape[1]
original=Image.open(out/'original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(s*300/W,0,x*3,0,s*300/W,y*3),Image.Resampling.BILINEAR)
original=np.array(original)
def bounds(mask):return np.argmax(mask,axis=1),mask.shape[1]-1-np.argmax(mask[:,::-1],axis=1)
report={'note':'Silhouette scores compare visible boundaries only, not internal geometry, wood, lighting or unseen surfaces. Original is authoritative.','images':{}}
for name,ar in [('original',original),('selected',ref)]:
 a=(ar[:,:,3]>128)&(ar[:,:,:3].max(2)>12);b=ren[:,:,3]>128;l,rr=bounds(a);bl,br=bounds(b);valid=a.any(1)&b.any(1)
 error=np.abs(np.r_[l[valid]-bl[valid],rr[valid]-br[valid]])
 report['images'][name]={'silhouette_iou':float((a&b).sum()/(a|b).sum()),'mean_boundary_error_px':float(error.mean()),'p95_boundary_error_px':float(np.quantile(error,.95)),'reference_sha256':__import__('hashlib').sha256((out/('original.png' if name=='original' else 'ref.png')).read_bytes()).hexdigest()}
 canvas=Image.fromarray((ar[:,:,:3]*.65).astype('uint8'));d=ImageDraw.Draw(canvas)
 for m,color in [(a,'#60e0ff'),(b,'#ff65bb')]:
  ll,rrr=bounds(m);ys=np.where(m.any(1))[0];d.line([(int(ll[t]),int(t)) for t in ys],fill=color,width=2);d.line([(int(rrr[t]),int(t)) for t in ys],fill=color,width=2)
 canvas.save(out/f'contour-{name}.png')
# The very dark original has near-black wood beside a black cast shadow.
# Preserve the strict inherited threshold and expose its sensitivity explicitly.
report['original_mask_sensitivity']={}
for threshold in [4,8,12,16]:
 a=(original[:,:,3]>128)&(original[:,:,:3].max(2)>threshold);b=ren[:,:,3]>128
 report['original_mask_sensitivity'][str(threshold)]=float((a&b).sum()/(a|b).sum())
report['camera']={'elevation_degrees':54,'roll_degrees':-0.35,'frame':'selected candidate 8; original registered by preserved uniform alignment'}
report['internal_features']={'wall_thickness_px_in_model_profile':23,'outer_radius_px':177,'thickness_fraction_of_radius':23/177,'crenel_count':4,'floor_rear_native_original_y_target':[82,85],'assessment':'Raised the cavity floor by 10 model-frame pixels after comparing both original colors. Equal annular wall thickness on all four merlons. Rectangular slots, rounded edges, continuous outer bowl and two turned foot beads inspected separately from silhouette.'}
report['limitations']=['Single-view reconstruction: unseen surfaces inferred with rotational symmetry and four equal crenels.','Dark original shadow/wood boundary changes the measured silhouette with threshold. Scores do not measure recovered topology or wood.','The selected image has a somewhat deeper-looking interior than the original; original proportions take precedence.','Neutral clay and lighting are diagnostic. Original wood and finish are not reconstructed.']
for label,ar in [('original',original),('selected',ref)]:
 back=Image.new('RGBA',(W,W),(0,0,0,255));back.alpha_composite(Image.fromarray(ar));model=Image.new('RGBA',(W,W),(0,0,0,255));model.alpha_composite(Image.fromarray(ren));Image.blend(back,model,.5).convert('RGB').save(out/f'overlay-{label}.png')
contact=Image.new('RGB',(1200,580),'#16191e');draw=ImageDraw.Draw(contact)
for i,(label,ar) in enumerate([('Original (registered)',original),('Neutral reconstruction',ren),('Selected candidate 8',ref)]):
 im=Image.fromarray(ar);bg=Image.new('RGBA',(W,W),(0,0,0,255));bg.alpha_composite(im);crop=bg.crop((190,230,780,1100)).resize((354,522),Image.Resampling.LANCZOS);contact.paste(crop,(i*400+23,42));draw.text((i*400+23,16),label,fill='#eeeeee')
contact.save(out/'comparison.png')
(out/'qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

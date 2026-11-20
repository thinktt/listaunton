"""Measure actual six-angle renders and create source overlays and contact sheets."""
from pathlib import Path
import argparse,json,hashlib,math
import numpy as np
from PIL import Image,ImageDraw
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args=ap.parse_args();root=args.root
directory=root/'assets/rook-projections';manifest=json.loads((directory/'variants.json').read_text(encoding='utf-8'));assets=root/'assets/rook';W=1254
placement=json.loads((assets/'original-alignment.json').read_text(encoding='utf-8'));s,x,y=[placement[k] for k in ['scale','x','y']]
original=Image.open(assets/'original.png').convert('RGBA').transform((W,W),Image.Transform.AFFINE,(s*300/W,0,x*3,0,s*300/W,y*3),Image.Resampling.BILINEAR)
sources={'original':np.array(original),'selected':np.array(Image.open(assets/'ref.png').convert('RGBA'))}
profiles=Image.new('RGB',(1800,500),'#15191e');profile_draw=ImageDraw.Draw(profiles)
renders=Image.new('RGB',(1800,535),'#15191e');render_draw=ImageDraw.Draw(renders)
def mask(ar,threshold=12):return (ar[:,:,3]>128)&(ar[:,:,:3].max(2)>threshold)
def bounds(m):return m.argmax(1),m.shape[1]-1-m[:,::-1].argmax(1)
def backdrop(ar):
 im=Image.new('RGBA',(W,W),(0,0,0,255));im.alpha_composite(Image.fromarray(ar));return im
def metric(a,b):
 l,r=bounds(a);ll,rr=bounds(b);valid=a.any(1)&b.any(1);errors=np.abs(np.r_[l[valid]-ll[valid],r[valid]-rr[valid]])
 return {'silhouette_iou':float((a&b).sum()/(a|b).sum()),'mean_boundary_error_px':float(errors.mean()),'p95_boundary_error_px':float(np.quantile(errors,.95))}
for i,item in enumerate(manifest['variants']):
 dest=root/item['assetDir'];ren=np.array(Image.open(dest/'render.png').convert('RGBA'));b=ren[:,:,3]>128;cfg=json.loads((dest/'profile.json').read_text(encoding='utf-8'))
 report={'note':'Strict historical RGB > 12 mask retained for comparability. Fitting used RGB > 8 to retain near-black original wood; all four threshold scores are exposed. Scores are silhouette evidence, not proof of internal or unseen geometry.','images':{},'original_mask_sensitivity':{},'elevation_degrees':item['elevation'],'fit':item['fit'],'visible_wall_thickness_fraction':(cfg['turret']['outer_radius']-cfg['turret']['inner_radius'])/cfg['turret']['outer_radius']}
 for name,ar in sources.items():
  a=mask(ar);report['images'][name]={**metric(a,b),'reference_sha256':hashlib.sha256((assets/('original.png' if name=='original' else 'ref.png')).read_bytes()).hexdigest()}
  canvas=Image.fromarray((ar[:,:,:3]*.65).astype('uint8'));d=ImageDraw.Draw(canvas)
  for m,color in [(a,'#60e0ff'),(b,'#ff65bb')]:
   ll,rr=bounds(m);ys=np.where(m.any(1))[0];d.line([(int(ll[t]),int(t)) for t in ys],fill=color,width=2);d.line([(int(rr[t]),int(t)) for t in ys],fill=color,width=2)
  canvas.save(dest/f'contour-{name}.png');Image.blend(backdrop(ar),backdrop(ren),.5).convert('RGB').save(dest/f'overlay-{name}.png')
 for threshold in [4,8,12,16]:report['original_mask_sensitivity'][str(threshold)]=metric(mask(sources['original'],threshold),b)['silhouette_iou']
 camera=json.loads((dest/'camera.json').read_text(encoding='utf-8'));view=np.asarray(camera['worldToCamera']).reshape(4,4);proj=np.asarray(camera['projectionMatrix']).reshape(4,4)
 def pixel(radius,ycenter,front):
  z=(cfg['y0']-ycenter)/(cfg['scale']*math.cos(math.radians(cfg['elevation'])));v=proj@view@np.array([0,-radius/cfg['scale'] if front else radius/cfg['scale'],z,1]);return [(v[0]/v[3]+1)*W/2,(1-v[1]/v[3])*W/2]
 fy=pixel(cfg['profile'][56][0],cfg['profile'][56][1],False)[1];native=(fy*s+y*W/100)*300/W
 report['floor_rear_landmark']={'native_original_y_estimate':float(native),'original_visual_interval':[82,85],'note':'Projected floor-edge parameter, independently constrained by the original white and black sprites. Bevel/shading shifts its visible highlight.'}
 (dest/'qa.json').write_text(json.dumps(report,indent=2)+'\n');item['comparison']=report['images'];item['originalMask8IoU']=report['original_mask_sensitivity']['8']
 profile=Image.open(dest/'profile.png').convert('RGBA');pb=Image.new('RGBA',profile.size,(0,0,0,255));pb.alpha_composite(profile);profiles.paste(pb.resize((300,450),Image.Resampling.LANCZOS),(i*300,40));profile_draw.text((i*300+12,12),item['label'],fill='#eceae5')
 rb=backdrop(ren).crop((190,230,780,1120)).resize((300,452),Image.Resampling.LANCZOS);renders.paste(rb,(i*300,40));render_draw.text((i*300+12,12),item['label'],fill='#eceae5');render_draw.text((i*300+12,503),'Original IoU '+str(round(report['images']['original']['silhouette_iou'],4)),fill='#bfc5cf')
 print(item['id'],report['images']['original'],report['floor_rear_landmark'],flush=True)
profiles.save(directory/'profiles-comparison.png');renders.save(directory/'reference-renders-comparison.png');(directory/'variants.json').write_text(json.dumps(manifest,indent=2)+'\n')

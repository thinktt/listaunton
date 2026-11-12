"""Compare measured atlas visibility with the older interpolated confidence."""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--capture',required=True);p.add_argument('--atlas',required=True)
a=p.parse_args();folder=ROOT/a.capture;meta=json.loads((folder/'manifest.json').read_text())
encoded=np.load(folder/'position.npy');normal=np.load(folder/'normal.npy')[:,:,:3]*2-1
coverage=np.clip(np.load(folder/'legacy-coverage.npy')[:,:,0],0,1)
valid=(encoded[:,:,:3].min(2)>.05)&(np.linalg.norm(normal,axis=2)>.9)
lo=np.array(meta['encode_min'],np.float32);extent=np.array(meta['encode_extent'],np.float32)
positions=(encoded[:,:,:3]-.1)/.8*extent+lo
view=np.array(meta['view_direction'],np.float32);view/=np.linalg.norm(view)
frame=np.load(folder/'fixed-position.npy');frame_positions=(frame[:,:,:3]-.1)/.8*extent+lo
frame_depth=frame_positions@view;depth=positions@view
matrix=np.array(meta['world_to_clip'],np.float32);w,h=meta['image_size']
x=((positions@matrix[0,:3]+matrix[0,3])*.5+.5)*w-.5
y=(.5-(positions@matrix[1,:3]+matrix[1,3])*.5)*h-.5
ix=np.rint(x).astype(np.int32);iy=np.rint(y).astype(np.int32)
inside=(ix>=0)&(ix<w)&(iy>=0)&(iy<h)
error=np.full(valid.shape,np.inf,dtype=np.float32)
for dy in [-1,0,1]:
    for dx in [-1,0,1]:
        sx=np.clip(ix+dx,0,w-1);sy=np.clip(iy+dy,0,h-1)
        alpha=frame[sy,sx,3]>.999
        value=np.abs(frame_depth[sy,sx]-depth);value[~alpha]=np.inf
        error=np.minimum(error,value)
facing=(normal@view)>-.005
visible=valid&inside&facing&(error<.02)
np.save(folder/'visible.npy',visible);np.save(folder/'valid.npy',valid)
np.save(folder/'visibility-depth-error.npy',error)
atlas=np.array(Image.open(ROOT/a.atlas).convert('RGB'))
rgb=atlas.astype(np.float32)/255;linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
broad=blur(np.log(np.maximum(linear,.0001)),12,2)
gradient=np.hypot(*np.gradient(broad.mean(2)))
boundary=valid&(coverage>.02)&(coverage<.98)
report={'source':meta['source'],'source_sha256':meta['source_sha256'],
 'atlas':a.atlas,'atlas_sha256':hashlib.sha256((ROOT/a.atlas).read_bytes()).hexdigest(),
 'valid_texels':int(valid.sum()),'measured_visible_texels':int(visible.sum()),
 'visible_fraction':float(visible.sum()/valid.sum()),
 'visible_with_legacy_confidence_below_98_percent':int((visible&(coverage<.98)).sum()),
 'legacy_transition_texels':int(boundary.sum()),'transition_visible_fraction':float(visible[boundary].mean()),
 'mean_broad_gradient_on_visible_transition':float(gradient[boundary&visible].mean()),
 'mean_broad_gradient_on_hidden_transition':float(gradient[boundary&~visible].mean()),
 'thresholds':{'depth_tolerance_world_units':.02,'nearest_neighborhood_pixels':3,'facing_dot_min':-.005},
 'method':'Atlas positions are reprojected into an independently rendered fixed-view position field. A conservative 3x3 neighborhood and depth tolerance protect grazing/antialiased edges. This is a visibility measurement, not a final material.'}
(folder/'visibility.json').write_text(json.dumps(report,indent=2)+'\n')
colors=np.zeros_like(atlas);colors[valid&~visible]=[190,55,48];colors[visible]=[48,177,230]
marked=(atlas.astype(np.float32)*.55+colors*.45).astype(np.uint8)
confidence=np.repeat(np.uint8(coverage*255)[:,:,None],3,axis=2)
sheet=Image.new('RGB',(1536,550),'#171b21');draw=ImageDraw.Draw(sheet)
for i,(name,im) in enumerate([('Accepted pigment',atlas),('Blue: visible / red: hidden',marked),('Old pigment confidence',confidence)]):
    sheet.paste(Image.fromarray(im).resize((512,512),Image.Resampling.LANCZOS),(i*512,38));draw.text((i*512+12,12),name,fill='white')
sheet.save(folder/'visibility-atlas.png');print(json.dumps(report,indent=2))

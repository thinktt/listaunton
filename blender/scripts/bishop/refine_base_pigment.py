"""Bounded per-channel pigment feedback on the observed lower-base patch only.

Saturated reference channels are lower bounds, not a reason to discard the
other channels. Real measured BSDF responses still downweight specular regions.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from image_math import blur

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--response', default='build/bishop-mission/131-base-response')
p.add_argument('--out', default='build/bishop-mission/132-base-pigment')
p.add_argument('--strength', type=float, default=1)
p.add_argument('--clipped-bound-weight', type=float, default=.6)
p.add_argument('--max-gain', type=float, default=1.6)
a = p.parse_args()
assert 0 < a.strength <= 1
assert 0 <= a.clipped_bound_weight <= 1 and 1 <= a.max_gain <= 2
response = ROOT/a.response
out = ROOT/a.out
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True, exist_ok=True)
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
source = ROOT/'history/bishop-mission-015/bishop-boxwood-albedo.png'
source_model = ROOT/'history/bishop-mission-015/bishop-rebuilt.blend'
assert sha(source) == 'c09df839f9ab363f5e4c2ed3d669293f99a81de59a449f85096a49e849aa8f2a'
assert sha(source_model) == 'dc3a11db2800b79bf45baee458d5b6a53a7602b3531137afe5db9b914a45cf07'
rm = json.loads((response/'manifest.json').read_text())
assert rm['source_sha256'] == sha(source_model) and rm['source_unchanged']
assert sha(ROOT/'assets/bishop/reference.png') == rm['reference_sha256']
capture = ROOT/'build/bishop-mission/099-atlas-surface'
cm = json.loads((capture/'manifest.json').read_text())
assert sha(ROOT/cm['source']) == cm['source_sha256']
audits = [ROOT/f'docs/bishop-mission/iteration-{n}/validation/pigment-validation.json' for n in ['013','015']]
inherited_hash = cm['source_sha256']
for path in audits:
    audit = json.loads(path.read_text())
    assert audit['passed'] and audit['reopened_audit'] and audit['only_declared_atlas_changed']
    assert audit['geometry_uvs_material_graph_relief_camera_lights_world_and_render_path_preserved']
    assert audit['source_sha256'] == inherited_hash
    inherited_hash = audit['model_sha256']
assert inherited_hash == sha(source_model)

black = np.load(response/'black-bsdf.npy')[:,:,:3]
white = np.load(response/'white-bsdf.npy')[:,:,:3]
actual = np.load(response/'linear-beauty.npy')
pigment = np.load(response/'pigment.npy')
target = np.load(response/'reference-linear.npy')
target_srgb = np.load(response/'reference-srgb.npy')
ref = np.array(Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA'))
interior = (actual[:,:,3]>.995)&(pigment[:,:,3]>.995)&(ref[:,:,3]>127)&(ref[:,:,:3].max(2)>12)
interior = blur(interior.astype(np.float32),5)>.999
ratio = np.clip(np.maximum(target-black,0)/np.maximum(actual[:,:,:3]-black,.001),.8,a.max_gain)
spec_ratio = black/np.maximum(target,.001)
confidence = np.clip((.8-spec_ratio)/.5,0,1)
confidence *= np.clip((white-black-.015)/.06,0,1)
clipped = target_srgb >= .995
ordinary = np.clip((.995-target_srgb)/.02,0,1)
# A clipped channel supplies only a lower bound. It may brighten pigment if
# the current image is below that bound, but cannot justify darkening it.
bound = clipped & (actual[:,:,:3] < .95) & (ratio > 1)
confidence *= np.where(clipped,bound.astype(float)*a.clipped_bound_weight,ordinary)
confidence *= interior[:,:,None]
log_feedback = blur(confidence*np.log(ratio),2)

position = np.load(capture/'position.npy')[:,:,:3]
position = (position-cm['encode_offset'])/cm['encode_scale']*np.array(cm['encode_extent'])+np.array(cm['encode_min'])
normal = np.load(capture/'normal.npy')[:,:,:3]*2-1
visible = np.load(capture/'visible.npy')
valid = np.load(capture/'valid.npy')
matrix = np.array(cm['world_to_clip'])
fw,fh = cm['image_size']
x = ((position@matrix[0,:3]+matrix[0,3])*.5+.5)*fw-.5
y = (.5-(position@matrix[1,:3]+matrix[1,3])*.5)*fh-.5
xx,yy = np.clip(x,0,fw-1),np.clip(y,0,fh-1)
ix,iy = np.floor(xx).astype(int),np.floor(yy).astype(int)
jx,jy = np.minimum(ix+1,fw-1),np.minimum(iy+1,fh-1)
fx,fy = (xx-ix)[:,:,None],(yy-iy)[:,:,None]
field = (log_feedback[iy,ix]*(1-fx)+log_feedback[iy,jx]*fx)*(1-fy)
field += (log_feedback[jy,ix]*(1-fx)+log_feedback[jy,jx]*fx)*fy

def smooth(v):
    v=np.clip(v,0,1)
    return v*v*(3-2*v)

radius = np.sqrt(((x-583)/100)**2+((y-978)/65)**2)
scope = smooth((1.15-radius)/.45)
height = position[:,:,2]
scope *= smooth((height-.44)/.06)*smooth((.99-height)/.09)
scope *= valid*visible*((x>=0)&(x<=fw-1)&(y>=0)&(y<=fh-1))
scope *= smooth(((normal@np.array(cm['view_direction']))-.05)/.2)
old = np.array(Image.open(source).convert('RGBA'))
rgb = old[:,:,:3].astype(np.float32)/255
linear = np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
new_linear = np.clip(linear*np.exp(a.strength*scope[:,:,None]*field),0,.85)
srgb = np.where(new_linear<=.0031308,new_linear*12.92,1.055*new_linear**(1/2.4)-.055)
new = old.copy()
active = scope>0
new[active,:3] = np.uint8(np.rint(np.clip(srgb[active],0,1)*255))
assert np.array_equal(new[~active],old[~active]) and np.array_equal(new[:,:,3],old[:,:,3])
Image.fromarray(new).save(out/'albedo.png')
np.save(out/'scope.npy',scope.astype(np.float32))
sheet = Image.new('RGB',(1536,550),'#171b21')
draw=ImageDraw.Draw(sheet)
for i,(label,pixels) in enumerate([('Accepted 015 pigment',old),('Local per-channel feedback',new),('Physical-surface scope',np.uint8(np.clip(scope,0,1)*255))]):
    sheet.paste(Image.fromarray(pixels).convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(512*i,38))
    draw.text((512*i+10,12),label,fill='white')
sheet.save(out/'atlas-comparison.png')
record = dict(source_atlas=source.relative_to(ROOT).as_posix(),source_atlas_sha256=sha(source),
    source=source_model.relative_to(ROOT).as_posix(),source_sha256=sha(source_model),
    response=a.response,response_manifest_sha256=sha(response/'manifest.json'),
    reference_sha256=rm['reference_sha256'],capture=capture.relative_to(ROOT).as_posix(),
    capture_manifest_sha256=sha(capture/'manifest.json'),
    geometry_inheritance_audits=[dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path)) for path in audits],
    strength=a.strength,clipped_bound_weight=a.clipped_bound_weight,feedback_bounds=[.8,a.max_gain],linear_pigment_cap=.85,
    ellipse=[583,978,100,65],radial_feather=[.70,1.15],height_feather=[.44,.50,.90,.99],
    changed_texels=int(np.any(new!=old,axis=2).sum()),scope_texels=int(active.sum()),
    alpha_and_outside_scope_exact=True,output_sha256=sha(out/'albedo.png'),scope_sha256=sha(out/'scope.npy'),
    note='Local approximate material inference from actual BSDF response. Clipped reference channels are lower bounds; other channels remain usable. Specular-dominated samples have low weight. No reference pixels, lights, relief, UVs, camera or geometry are changed. Requires a fresh real-BSDF render and scope audit.')
(out/'pigment.json').write_text(json.dumps(record,indent=2)+'\n',newline='\n')
print('BASE_PIGMENT_PREPARED',json.dumps(record),flush=True)

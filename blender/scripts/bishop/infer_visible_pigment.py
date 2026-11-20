"""Infer visible pigment from actual BSDF response and continue it around the body.

Uses measured visibility, not the older projection-confidence attribute. The
texture remains real BSDF base color; response/emission passes are diagnostics.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--response',default='build/bishop-mission/119-current-response')
p.add_argument('--fallback',default='build/bishop-mission/118-harmonic-pigment/albedo.png')
p.add_argument('--out',default='build/bishop-mission/120-visible-pigment')
p.add_argument('--screen',type=float,default=50)
p.add_argument('--iterations',type=int,default=5000)
p.add_argument('--scope-audit',action='append',default=[],help='Ordered independently reopened atlas audits after the accepted source.')
p.add_argument('--preserve-uncertain-visible',action='store_true',help='Retain the current pigment where reflections make inversion uncertain, instead of replacing it with inferred grain.')
p.add_argument('--retain-visible-range',action='store_true',help='Keep the full existing log-pigment variation in visible regions; requires uncertain-pigment preservation.')
a=p.parse_args();response=ROOT/a.response;fallback=ROOT/a.fallback;out=ROOT/a.out
assert not a.retain_visible_range or a.preserve_uncertain_visible
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve());out.mkdir(parents=True,exist_ok=True)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
rm=json.loads((response/'manifest.json').read_text());assert sha(ROOT/rm['source'])==rm['source_sha256']
reference=ROOT/'assets/bishop/reference.png';assert sha(reference)==rm['reference_sha256']
capture=ROOT/'build/bishop-mission/099-atlas-surface';cm=json.loads((capture/'manifest.json').read_text())
assert sha(ROOT/cm['source'])==cm['source_sha256']
inheritance_path=ROOT/'docs/bishop-mission/iteration-013/validation/pigment-validation.json'
inheritance=json.loads(inheritance_path.read_text())
assert inheritance['source_sha256']==cm['source_sha256']
assert inheritance['geometry_uvs_material_graph_relief_camera_lights_world_and_render_path_preserved']
inherited_hash=inheritance['model_sha256']
audit_records=[]
for audit_path in a.scope_audit:
    audit_file=ROOT/audit_path; scope=json.loads(audit_file.read_text())
    assert scope['passed'] and scope['reopened_audit'] and scope['only_declared_atlas_changed']
    assert scope['geometry_uvs_material_graph_relief_camera_lights_world_and_render_path_preserved']
    assert scope['source_sha256']==inherited_hash
    assert sha(ROOT/scope['source'])==scope['source_sha256']
    assert sha(ROOT/scope['model'])==scope['model_sha256']
    inherited_hash=scope['model_sha256']
    audit_records.append(dict(path=audit_path,sha256=sha(audit_file)))
assert inherited_hash==rm['source_sha256']
black=np.load(response/'black-bsdf.npy')[:,:,:3]
white=np.load(response/'white-bsdf.npy')[:,:,:3]
actual=np.load(response/'linear-beauty.npy')
pigment=np.load(response/'pigment.npy')
target=np.load(response/'reference-linear.npy');srgb_target=np.load(response/'reference-srgb.npy')
roundtrip=np.load(response/'inverse-roundtrip-error.npy')
correction=np.clip(np.maximum(target-black,0)/np.maximum(actual[:,:,:3]-black,.001),.67,1.5)
inferred=np.clip(pigment[:,:,:3]*blur(correction,2),.0001,.85)
specular_ratio=black.max(2)/np.maximum(target.max(2),.001)
confidence=np.clip((.65-specular_ratio)/.45,0,1)
confidence*=np.clip((.995-srgb_target.max(2))/.05,0,1)
confidence*=np.clip(((white-black).mean(2)-.015)/.06,0,1)
confidence*=np.clip((2/255-roundtrip)/(1/255),0,1)
ref=np.array(Image.open(reference).convert('RGBA'))
interior=(actual[:,:,3]>.995)&(pigment[:,:,3]>.995)&(pigment[:,:,:3].max(2)>.005)
interior&=(ref[:,:,3]>127)&(ref[:,:,:3].max(2)>12)
interior=blur(interior.astype(np.float32),5)>.999
confidence=blur(confidence,1)*interior
if a.preserve_uncertain_visible:
    # A weak inverse observation does not invalidate the existing pigment.
    # Preserve its color/detail near reflections and only apply trusted feedback.
    inferred=np.clip(pigment[:,:,:3]*np.exp(confidence[:,:,None]*np.log(blur(correction,2))),.0001,.85)
    projection_confidence=interior.astype(np.float32)
else:
    projection_confidence=confidence
position=np.load(capture/'position.npy')[:,:,:3]
position=(position-cm['encode_offset'])/cm['encode_scale']*np.array(cm['encode_extent'])+np.array(cm['encode_min'])
normal=np.load(capture/'normal.npy')[:,:,:3]*2-1
visible=np.load(capture/'visible.npy');valid=np.load(capture/'valid.npy')
matrix=np.array(cm['world_to_clip']);fw,fh=cm['image_size']
x=((position@matrix[0,:3]+matrix[0,3])*.5+.5)*fw-.5
y=(.5-(position@matrix[1,:3]+matrix[1,3])*.5)*fh-.5
inside=(x>=0)&(x<=fw-1)&(y>=0)&(y<=fh-1)
def sample(field):
    xx=np.clip(x,0,fw-1);yy=np.clip(y,0,fh-1)
    ix=np.floor(xx).astype(int);iy=np.floor(yy).astype(int)
    jx=np.minimum(ix+1,fw-1);jy=np.minimum(iy+1,fh-1)
    fx=xx-ix;fy=yy-iy
    if field.ndim==3:fx=fx[:,:,None];fy=fy[:,:,None]
    return (field[iy,ix]*(1-fx)+field[iy,jx]*fx)*(1-fy)+(field[jy,ix]*(1-fx)+field[jy,jx]*fx)*fy
facing=np.clip(((normal@np.array(cm['view_direction']))-.05)/.2,0,1)
weight=sample(projection_confidence)*visible*valid*inside*facing
desired_log=sample(np.log(inferred))
base=np.array(Image.open(fallback).convert('RGBA'))
rgb=base[:,:,:3].astype(np.float32)/255
base_log=np.log(np.maximum(np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4),.0001))
h,w=weight.shape;x0,x1=int(.01*w),int(.99*w)+1;y0,y1=int(.30*h),int(.99*h)+1
region=np.s_[y0:y1,x0:x1];coverage=weight[region];data=desired_log[region];prior=base_log[region]
denominator=blur(coverage,24,2)
data_broad=blur(data*coverage[:,:,None],24,2)/np.maximum(denominator[:,:,None],1e-5)
prior_broad=blur(prior,24,2)
data_broad=np.where((denominator>.001)[:,:,None],data_broad,prior_broad)
gw=192;gh=round(gw*coverage.shape[0]/coverage.shape[1])
def resize(field,size):return np.array(Image.fromarray(field.astype(np.float32)).resize(size,Image.Resampling.BILINEAR))
size=(gw,gh)
coarse=np.stack([resize(data_broad[:,:,c],size) for c in range(3)],axis=2)
anchor=np.stack([resize(prior_broad[:,:,c],size) for c in range(3)],axis=2)
screen=a.screen*resize(coverage,size)**2
field=anchor.copy();yy,xx=np.indices((gh,gw));parity=(xx+yy)%2
anchor_weight=.001
for iteration in range(a.iterations):
    maximum=0
    for parity_value in [0,1]:
        neighbours=np.roll(field,1,1)+np.roll(field,-1,1)+np.r_[field[:1],field[:-1]]+np.r_[field[1:],field[-1:]]
        next_value=(neighbours+screen[:,:,None]*coarse+anchor_weight*anchor)/(4+screen[:,:,None]+anchor_weight)
        active=parity==parity_value;delta=1.65*(next_value-field)
        maximum=max(maximum,float(np.abs(delta[active]).max()));field[active]+=delta[active]
    if iteration%500==0:print('VISIBLE_PIGMENT_FIELD',iteration,maximum,flush=True)
    if maximum<5e-6:break
continuous=np.stack([resize(field[:,:,c],(coverage.shape[1],coverage.shape[0])) for c in range(3)],axis=2)
raw_fine=data-data_broad
fine=raw_fine if a.retain_visible_range else np.clip(raw_fine,-.8,.4)
reliable=coverage>.9
truncation_fraction=float((np.any((raw_fine<-.8)|(raw_fine>.4),axis=2)&reliable).sum()/max(1,reliable.sum()))
swatch=ROOT/'assets/bishop/materials/inferred-boxwood-source-01.png'
tile=np.array(Image.open(swatch).convert('RGB'),dtype=np.float32)/255
tile=np.log(np.maximum(np.where(tile<=.04045,tile/12.92,((tile+.055)/1.055)**2.4),.0001))
tile=np.clip(tile-blur(tile,32,2),-.4,.4)
yy,xx=np.indices(coverage.shape);u=xx/(coverage.shape[1]-1)
sx=(.5-.49*np.cos(2*np.pi*u))*(tile.shape[1]-1);sy=(yy+y0)/(h-1)*(tile.shape[0]-1)
ix=np.floor(sx).astype(int);iy=np.floor(sy).astype(int);jx=np.minimum(ix+1,tile.shape[1]-1);jy=np.minimum(iy+1,tile.shape[0]-1)
fx=(sx-ix)[:,:,None];fy=(sy-iy)[:,:,None]
generated=(tile[iy,ix]*(1-fx)+tile[iy,jx]*fx)*(1-fy)+(tile[jy,ix]*(1-fx)+tile[jy,jx]*fx)*fy
grain_weight=np.clip((coverage-.15)/.7,0,1);grain_weight=grain_weight*grain_weight*(3-2*grain_weight)
grain_weight=blur(grain_weight,2)
new_log=continuous+fine*grain_weight[:,:,None]+generated*(1-grain_weight[:,:,None])*.8
linear=np.exp(new_log);display=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
new=base.copy();new[y0:y1,x0:x1,:3]=np.uint8(np.rint(np.clip(display,0,1)*255))
assert np.array_equal(new[:,:,3],base[:,:,3])
Image.fromarray(new).save(out/'albedo.png');np.save(out/'visible-confidence.npy',weight.astype(np.float32))
np.save(out/'image-confidence.npy',confidence.astype(np.float32))
sheet=Image.new('RGB',(1536,550),'#171b21');draw=ImageDraw.Draw(sheet)
confidence_image=np.repeat(np.uint8(np.clip(weight,0,1)*255)[:,:,None],3,axis=2)
confidence_label='Measured visibility; uncertain pigment retained' if a.preserve_uncertain_visible else 'Measured diffuse confidence (no legacy mask)'
for i,(label,im) in enumerate([('Continuous fallback',base),('Physical visible-surface pigment + continuation',new),(confidence_label,confidence_image)]):
    sheet.paste(Image.fromarray(im).convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(i*512,38));draw.text((i*512+10,12),label,fill='white')
sheet.save(out/'atlas-comparison.png')
legacy=np.clip(np.load(capture/'legacy-coverage.npy')[:,:,0],0,1)
record=dict(response=a.response,response_source_sha256=rm['source_sha256'],reference_sha256=sha(reference),
 geometry_inheritance_audits=audit_records,
 geometry_inheritance_root=dict(path=inheritance_path.relative_to(ROOT).as_posix(),sha256=sha(inheritance_path)),
 preserve_uncertain_visible_pigment=a.preserve_uncertain_visible,
 retain_visible_log_pigment_range=a.retain_visible_range,
 reliable_texels_that_default_fine_bounds_would_clip=truncation_fraction,
 projection_confidence_kind='Actual visible surface, preserving uncertain current pigment' if a.preserve_uncertain_visible else 'Diffuse inverse confidence',
 fallback=a.fallback,fallback_sha256=sha(fallback),capture=capture.relative_to(ROOT).as_posix(),
 actual_visibility_sha256=sha(capture/'visible.npy'),swatch=swatch.relative_to(ROOT).as_posix(),swatch_sha256=sha(swatch),
 output_sha256=sha(out/'albedo.png'),correction_bounds=[.67,1.5],inferred_linear_bounds=[.0001,.85],
 confidence_texels_above_half=int((coverage>.5).sum()),
 reliable_texels_with_legacy_below_98_percent=int(((weight>.5)&(legacy<.98)).sum()),
 continuation=dict(grid=[gw,gh],screen=a.screen,anchor=anchor_weight,iterations=iteration+1,max_final_update=maximum),
 body_rectangle=[x0,y0,x1,y1],body_padding_filled=True,alpha_button_and_cap_islands_preserved=True,
 method='Bounded local pigment feedback after subtracting measured black-BSDF response. Clipping, reflections, weak responses, inverse errors, geometry edges and cuts are downweighted. Actual atlas visibility projects observations onto the surface. Strongly screened periodic broad-color continuation and bounded observed/inferred fine grain replace the old projection-confidence boundary.',
 limits='An approximate inverse under inferred lighting. Interreflections, uncertain geometry and missing original material information can leave residual shading. Actual BSDF views and scope audits decide acceptance; this is not an emission beauty or reference composite.')
(out/'pigment.json').write_text(json.dumps(record,indent=2)+'\n',newline='\n')
print('VISIBLE_PIGMENT_PREPARED',json.dumps(record),flush=True)

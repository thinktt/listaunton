"""Infer continuous ring-wise wood tone while retaining bounded observed grain.

Unlike the rejected constant-color study, the broad color varies with actual
surface height. This is a material hypothesis, not recovered intrinsic albedo.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--amount',type=float,default=1)
p.add_argument('--out',default='build/bishop-mission/116-height-pigment')
p.add_argument('--bins',type=int,default=384)
p.add_argument('--angular',action='store_true',help='Fit a bounded first angular harmonic at every height.')
p.add_argument('--angular-limit',type=float,default=.35)
p.add_argument('--clean-boundary-detail',action='store_true',help='Remove old fine residuals near the projection-confidence boundary.')
a=p.parse_args();assert 0<=a.amount<=1 and a.bins>=64
out=ROOT/a.out;assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve());out.mkdir(parents=True,exist_ok=True)
source=ROOT/'history/bishop-mission-013/bishop-boxwood-albedo.png'
capture=ROOT/'build/bishop-mission/099-atlas-surface'
swatch=ROOT/'assets/bishop/materials/inferred-boxwood-source-01.png'
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
meta=json.loads((capture/'manifest.json').read_text())
assert sha(ROOT/meta['source'])==meta['source_sha256']
inheritance=json.loads((ROOT/'docs/bishop-mission/iteration-013/validation/pigment-validation.json').read_text())
assert inheritance['source_sha256']==meta['source_sha256']
assert inheritance['model_sha256']==sha(ROOT/'history/bishop-mission-013/bishop-rebuilt.blend')
assert inheritance['geometry_uvs_material_graph_relief_camera_lights_world_and_render_path_preserved']
def log_rgb(path):
    rgb=np.array(Image.open(path).convert('RGB'),dtype=np.float32)/255
    return np.log(np.maximum(np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4),.0001))
old=np.array(Image.open(source).convert('RGBA'));log=log_rgb(source)
position=np.load(capture/'position.npy')[:,:,:3]
position=(position-meta['encode_offset'])/meta['encode_scale']*np.array(meta['encode_extent'])+np.array(meta['encode_min'])
height=position[:,:,2]
normal=np.load(capture/'normal.npy')[:,:,:3]*2-1
visible=np.load(capture/'visible.npy');valid=np.load(capture/'valid.npy')
coverage=np.clip(np.load(capture/'legacy-coverage.npy')[:,:,0],0,1)
yy,xx=np.indices(height.shape);h,w=height.shape
# Preserve button islands, caps, alpha and unused texels. Body atlas layout is
# documented in the existing material baker: u .01..99, v .01..70.
domain=valid&(xx>=int(.01*w))&(xx<=int(.99*w))&(yy>=int(.30*h))&(yy<=int(.99*h))
reliable=domain&visible&(coverage>.99)&((normal@np.array(meta['view_direction']))>.35)
broad=blur(log,24,2)
zmin,zmax=float(height[domain].min()),float(height[domain].max())
step=(zmax-zmin)/a.bins
bin_id=np.clip(((height-zmin)/step).astype(np.int32),0,a.bins-1)
centers=zmin+(np.arange(a.bins)+.5)*step
tones=np.zeros((a.bins,3));counts=np.zeros(a.bins,dtype=int)
angle=np.arctan2(position[:,:,0],-position[:,:,1])
angular=np.stack([np.cos(angle),np.sin(angle)],axis=2)
coefficients=np.zeros((a.bins,3,3))
for i in range(a.bins):
    selection=reliable&(bin_id==i);counts[i]=int(selection.sum())
    if counts[i]>=30:
        values=broad[selection];tones[i]=np.median(values,axis=0)
        if a.angular:
            xy=angular[selection]
            design=np.column_stack([np.ones(counts[i]),xy])
            ridge=np.diag([0,.04,.04])*counts[i]
            beta=np.linalg.solve(design.T@design+ridge,design.T@values)
            amplitude=np.linalg.norm(beta[1:],axis=0)
            beta[1:]*=np.minimum(1,a.angular_limit/np.maximum(amplitude,1e-9))
            beta[0]=np.median(values-xy@beta[1:],axis=0)
            coefficients[i]=beta
known=counts>=30;assert known.sum()>a.bins*.6
for c in range(3):tones[:,c]=np.interp(centers,centers[known],tones[known,c])
# Smooth along height only, never around an image-space projection boundary.
kernel=np.exp(-.5*(np.arange(-7,8)/2.5)**2);kernel/=kernel.sum()
for c in range(3):tones[:,c]=np.convolve(np.pad(tones[:,c],7,mode='edge'),kernel,mode='valid')
ring=np.stack([np.interp(height,centers,tones[:,c]) for c in range(3)],axis=2)
if a.angular:
    for j in range(3):
        for c in range(3):
            coefficients[:,j,c]=np.interp(centers,centers[known],coefficients[known,j,c])
            coefficients[:,j,c]=np.convolve(np.pad(coefficients[:,j,c],7,mode='edge'),kernel,mode='valid')
    ring=np.zeros_like(log,dtype=np.float64)
    for j in range(3):
        value=np.stack([np.interp(height,centers,coefficients[:,j,c]) for c in range(3)],axis=2)
        ring+=value*(1 if j==0 else angular[:,:,j-1,None])
measured=np.clip(log-broad,-.8,.4)
tile=log_rgb(swatch);generated=np.clip(tile-blur(tile,32,2),-.4,.4)
u=(xx/w-.01)/.98
sx=(.5-.49*np.cos(2*np.pi*u))*(tile.shape[1]-1);sy=yy/(h-1)*(tile.shape[0]-1)
lx=np.floor(sx).astype(int);hx=np.minimum(lx+1,tile.shape[1]-1);fx=sx-lx
ly=np.floor(sy).astype(int);hy=np.minimum(ly+1,tile.shape[0]-1);fy=sy-ly
mapped=(generated[ly,lx]*(1-fx[:,:,None])+generated[ly,hx]*fx[:,:,None])*(1-fy[:,:,None])
mapped+=(generated[hy,lx]*(1-fx[:,:,None])+generated[hy,hx]*fx[:,:,None])*fy[:,:,None]
trust=np.clip((coverage-.90)/.10,0,1);trust=trust*trust*(3-2*trust)
if a.clean_boundary_detail:
    interior=blur((coverage>.995).astype(np.float32),16)>.999
    trust=blur(interior.astype(np.float32),12)
fine=measured*trust[:,:,None]+mapped*(1-trust[:,:,None])*.8
candidate=ring+fine
result=(1-a.amount)*log+a.amount*candidate
linear=np.exp(result);srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
new=old.copy();new[:,:,:3][domain]=np.uint8(np.rint(np.clip(srgb[domain],0,1)*255))
assert np.array_equal(new[~domain],old[~domain]) and np.array_equal(new[:,:,3],old[:,:,3])
Image.fromarray(new).save(out/'albedo.png')
sheet=Image.new('RGB',(1536,550),'#171b21');draw=ImageDraw.Draw(sheet)
for i,(label,pixels) in enumerate([('Accepted 013 atlas',old),('Height-continuous candidate '+str(a.amount),new)]):
    im=Image.fromarray(pixels).convert('RGB').resize((512,512),Image.Resampling.LANCZOS)
    sheet.paste(im,(512*i,38));draw.text((512*i+10,12),label,fill='white')
draw.text((1036,12),'Ring-wise broad color / physical height',fill='white')
tone=np.exp(tones);tone=np.where(tone<=.0031308,tone*12.92,1.055*tone**(1/2.4)-.055)
for c,color in enumerate(['#ff7766','#72dd88','#81aaff']):
    points=[(1040+float(v)*470,530-i/(a.bins-1)*480) for i,v in enumerate(tone[:,c])]
    draw.line(points,fill=color,width=2)
sheet.save(out/'atlas-comparison.png')
record=dict(source_atlas=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),
 source_model='history/bishop-mission-013/bishop-rebuilt.blend',source_model_sha256=sha(ROOT/'history/bishop-mission-013/bishop-rebuilt.blend'),
 capture=capture.relative_to(ROOT).as_posix(),capture_source_sha256=meta['source_sha256'],
 source_geometry_inheritance_verified=True,position_field_sha256=sha(capture/'position.npy'),
 swatch=swatch.relative_to(ROOT).as_posix(),swatch_sha256=sha(swatch),amount=a.amount,
 angular_first_harmonic=a.angular,angular_log_amplitude_limit=a.angular_limit,
 angular_coefficients=coefficients.tolist() if a.angular else None,
 clean_boundary_detail=a.clean_boundary_detail,
 height_bins=a.bins,height_range=[zmin,zmax],reliable_bins=int(known.sum()),reliable_texels=int(reliable.sum()),
 height_tones=[[float(z),int(n),rgb.tolist()] for z,n,rgb in zip(centers,counts,tone)],
 fine_log_range=[-.8,.4],changed_texels=int(np.any(old!=new,axis=2).sum()),
 alpha_button_caps_and_non_surface_texels_preserved=True,output_sha256=sha(out/'albedo.png'),
 method='Broad log-RGB from reliable actual visible texels, smoothed by physical height and extended around each ring. Optional bounded first angular harmonic retains gentle circumferential color changes. Bounded observed detail remains inside the trusted projection; optional erosion excludes its boundary residual. Zero-mean inferred grain supplies other areas. Original color can be blended by amount.',
 limits='Regional tone may still include residual illumination. A continuous color map is not proof of original pigment or grain. Fresh fixed/side/rear BSDF renders and independent scope checks are required.')
(out/'pigment.json').write_text(json.dumps(record,indent=2)+'\n',newline='\n')
print('HEIGHT_CONTINUOUS_PIGMENT',json.dumps({k:record[k] for k in ['amount','height_range','reliable_bins','reliable_texels','changed_texels','output_sha256']}),flush=True)

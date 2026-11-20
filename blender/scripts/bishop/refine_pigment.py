"""Confidence-weighted inverse pigment on real surfaces, retaining the BSDF and lights."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--response',required=True);p.add_argument('--variant',required=True)
p.add_argument('--lower',type=float,default=.25);p.add_argument('--upper',type=float,default=4)
p.add_argument('--weight',type=float,default=.9);p.add_argument('--samples',type=int,default=48)
p.add_argument('--feedback',help='Directory captured from a previous actual BSDF trial; one bounded correction.')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
directory=ROOT/a.response;manifest=json.loads((directory/'manifest.json').read_text())
source=ROOT/manifest['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert digest==manifest['source_sha256']
black=np.load(directory/'black-bsdf.npy')[:,:,:3]
white=np.load(directory/'white-bsdf.npy')[:,:,:3]
old=np.load(directory/'pigment.npy');srgb=np.load(directory/'reference-srgb.npy')
target=np.load(directory/'reference-linear.npy');inverse_error=np.load(directory/'inverse-roundtrip-error.npy')
response=np.maximum(white-black,.001)
inferred=np.maximum(target-black,0)/response
inferred=np.clip(inferred,np.maximum(old[:,:,:3]*a.lower,.0001),np.minimum(old[:,:,:3]*a.upper+.003,.85))
# Reflections, clipped channels, uncertain inverse pixels and geometry edges do
# not become new pigment. The surface attribute also protects hidden surfaces.
ratio=black.max(2)/np.maximum(target.max(2),.001)
weight=np.clip((.65-ratio)/.45,0,1)
weight*=np.clip((.995-srgb.max(2))/.05,0,1)
weight*=np.clip((response.mean(2)-.015)/.06,0,1)
weight*=np.clip((2/255-inverse_error)/(1/255),0,1)
interior=blur((old[:,:,3]>.995).astype(np.float32),radius=5)>.999
weight=blur(weight,radius=1)*interior*a.weight
inferred=np.nan_to_num(inferred,nan=.2,posinf=.85,neginf=.0001)
feedback_details=None
if a.feedback:
    feedback=ROOT/a.feedback;fm=json.loads((feedback/'manifest.json').read_text())
    source=ROOT/fm['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==fm['source_sha256']
    current=np.load(feedback/'actual-pigment.npy')[:,:,:3]
    actual=np.load(feedback/'linear-beauty.npy')[:,:,:3]
    correction=np.clip(np.maximum(target-black,0)/np.maximum(actual-black,.001),.67,1.5)
    correction=blur(correction,radius=2)
    inferred=np.clip(current*correction,.0001,.85)
    feedback_details={'source':fm['source'],'response_directory':a.feedback,'ratio_bounds':[.67,1.5],'blur_radius':2,'method':'One actual-render correction to the initial black/white response approximation.'}
coverage=np.load(directory/'coverage.npy')[:,:,0]
effective=weight*coverage
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
objects=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
mat=objects[0].data.materials[0];assert all(o.data.materials[0]==mat for o in objects)
ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns['Principled BSDF'];previous=bs.inputs['Base Color'].links[0].from_socket
assert s.camera.data.type=='ORTHO'
matrix=s.camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=s.render.resolution_x,y=s.render.resolution_y)@s.camera.matrix_world.inverted()
geom=ns.new('ShaderNodeNewGeometry');uv=ns.new('ShaderNodeCombineXYZ');uv.label='Fixed-camera pigment coordinates'
for row in range(2):
    dot=ns.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT'
    ls.new(geom.outputs['Position'],dot.inputs[0]);dot.inputs[1].default_value=tuple(.5*matrix[row][k] for k in range(3))
    add=ns.new('ShaderNodeMath');add.operation='ADD';ls.new(dot.outputs['Value'],add.inputs[0]);add.inputs[1].default_value=.5+.5*matrix[row][3]
    ls.new(add.outputs[0],uv.inputs[row])
out=ROOT/'build/bishop-mission'/a.variant;out.mkdir(parents=True,exist_ok=True)

def image_node(name,rgb,space):
    h,w=rgb.shape[:2];pixels=np.dstack([rgb,np.ones((h,w),dtype=np.float32)])
    im=bpy.data.images.new(name,width=w,height=h,alpha=False,float_buffer=True)
    im.colorspace_settings.name=space;im.pixels.foreach_set(pixels[::-1].copy().reshape(-1))
    im.filepath_raw=str(out/(name+'.exr'));im.file_format='OPEN_EXR';im.save();im.pack()
    node=ns.new('ShaderNodeTexImage');node.image=im;node.extension='EXTEND';ls.new(uv.outputs[0],node.inputs['Vector'])
    return node

color=image_node('Bishop measured pigment',inferred,'Linear Rec.709')
confidence=image_node('Bishop pigment confidence',np.repeat(weight[:,:,None],3,axis=2),'Non-Color')
cover=ns.new('ShaderNodeAttribute');cover.attribute_name='Pigment coverage'
factor=ns.new('ShaderNodeMath');factor.operation='MULTIPLY';ls.new(cover.outputs['Fac'],factor.inputs[0]);ls.new(confidence.outputs['Color'],factor.inputs[1])
mix=ns.new('ShaderNodeMixRGB');mix.name='Measured pigment blend';ls.new(factor.outputs[0],mix.inputs[0]);ls.new(previous,mix.inputs[1]);ls.new(color.outputs['Color'],mix.inputs[2]);ls.new(mix.outputs[0],bs.inputs['Base Color'])
assert ns['Material Output'].inputs['Surface'].links[0].from_node==bs
record={'source':source.relative_to(ROOT).as_posix(),'source_sha256':digest,'variant':a.variant,'response_directory':a.response,'feedback':feedback_details,
    'relative_pigment_bounds':[a.lower,a.upper],'max_weight':a.weight,'mean_effective_weight':float(effective[interior].mean()),
    'effective_weight_above_half_pixels':int((effective>.5).sum()),'reference_sha256':manifest['reference_sha256'],
    'targeted_metric':'Wood color and grain, with geometry, relief, BSDF and light rig fixed.',
    'view':manifest['view'],'look':manifest['look'],
    'method':'Measured black/white BSDF response with the verified matching display/view/Look transform. Reflections, clipping, failed inverse pixels and boundaries excluded. Visible-surface confidence preserves the hidden atlas.',
    'caveat':'Approximate inferred pigment under estimated lights. Interreflections make the response nonlinear and residual shading may remain.'}
s['bishop_measured_pigment']=json.dumps(record,sort_keys=True)
s.render.resolution_percentage=100;s.cycles.samples=a.samples;s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
record['saved_model_sha256']=hashlib.sha256((out/'bishop.blend').read_bytes()).hexdigest()
(out/'parameters.json').write_text(json.dumps(record,indent=2)+'\n')
np.save(out/'effective-weight.npy',effective)
print('BISHOP_MEASURED_PIGMENT_COMPLETE',json.dumps(record),flush=True)

"""Bounded pigment correction using current diffuse/specular measurements."""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--variant',default='116-measured-pigment');p.add_argument('--lower',type=float,default=.5);p.add_argument('--upper',type=float,default=2);p.add_argument('--weight',type=float,default=.8);p.add_argument('--feedback',default='');p.add_argument('--source',default='models/queen/queen-rebuilt.blend');p.add_argument('--response-directory',default='build/queen-mission/pigment-fit-011');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/args.source;directory=ROOT/args.response_directory;manifest=json.loads((directory/'manifest.json').read_text());digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==manifest['source_sha256']
black=np.load(directory/'black-bsdf.npy')[:,:,:3];white=np.load(directory/'white-bsdf.npy')[:,:,:3];old=np.load(directory/'pigment.npy');target=np.load(directory/'reference-linear.npy');srgb=np.load(directory/'reference-srgb.npy')
response=np.maximum(white-black,.001);inferred=np.maximum(target-black,0)/response
inferred=np.clip(inferred,np.maximum(old[:,:,:3]*args.lower,.0001),np.minimum(old[:,:,:3]*args.upper+.003,.85))
ratio=black.max(2)/np.maximum(target.max(2),.001)
weight=np.clip((.6-ratio)/.4,0,1)*np.clip((.35-srgb.min(2))/.2,0,1)
weight*=np.clip((response.mean(2)-.015)/.06,0,1)
interior=blur((old[:,:,3]>.995).astype(np.float32),r=5,passes=1)>.999
weight=blur(weight,r=1,passes=1)*interior*args.weight
feedback_details=None
if args.feedback:
 feedback=ROOT/'build/queen-mission'/args.feedback
 source=feedback/'queen.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
 feedback_manifest=feedback/'feedback-manifest.json'
 assert json.loads(feedback_manifest.read_text())['source_sha256']==digest
 current=np.load(feedback/'actual-pigment.npy')[:,:,:3];actual=np.load(feedback/'linear-beauty.npy')[:,:,:3]
 correction=np.clip(np.maximum(target-black,0)/np.maximum(actual-black,.001),.67,1.5)
 correction=blur(correction,r=2,passes=1)
 inferred=np.clip(current*correction,.0001,.85)
 feedback_details={'source_variant':args.feedback,'correction_bounds':[.67,1.5],'correction_blur_radius':2,'method':'One measured actual-BSDF correction after the black/white approximation; existing confidence excludes strong reflections.'}
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);mat=obj.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links;b=nodes.get('Principled BSDF');previous=b.inputs['Base Color'].links[0].from_socket
assert s.camera.data.type=='ORTHO';graph=bpy.context.evaluated_depsgraph_get();matrix=s.camera.calc_matrix_camera(graph,x=s.render.resolution_x,y=s.render.resolution_y)@s.camera.matrix_world.inverted()
geom=nodes.new('ShaderNodeNewGeometry');uv=nodes.new('ShaderNodeCombineXYZ');uv.label='Fixed reference-camera pigment coordinates'
for row in range(2):
 dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';links.new(geom.outputs['Position'],dot.inputs[0]);dot.inputs[1].default_value=tuple(.5*matrix[row][k] for k in range(3));add=nodes.new('ShaderNodeMath');add.operation='ADD';links.new(dot.outputs['Value'],add.inputs[0]);add.inputs[1].default_value=.5+.5*matrix[row][3];links.new(add.outputs[0],uv.inputs[row])
out=ROOT/'build/queen-mission'/args.variant;out.mkdir(exist_ok=True,parents=True)
def image_node(name,rgb,space):
 h,w=rgb.shape[:2];a=np.dstack([rgb,np.ones((h,w))]).astype(np.float32);im=bpy.data.images.new(name,width=w,height=h,alpha=False,float_buffer=True);im.colorspace_settings.name=space;im.pixels.foreach_set(a[::-1].copy().reshape(-1));im.filepath_raw=str(out/(name+'.exr'));im.file_format='OPEN_EXR';im.save();im.pack();n=nodes.new('ShaderNodeTexImage');n.image=im;n.extension='EXTEND';links.new(uv.outputs[0],n.inputs['Vector']);return n
pigment=image_node('Measured pigment',inferred,'Linear Rec.709');confidence=image_node('Measured pigment confidence',np.repeat(weight[:,:,None],3,axis=2),'Non-Color');coverage=nodes.new('ShaderNodeAttribute');coverage.attribute_name='Inferred pigment coverage';factor=nodes.new('ShaderNodeMath');factor.operation='MULTIPLY';links.new(coverage.outputs['Fac'],factor.inputs[0]);links.new(confidence.outputs['Color'],factor.inputs[1]);mix=nodes.new('ShaderNodeMixRGB');links.new(factor.outputs[0],mix.inputs[0]);links.new(previous,mix.inputs[1]);links.new(pigment.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],b.inputs['Base Color'])
output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');assert output.inputs['Surface'].links[0].from_node==b
cfg=json.loads(s['mission_material_config']);cfg['variant']=out.name;cfg['measured_pigment']={'source_sha256':digest,'response_directory':directory.relative_to(ROOT).as_posix(),'bounds':[args.lower,args.upper],'max_weight':args.weight,'mean_weight':float(weight[interior].mean()),'confidence_above_half_pixels':int((weight>.5).sum()),'projection':'Fixed world-space orthographic camera; original visible-surface coverage; hidden surfaces keep the accepted atlas','method':'(reference-linear minus measured black BSDF) / measured white-minus-black response; exclude strong reflections and boundary pixels. Packed pigment/confidence are separate; actual BSDF/normal/roughness/lights are retained.','caveat':'Approximate inverse pigment under inferred geometry and lighting; residual shading can remain.'};cfg['measured_pigment']['feedback']=feedback_details;s['mission_material_config']=json.dumps(cfg);s['mission_variant']=out.name
s.cycles.samples=128;s.cycles.use_denoising=True;s.render.use_persistent_data=True;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2));print('MEASURED_PIGMENT_DONE',flush=True)

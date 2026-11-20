"""Infer rook pigment from black/white BSDF response, preserving live lighting."""
from pathlib import Path
import sys,json,hashlib,math
import bpy,numpy as np,PyOpenColorIO as ocio
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'build/rook-mission/001-procedural-baseline/rook.blend'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
separate='--separate-lights' in args
variant='003-separated-light-pigment' if separate else '002-inverse-pigment'
out=ROOT/'build/rook-mission'/variant
out.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(im):
    w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a)
    return a.reshape(h,w,4)[::-1].copy()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;gpu(s)
if separate:
    for ob in s.objects:
        if ob.type=='LIGHT':ob.visible_glossy=False
    # Real small glossy emitters replace the cavity-filling softbox reflections.
    for name,position,power,size,target in [
        ('Rook upper edge',(-3,-4,7),180,.45,(0,0,2.5)),
        ('Rook front crescent',(0,-5,3),45,.18,(0,0,.6)),
        ('Rook rim edge',(1,0,7),90,.35,(0,0,2.6))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
        ob=bpy.data.objects.new(name,data);s.collection.objects.link(ob);ob.location=position
        ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();ob.visible_diffuse=False
    s.world.node_tree.nodes['Background'].inputs[1].default_value=.12
s.render.resolution_percentage=100;s.cycles.samples=64;s.render.use_persistent_data=True
assert s.view_settings.view_transform=='AgX' and s.view_settings.look=='None'
body=next(o for o in s.objects if o.type=='MESH' and not o.hide_render)
mat=body.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF']
previous=bs.inputs['Base Color'].links[0].from_socket
for link in list(bs.inputs['Base Color'].links):l.remove(link)
responses={}
for label,value in [('black',0),('white',1)]:
    bs.inputs['Base Color'].default_value=(value,value,value,1)
    s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32'
    s.render.filepath=str(out/(label+'.exr'));bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(s.render.filepath,check_existing=False);responses[label]=pixels(im);bpy.data.images.remove(im)
refpath=ROOT/'assets/rook/ref.png';ref=bpy.data.images.load(str(refpath),check_existing=False)
raw=pixels(ref);display=raw[:,:,:3].copy()
assert raw.shape==responses['black'].shape
config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
tr=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX');tr.setDirection(ocio.TRANSFORM_DIR_INVERSE)
target=display.copy();config.getProcessor(tr).getDefaultCPUProcessor().applyRGB(target)
black=responses['black'];white=responses['white'];response=np.maximum(white[:,:,:3]-black[:,:,:3],0)
pigment=np.clip((target-black[:,:,:3])/np.maximum(response,.008),.002,.75)
lum=np.array([.2126,.7152,.0722],np.float32)
confidence=np.clip((response@lum-.025)/.12,0,1)
confidence*=np.clip((.8-(black[:,:,:3]@lum)/np.maximum(target@lum,.008))/.5,0,1)
confidence*=np.clip((.46-display.min(2))/.22,0,1)
confidence*=np.clip((raw[:,:,3]-.8)/.1,0,1)*(white[:,:,3]>.99)
confidence*=np.clip((display.max(2)-.04)/.08,0,1)
def float_image(name,rgb):
    h,w=rgb.shape[:2];a=np.dstack([rgb,np.ones((h,w),np.float32)]).astype(np.float32)
    im=bpy.data.images.new(name,width=w,height=h,float_buffer=True,alpha=False)
    im.colorspace_settings.name='Linear Rec.709';im.pixels.foreach_set(a[::-1].copy().reshape(-1))
    im.file_format='OPEN_EXR';im.filepath_raw=str(out/(name+'.exr'));im.save();im.pack();return im
color=float_image('rook-inferred-pigment',pigment)
weight_image=float_image('rook-confidence',np.repeat(confidence[:,:,None],3,2))
# Fixed affine projection in OBJECT coordinates: the texture stays attached to
# the actual carved object when the inspection camera rotates.
coord=n.new('ShaderNodeTexCoord');combine=n.new('ShaderNodeCombineXYZ')
p0=world_to_camera_view(s,s.camera,Vector((0,0,0)))
coeff=[]
for dim in [0,1]:
    vec=[]
    for axis in range(3):
        p=Vector((0,0,0));p[axis]=1
        vec.append(world_to_camera_view(s,s.camera,p)[dim]-p0[dim])
    dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=vec;l.new(coord.outputs['Object'],dot.inputs[0])
    add=n.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=p0[dim];l.new(dot.outputs['Value'],add.inputs[0]);l.new(add.outputs[0],combine.inputs[dim]);coeff.append(vec+[p0[dim]])
tex=n.new('ShaderNodeTexImage');tex.name='Rook inferred diffuse pigment';tex.image=color;tex.extension='EXTEND';l.new(combine.outputs[0],tex.inputs[0])
conf=n.new('ShaderNodeTexImage');conf.name='Rook pigment confidence';conf.image=weight_image;conf.extension='EXTEND';l.new(combine.outputs[0],conf.inputs[0])
geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT'
view=s.camera.matrix_world.to_3x3()@Vector((0,0,1));dot.inputs[1].default_value=view;l.new(geo.outputs['Normal'],dot.inputs[0])
gate=n.new('ShaderNodeMapRange');gate.inputs['From Min'].default_value=.08;gate.inputs['From Max'].default_value=.35;gate.clamp=True;l.new(dot.outputs['Value'],gate.inputs['Value'])
weight=n.new('ShaderNodeMath');weight.operation='MULTIPLY';l.new(gate.outputs[0],weight.inputs[0]);l.new(conf.outputs['Color'],weight.inputs[1])
mix=n.new('ShaderNodeMixRGB');mix.name='Rook bounded reference pigment';l.new(weight.outputs[0],mix.inputs[0]);l.new(previous,mix.inputs[1]);l.new(tex.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
s['rook_pigment_method']='Approximate inverse real-BSDF response, bounded confidence, procedural unseen surfaces; live lights and specular.'
s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.ortho_scale=4.5;cam.location=(0,-12,1.4);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_percentage=60;s.render.filepath=str(out/'side.png');bpy.ops.render.render(write_still=True)
(out/'report.json').write_text(json.dumps({'source_sha256':sha(source),'reference_sha256':sha(refpath),'model_sha256':sha(out/'rook.blend'),'projection':coeff,'confidence_mean':float(confidence[white[:,:,3]>.99].mean()),'limitation':'Single-view approximate inversion cannot uniquely recover pigment; high-reflection or low-response areas retain procedural prior. Not accepted.'},indent=2))
print('ROOK_INVERSE_TRIAL_COMPLETE')

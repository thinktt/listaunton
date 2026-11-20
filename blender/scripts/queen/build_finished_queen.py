"""Build the 54-degree queen, procedural walnut material and studio renders.

Start from the saved 54-degree study so the original accepted sculpture and
alternative projection study remain recoverable in Git. Run fit_54_finish.py
first. The saved camera is the one used for the overlay and viewer export.
"""
from pathlib import Path
import json, math, sys
import bpy
import numpy as np
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/queen'
fit=json.loads((OUT/'finish-fit.json').read_text())
source=ROOT/'models/queen-projections/queen-54.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
n=192
co=np.empty(len(obj.data.vertices)*3,dtype=np.float32)
obj.data.vertices.foreach_get('co',co);co=co.reshape((-1,n,3)).astype(float)
mean_z=co[:,:,2].mean(axis=1)
p=np.array(fit['parameters'])
radial=np.interp(mean_z,fit['radial_knots'],p[:14])
vertical=np.interp(mean_z,fit['vertical_knots'],np.r_[0,p[14:20],0])
radius=np.linalg.norm(co[:,:,:2],axis=2).mean(axis=1)
cap=2.0734214782714844/2
new_z=mean_z*fit['height_multiplier']+vertical
radial=np.where(new_z<new_z.max()*.25,np.minimum(1+radial,cap/np.maximum(radius,1e-8))-1,radial)
co[:,:,:2]*=(1+radial[:,None,None])
co[:,:,2]=co[:,:,2]*fit['height_multiplier']+vertical[:,None]
obj.data.vertices.foreach_set('co',co.astype(np.float32).reshape(-1));obj.data.update()
for modifier in obj.modifiers:
    if modifier.type=='SUBSURF':modifier.levels=modifier.render_levels=2

def make_wood():
    mat=bpy.data.materials.new('Walnut - procedural polished grain');mat.use_nodes=True
    mat.diffuse_color=(.15,.047,.015,1)
    tree=mat.node_tree;nodes=tree.nodes;links=tree.links
    bs=nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.32
    bs.inputs['Coat Weight'].default_value=.10
    bs.inputs['Coat Roughness'].default_value=.30
    bs.inputs['IOR'].default_value=1.48
    tex=nodes.new('ShaderNodeTexCoord');tex.label='Continuous local wood coordinates'
    mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(2.3,2.3,.32)
    links.new(tex.outputs['Object'],mapping.inputs[0])
    noise=nodes.new('ShaderNodeTexNoise');noise.noise_dimensions='3D'
    noise.inputs['Scale'].default_value=3.0;noise.inputs['Detail'].default_value=4
    noise.inputs['Roughness'].default_value=.65
    links.new(mapping.outputs['Vector'],noise.inputs['Vector'])
    ramp=nodes.new('ShaderNodeValToRGB');ramp.label='Warm reddish walnut'
    ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[0].color=(.045,.009,.002,1)
    ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(.16,.045,.010,1)
    mid=ramp.color_ramp.elements.new(.48);mid.color=(.090,.021,.0048,1)
    # Long distorted fibers run through the wood, with finer growth bands.
    wave=nodes.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction='Z'
    wave.inputs['Scale'].default_value=15;wave.inputs['Distortion'].default_value=7
    wave.inputs['Detail Scale'].default_value=1.2;wave.inputs['Detail'].default_value=3
    links.new(tex.outputs['Object'],wave.inputs['Vector'])
    mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[0].default_value=.05
    links.new(noise.outputs['Fac'],mix.inputs[1]);links.new(wave.outputs['Color'],mix.inputs[2])
    fine=nodes.new('ShaderNodeTexNoise');fine.noise_dimensions='3D'
    fine.inputs['Scale'].default_value=15;fine.inputs['Detail'].default_value=3;fine.inputs['Roughness'].default_value=.7
    links.new(mapping.outputs['Vector'],fine.inputs['Vector'])
    detail=nodes.new('ShaderNodeMixRGB');detail.blend_type='MIX';detail.inputs[0].default_value=.20
    links.new(mix.outputs['Color'],detail.inputs[1]);links.new(fine.outputs['Fac'],detail.inputs[2])
    links.new(detail.outputs['Color'],ramp.inputs['Fac'])
    image=bpy.data.images.load(str(OUT/'walnut-albedo.png'),check_existing=True)
    image.pack();image.filepath='//../../assets/queen/walnut-albedo.png'
    grain=nodes.new('ShaderNodeTexImage');grain.label='Generated wood-grain albedo';grain.image=image
    grain.projection='BOX';grain.projection_blend=.35;grain.extension='REPEAT'
    grain_mapping=nodes.new('ShaderNodeVectorMath');grain_mapping.operation='SCALE';grain_mapping.inputs[3].default_value=.85
    links.new(tex.outputs['Object'],grain_mapping.inputs[0]);links.new(grain_mapping.outputs['Vector'],grain.inputs['Vector'])
    colors=nodes.new('ShaderNodeMixRGB');colors.blend_type='MIX';colors.inputs[0].default_value=.78
    links.new(ramp.outputs['Color'],colors.inputs[1]);links.new(grain.outputs['Color'],colors.inputs[2])
    links.new(colors.outputs['Color'],bs.inputs['Base Color'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.06;bump.inputs['Distance'].default_value=.006
    links.new(grain.outputs['Color'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    return mat

wood=make_wood();obj.data.materials.clear();obj.data.materials.append(wood)
# Control broad studio reflections while keeping the carved recesses dark.
for name,energy in [('Key - upper left',550),('Front right soft highlight',140),('Gentle rim',260)]:
    light=bpy.data.objects.get(name)
    if light and light.type=='LIGHT':light.data.energy=energy
if scene.world and scene.world.use_nodes:
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.10
cam=scene.camera;e=math.radians(54);s=fit['camera_scale'];w=1254
target=(fit['camera_floor']-w/2)/(s*math.cos(e))
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=w/s;cam.data.shift_x=(w/2-fit['camera_cx'])/w;cam.data.shift_y=0;cam.data.sensor_fit='AUTO'
cam.location=(0,-12*math.cos(e),target+12*math.sin(e));aim(cam,(0,0,target))
scene.render.resolution_x=w;scene.render.resolution_y=w;scene.render.resolution_percentage=100
scene.render.pixel_aspect_x=scene.render.pixel_aspect_y=1
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.device='CPU'
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX'
scene['projection_elevation']=54.0
scene['reconstruction']='54-degree assumed camera, owner-selected 83.4% queen/king side-view height, procedural polished walnut.'
sys.path.insert(0,str(Path(__file__).parent))
from write_finished_landmarks import write as write_landmarks
write_landmarks(scene,obj,fit)
scene.render.filepath='//../../assets/queen/queen-brown.png'
bpy.context.preferences.filepaths.save_version=0
model=ROOT/'models/queen/queen-rebuilt.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(model))
scene.render.filepath=str(OUT/'queen-brown.png')

try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    gpu=False
    for device in prefs.devices:
        device.use=device.type=='OPTIX';gpu |= device.use
    if gpu:scene.cycles.device='GPU'
except Exception as e:print('CPU render fallback',e)
if '--draft' in sys.argv:scene.cycles.samples=16
bpy.ops.render.render(write_still=True)
clay=bpy.data.materials.new('Inspection clay');clay.use_nodes=True
clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.24,.26,.29,1)
clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.32
obj.data.materials[0]=clay
scene.render.filepath=str(OUT/'queen-matched.png');bpy.ops.render.render(write_still=True)
cam.data.shift_x=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=6.6
cam.location=(0,-16,2.55);aim(cam,(0,0,2.55))
scene.render.resolution_x=600;scene.render.resolution_y=900
scene.render.filepath=str(OUT/'queen-finished-profile.png');bpy.ops.render.render(write_still=True)
print('QUEEN_FINISH_RENDERED',flush=True)

"""Create a new queen mesh from side-inspired controls and a 54° source fit.

This starts from an empty Blender scene; it does not open or deform a previous
queen model. The packed wood image is reused as a material, not as geometry.
"""
from pathlib import Path
import json,math,sys
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'assets/queen'
sys.path.insert(0,str(Path(__file__).parent))
from scratch_profile import PROFILE,CROWN,controls,apply_fit
fit=json.loads((OUT/'scratch-fit.json').read_text())
points=apply_fit(controls(192),fit);segments=points.shape[1];rings=points.shape[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
collection=bpy.data.collections.new('Queen - fresh side-inspired reconstruction');scene.collection.children.link(collection)
vertices=points.reshape(-1,3).tolist();faces=[]
for j in range(rings-1):
 for i in range(segments):
  k=(i+1)%segments;faces.append((j*segments+i,j*segments+k,(j+1)*segments+k,(j+1)*segments+i))
faces.extend([tuple(reversed(range(segments))),tuple((rings-1)*segments+i for i in range(segments))])
mesh=bpy.data.meshes.new('Queen side-inspired control mesh');mesh.from_pydata(vertices,[],faces);mesh.update()
obj=bpy.data.objects.new('01 Queen - continuous body and splash crown',mesh);collection.objects.link(obj)
for f in mesh.polygons:f.use_smooth=True
sub=obj.modifiers.new('Smooth carving','SUBSURF');sub.levels=2;sub.render_levels=2
obj['ring_segments']=segments;obj['body_preserved_ring_count']=len(PROFILE);obj['finial_first_ring']=len(PROFILE)+13
scene['continuous_crown']=True;scene['crown_tip_count']=8
scene['reconstruction']='Fresh side-inspired geometry fitted to the original Lichess black queen from an assumed 54° camera.'

material=bpy.data.materials.new('Polished walnut - generated wood grain');material.diffuse_color=(.12,.035,.009,1);material.use_nodes=True
tree=material.node_tree;nodes=tree.nodes;links=tree.links;bs=nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.29;bs.inputs['Coat Weight'].default_value=.11;bs.inputs['Coat Roughness'].default_value=.28
tex=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=.85
links.new(tex.outputs['Object'],mapping.inputs[0])
image=bpy.data.images.load(str(OUT/'walnut-albedo.png'));image.pack();image.filepath='//../../assets/queen/walnut-albedo.png'
grain=nodes.new('ShaderNodeTexImage');grain.image=image;grain.projection='BOX';grain.projection_blend=.35;grain.extension='REPEAT'
links.new(mapping.outputs['Vector'],grain.inputs['Vector']);links.new(grain.outputs['Color'],bs.inputs['Base Color'])
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.07;bump.inputs['Distance'].default_value=.006
links.new(grain.outputs['Color'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal']);mesh.materials.append(material)
world=bpy.data.worlds.new('Dark studio');world.use_nodes=True;scene.world=world
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.14,.14,.14,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.10
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
 light=bpy.data.objects.new(name,data);scene.collection.objects.link(light);light.location=loc;aim(light,(0,0,2));return light
area('Key upper left',(-3,-4,8),500,1.3)
area('Front right soft highlight',(3,-4,5),110,.85)
area('Gentle rim',(2,3,7),220,2.0)
camera=bpy.data.cameras.new('Aligned 54-degree camera');cam=bpy.data.objects.new(camera.name,camera);scene.collection.objects.link(cam);scene.camera=cam
e=math.radians(54);s=fit['camera_scale'];w=1254
target=(fit['camera_floor']-w/2)/(s*math.cos(e))
camera.type='ORTHO';camera.ortho_scale=w/s;camera.shift_x=(w/2-fit['camera_cx'])/w;camera.sensor_fit='AUTO'
cam.location=(0,-12*math.cos(e),target+12*math.sin(e));aim(cam,(0,0,target))
reference=bpy.data.images.load(str(OUT/'reference.png'));reference.pack()
bg=camera.background_images.new();bg.image=reference;bg.alpha=.5;bg.display_depth='FRONT';bg.frame_method='FIT';camera.show_background_images=True
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.cycles.device='CPU'
scene.render.resolution_x=w;scene.render.resolution_y=w;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='AgX';scene['projection_elevation']=54.0
scene.render.filepath='//../../assets/queen/queen-brown.png'
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
for screen in bpy.data.screens:
 for area_ in screen.areas:
  if area_.type=='VIEW_3D':
   space=area_.spaces.active;space.region_3d.view_location=(0,0,2);space.region_3d.view_distance=8;space.region_3d.view_perspective='CAMERA';space.shading.type='SOLID';space.overlay.show_overlays=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models/queen/queen-rebuilt.blend'))
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 gpu=False
 for device in prefs.devices:device.use=device.type=='OPTIX';gpu|=device.use
 if gpu:scene.cycles.device='GPU'
except Exception as error:print('CPU fallback:',error)
if '--draft' in sys.argv:scene.cycles.samples=8
scene.render.filepath=str(OUT/'queen-brown.png');bpy.ops.render.render(write_still=True)
clay=bpy.data.materials.new('Neutral clay');clay.use_nodes=True
clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.24,.26,.29,1)
clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.32
mesh.materials[0]=clay
scene.render.filepath=str(OUT/'queen-matched.png');bpy.ops.render.render(write_still=True)
# Common straight side view; no side-image-based camera distortion or warping.
cam.location=(0,-16,2.0);aim(cam,(0,0,2.0));camera.shift_x=0;camera.shift_y=0;camera.sensor_fit='VERTICAL';camera.ortho_scale=5.15
scene.render.resolution_x=600;scene.render.resolution_y=900
scene.render.filepath=str(OUT/'queen-finished-profile.png');bpy.ops.render.render(write_still=True)
if '--quick' not in sys.argv:
 mesh.materials[0]=material;scene.render.filepath=str(OUT/'queen-wood-profile.png');bpy.ops.render.render(write_still=True)
print('FRESH_QUEEN_RENDERED',flush=True)

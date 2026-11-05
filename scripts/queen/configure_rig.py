"""Configure a reproducible area/spot rig, including Cycles ray visibility."""
import math
import bpy
from mathutils import Vector

def configure(scene, settings):
 for light in list(scene.objects):
  if light.type=='LIGHT':bpy.data.objects.remove(light,do_unlink=True)
 for spec in settings['lights']:
  kind=spec.get('type','AREA');data=bpy.data.lights.new(spec['name'],kind);data.energy=spec['energy'];data.diffuse_factor=spec.get('diffuse_factor',1);data.specular_factor=spec.get('specular_factor',1)
  if kind=='AREA':
   data.shape=spec.get('shape','DISK');data.size=spec['size']
   if data.shape=='RECTANGLE':data.size_y=spec['size_y']
  elif kind=='SPOT':data.shadow_soft_size=spec['size']/2;data.spot_size=math.radians(spec['spot_degrees']);data.spot_blend=spec.get('spot_blend',.3)
  else:raise ValueError(kind)
  data.color=spec.get('color',[1,1,1])
  if 'spread_degrees' in spec:data.spread=math.radians(spec['spread_degrees'])
  light=bpy.data.objects.new(spec['name'],data);scene.collection.objects.link(light);light.location=spec['position'];light.rotation_euler=(Vector(spec.get('target',[0,0,2.3]))-light.location).to_track_quat('-Z','Y').to_euler()
  if settings.get('cycles_ray_visibility'):
   assert spec.get('diffuse_factor',1) in (0,1) and spec.get('specular_factor',1) in (0,1)
   light.visible_diffuse=bool(spec.get('diffuse_factor',1));light.visible_glossy=bool(spec.get('specular_factor',1))
 scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=settings['world']

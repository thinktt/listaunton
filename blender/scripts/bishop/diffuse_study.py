"""Temporary diffuse-environment basis for joint bishop material/light fitting."""
import math
import bpy
from mathutils import Vector

def configure(scene,spec):
    assert not any(o.name.startswith('Study diffuse ') for o in scene.objects)
    prior=[]
    for ob in scene.objects:
        if ob.type=='LIGHT' and ob.visible_diffuse:
            prior.append(ob.name);ob.visible_diffuse=False
    tree=scene.world.node_tree;output=next(n for n in tree.nodes if n.type=='OUTPUT_WORLD')
    old=output.inputs['Surface'].links[0].from_socket
    path=tree.nodes.new('ShaderNodeLightPath');path.name='Study diffuse ray'
    dark=tree.nodes.new('ShaderNodeBackground');dark.name='Study unlit diffuse environment';dark.inputs['Strength'].default_value=0
    mix=tree.nodes.new('ShaderNodeMixShader');mix.name='Study preserve glossy environment'
    tree.links.new(path.outputs['Is Diffuse Ray'],mix.inputs[0]);tree.links.new(old,mix.inputs[1]);tree.links.new(dark.outputs[0],mix.inputs[2]);tree.links.new(mix.outputs[0],output.inputs['Surface'])
    lights=[]
    for i,entry in enumerate(spec['directions']):
        elev,az=map(math.radians,entry)
        direction=Vector((math.sin(az)*math.cos(elev),-math.cos(az)*math.cos(elev),math.sin(elev)))
        data=bpy.data.lights.new(f'Study diffuse {i:02d}','SUN');data.energy=0;data.angle=math.radians(spec['sun_angle_degrees'])
        ob=bpy.data.objects.new(data.name,data);scene.collection.objects.link(ob)
        ob.location=Vector((0,0,2.3))+10*direction;ob.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
        ob.visible_diffuse=True;ob.visible_glossy=False;lights.append(ob)
    return lights,prior

"""Unsaved neutral geometry views under broad, unfitted white illumination."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',default='models/bishop/bishop-rebuilt.blend')
p.add_argument('--out',default='build/bishop-mission/148-internal-audit')
p.add_argument('--views',nargs='+',choices=['fixed','side','head'],default=['fixed','side'])
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;cam=s.camera
saved_camera={'matrix':[list(row) for row in cam.matrix_world],'ortho_scale':cam.data.ortho_scale,'shift_x':cam.data.shift_x,'shift_y':cam.data.shift_y}
for ob in s.objects:
    if ob.type=='LIGHT':ob.hide_render=True
mat=bpy.data.materials.new('Unfitted geometry diagnostic');mat.use_nodes=True
bs=mat.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(.40,.40,.40,1)
bs.inputs['Roughness'].default_value=.65;bs.inputs['Specular IOR Level'].default_value=.25
for ob in s.objects:
    if ob.type=='MESH' and not ob.hide_render:
        ob.data.materials.clear();ob.data.materials.append(mat)
world=bpy.data.worlds.new('Unfitted geometry world');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.10;s.world=world
lights=[]
for name,location,power,size in [('Key',(-4,-6,8),850,5),('Fill',(5,-1,5),500,4),('Rim',(0,4,6),700,4)]:
    data=bpy.data.lights.new('Geometry '+name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(data.name,data);s.collection.objects.link(ob);ob.location=location
    ob.rotation_euler=(Vector((0,0,2.2))-ob.location).to_track_quat('-Z','Y').to_euler()
    lights.append({'name':name,'location':location,'power':power,'size':size})
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.cycles.samples=64;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
views={}
for view in a.views:
    if view=='fixed':
        from mathutils import Matrix
        cam.matrix_world=Matrix(saved_camera['matrix']);cam.data.ortho_scale=saved_camera['ortho_scale']
        cam.data.shift_x=saved_camera['shift_x'];cam.data.shift_y=saved_camera['shift_y']
        s.render.resolution_x=s.render.resolution_y=1254
    else:
        target=Vector((0,0,2.32 if view=='side' else 3.9));cam.location=target+Vector((0,-10,0))
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.ortho_scale=4.98 if view=='side' else 1.75;cam.data.shift_x=cam.data.shift_y=0
        s.render.resolution_x=s.render.resolution_y=1000
    bpy.context.view_layer.update();s.render.filepath=str(out/(view+'.png'));bpy.ops.render.render(write_still=True)
    views[view]={'matrix':[list(row) for row in cam.matrix_world],'ortho_scale':cam.data.ortho_scale,'shift_x':cam.data.shift_x,'shift_y':cam.data.shift_y}
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'studio.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'source_unchanged':True,'saved_camera':saved_camera,'lights':lights,'views':views,
    'note':'Diagnostic only. Unfitted broad white lights and neutral BSDF remove image-derived pigment, relief and localized reflector cues. The saved model, material, lights and camera are not changed.'},indent=2)+'\n')
print('GEOMETRY_STUDIO_COMPLETE',flush=True)

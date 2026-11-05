"""Measure the button's real BSDF response to each reflector; source stays unchanged."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
p.add_argument('--lighting-config');p.add_argument('--basis-energy',type=float,default=1000)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
names=['button reflection','Button second glint'];lamps=[bpy.data.objects[n] for n in names]
assert all(not lamp.visible_diffuse and lamp.visible_glossy for lamp in lamps)
lighting=json.loads((ROOT/a.lighting_config).read_text()) if a.lighting_config else None
if lighting:
    for spec in lighting['lights']:
        lamp=bpy.data.objects[spec['name']]
        for key in ['energy','color','size','size_y','shape']:
            if key in spec:setattr(lamp.data,key,spec[key])
        for key in ['location','rotation_euler']:
            if key in spec:setattr(lamp,key,spec[key])
original=[{'name':lamp.name,'energy':lamp.data.energy,'color':list(lamp.data.color),'size':lamp.data.size} for lamp in lamps]
for lamp in lamps:lamp.data.energy=0;lamp.data.color=(1,1,1)
s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=False
w,h=s.render.resolution_x,s.render.resolution_y
s.render.border_min_x=414/w;s.render.border_max_x=570/w;s.render.border_min_y=1-288/h;s.render.border_max_y=1-152/h
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
s.render.use_persistent_data=True;s.cycles.samples=96;s.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
def render(name):
    path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(path),check_existing=False);assert list(im.size)==[w,h]
    values=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1].copy();np.save(out/(name+'.npy'),values);bpy.data.images.remove(im)
    print('BISHOP_BUTTON_RESPONSE',name,flush=True)
render('base')
for index,lamp in enumerate(lamps):
    lamp.data.energy=a.basis_energy;render('reflector-'+str(index+1));lamp.data.energy=0
def emission(name,value):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear()
    e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(value,value,value,1)
    o=n.new('ShaderNodeOutputMaterial');l.new(e.outputs[0],o.inputs['Surface']);return mat
black=emission('Diagnostic black',0);white=emission('Diagnostic button ID',1)
for ob in s.objects:
    if ob.type=='MESH' and not ob.hide_render:
        ob.data.materials.clear();ob.data.materials.append(white if 'finial' in ob.name else black)
s.cycles.samples=16;render('mask')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'original_lights':original,'lighting_config':lighting,'basis_energy':a.basis_energy,'basis_color':[1,1,1],'reference_camera_unchanged':True,'render_border_pixels':[414,152,570,288],'samples':96,'source_unchanged':True,'purpose':'Linear physical reflector response for fitting actual light energies/colors; no reference used as an emission beauty image.'},indent=2)+'\n')

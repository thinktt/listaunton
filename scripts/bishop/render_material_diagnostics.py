"""Separate pigment, bump and lighting in a rear view; never save diagnostic shaders."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
target=Vector((0,0,2.1));e=math.radians(28);az=math.radians(120);cam=s.camera
cam.location=target+Vector((10*math.sin(az)*math.cos(e),-10*math.cos(az)*math.cos(e),10*math.sin(e)))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.scale=(1,1,1);cam.data.shift_x=0;cam.data.shift_y=0;cam.data.ortho_scale=6
s.render.resolution_x=s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.use_border=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.cycles.samples=64;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=True;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
mats={m for ob in s.objects if ob.type=='MESH' and not ob.hide_render for m in ob.data.materials if m and m.use_nodes}
original_outputs={m:m.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_socket for m in mats}
def render(label):
    s.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True);print('MATERIAL_DIAGNOSTIC',label,flush=True)
render('actual-bsdf')
for mat in mats:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes['Principled BSDF'];em=nodes.new('ShaderNodeEmission')
    color=bs.inputs['Base Color']
    if color.is_linked:links.new(color.links[0].from_socket,em.inputs['Color'])
    else:em.inputs['Color'].default_value=color.default_value
    links.new(em.outputs[0],nodes['Material Output'].inputs['Surface'])
render('pigment-only-diagnostic')
for mat in mats:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;links.new(original_outputs[mat],nodes['Material Output'].inputs['Surface'])
    for node in nodes:
        if node.type=='BUMP':node.inputs['Strength'].default_value=0
render('no-relief-diagnostic')
for mat in mats:
    bs=mat.node_tree.nodes['Principled BSDF'];links=mat.node_tree.links
    for link in list(bs.inputs['Base Color'].links):links.remove(link)
    bs.inputs['Base Color'].default_value=(.2,.08,.015,1)
render('constant-pigment-no-relief-diagnostic')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'source_unchanged':True,'camera':'Same rear-oblique diagnostic: elevation 28, azimuth 120, scale 6, 768 square.',
 'samples':64,'adaptive_sampling':False,'diagnostics_only':True,'note':'Pigment emission is a measurement only; other views are real BSDF isolation renders. No diagnostic scene is saved or promoted.'},indent=2)+'\n')

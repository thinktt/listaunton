"""Isolate socket lighting, pigment and neutral shape without changing the source."""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh,set_material
parser=argparse.ArgumentParser();parser.add_argument('--source',default='models/queen/queen-rebuilt.blend');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);source=ROOT/args.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
assert digest=='358e327b4aa8022117af741f87dc2af835ae9bac266c3f16f42e559739987ed6'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;mat=editable_mesh(s).data.materials[0]
out=ROOT/'build/queen-mission/socket-inspection-013';out.mkdir(parents=True,exist_ok=True)
x1,y1,x2,y2=315,650,635,815;W=s.render.resolution_x;H=s.render.resolution_y
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=(x1+.01)/W;s.render.border_max_x=(x2+.01)/W
s.render.border_min_y=(H-y2+.01)/H;s.render.border_max_y=(H-y1+.01)/H
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
s.render.use_persistent_data=True;s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
def render(name):
    path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size;assert (w,h)==(x2-x1,y2-y1)
    a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im)
    np.save(out/(name+'.npy'),a.reshape(h,w,4)[::-1].copy())
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
    bpy.data.images['Render Result'].save_render(str(out/(name+'.png')),scene=s)
    s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32'
    print('SOCKET_DIAGNOSTIC',name,flush=True)
lights=[o for o in s.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in lights}
bg=s.world.node_tree.nodes['Background'];world=bg.inputs['Strength'].default_value
names=['Display fitted socket-left','Display fitted socket-left-precise','Display fitted socket-right']
render('actual')
for name in names:bpy.data.objects[name].data.energy=0
render('without-socket-lights')
for o in lights:o.data.energy=0
bg.inputs['Strength'].default_value=0
for name in names:
    bpy.data.objects[name].data.energy=powers[name];render(name.replace('Display fitted ',''));bpy.data.objects[name].data.energy=0
for o in lights:o.data.energy=powers[o.name]
bg.inputs['Strength'].default_value=world
ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF');output=next(n for n in ns if n.type=='OUTPUT_MATERIAL')
em=ns.new('ShaderNodeEmission');ls.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);ls.new(em.outputs[0],output.inputs['Surface']);render('pigment')
ls.new(bs.outputs['BSDF'],output.inputs['Surface'])
clay=bpy.data.materials.new('Socket shape inspection');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.24,.26,.29,1);bs.inputs['Roughness'].default_value=.32;set_material(s,clay);render('neutral')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source_sha256':digest,'source_unchanged':True,'crop':[x1,y1,x2,y2],'samples':256,'isolated_lights':names},indent=2)+'\n')
print('SOCKET_INSPECTION_DONE',flush=True)

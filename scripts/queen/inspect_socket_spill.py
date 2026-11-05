"""Measure every active light's socket contribution, without editing the model."""
from pathlib import Path
import bpy,numpy as np,sys,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2];parser=argparse.ArgumentParser();parser.add_argument('--source',default='models/queen/queen-rebuilt.blend');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);source=ROOT/args.source;before=hashlib.sha256(source.read_bytes()).hexdigest()
assert before=='358e327b4aa8022117af741f87dc2af835ae9bac266c3f16f42e559739987ed6'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
lights=[o for o in s.objects if o.type=='LIGHT' and o.data.energy>0];powers={o.name:o.data.energy for o in lights}
out=ROOT/'build/queen-mission/socket-spill-013';out.mkdir(parents=True,exist_ok=True)
x1,y1,x2,y2=315,650,635,815;W=s.render.resolution_x;H=s.render.resolution_y
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=(x1+.01)/W;s.render.border_max_x=(x2+.01)/W
s.render.border_min_y=(H-y2+.01)/H;s.render.border_max_y=(H-y1+.01)/H
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
s.render.use_persistent_data=True;s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
bg=s.world.node_tree.nodes['Background'];wp=bg.inputs['Strength'].default_value;bg.inputs['Strength'].default_value=0
for o in lights:o.data.energy=0
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
responses={};scores=[];yy,xx=np.indices((y2-y1,x2-x1));patch=(xx+x1>525)&(xx+x1<575)&(yy+y1>745)&(yy+y1<790)
def render(name,light=None):
    path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size;assert (w,h)==(x2-x1,y2-y1)
    a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);bpy.data.images.remove(im);a=a.reshape(h,w,4)[::-1,:,:3].copy()
    responses[name]=a;lum=a@np.array([.2126,.7152,.0722])
    scores.append({'key':name,'name':light.name if light else 'World','linear_luminance_sum':float(lum.sum()),'wrong_patch_sum':float(lum[patch].sum()),'energy':powers[light.name] if light else wp})
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';bpy.data.images['Render Result'].save_render(str(out/(name+'.png')),scene=s)
    s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32'
for i,o in enumerate(lights):
    o.data.energy=powers[o.name];render('light-%02d'%i,o);o.data.energy=0;print('SOCKET_LIGHT',i,o.name,flush=True)
bg.inputs['Strength'].default_value=wp;render('world')
np.savez_compressed(out/'responses.npz',**responses)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
(out/'manifest.json').write_text(json.dumps({'source_sha256':before,'crop':[x1,y1,x2,y2],'samples':256,'source_unchanged':True,'lights':sorted(scores,key=lambda x:-x['wrong_patch_sum'])},indent=2)+'\n')
print('SOCKET_SPILL_DONE',flush=True)

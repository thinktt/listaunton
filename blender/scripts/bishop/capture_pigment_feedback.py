"""Read-only measurement of an actual bishop BSDF trial for bounded pigment feedback."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--samples',type=int,default=64)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest();out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
objects=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
mat=objects[0].data.materials[0];ns=mat.node_tree.nodes;ls=mat.node_tree.links
bs=ns['Principled BSDF'];pigment=bs.inputs['Base Color'].links[0].from_socket
assert ns['Material Output'].inputs['Surface'].links[0].from_node==bs
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
s.render.resolution_percentage=100;s.render.use_persistent_data=True;s.cycles.samples=a.samples
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
def render(name):
    path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size
    values=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1].copy();np.save(out/(name+'.npy'),values)
    bpy.data.images.remove(im);print('BISHOP_FEEDBACK_PASS',name,flush=True)
render('linear-beauty')
for cut in {m for o in objects for m in o.data.materials if m and m!=mat}:
    n=cut.node_tree.nodes;l=cut.node_tree.links;e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(0,0,0,1)
    l.new(e.outputs[0],next(v for v in n if v.type=='OUTPUT_MATERIAL').inputs['Surface'])
e=ns.new('ShaderNodeEmission');ls.new(pigment,e.inputs['Color']);ls.new(e.outputs[0],ns['Material Output'].inputs['Surface'])
s.cycles.samples=8;render('actual-pigment')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':digest,'samples':a.samples,'source_unchanged':True,'diagnostic_only':True},indent=2)+'\n')

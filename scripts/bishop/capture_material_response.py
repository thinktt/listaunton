"""Diagnostic BSDF responses and pigment; never save the diagnostic shader as a model."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from color_pipeline import processors
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source',required=True);p.add_argument('--out',required=True)
p.add_argument('--samples',type=int,default=64)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/a.source;digest=hashlib.sha256(source.read_bytes()).hexdigest()
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
objects=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
mat=objects[0].data.materials[0];assert all(o.data.materials[0]==mat for o in objects)
ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns['Principled BSDF'];output=ns['Material Output']
old=bs.inputs['Base Color'].links[0].from_socket
reference=ROOT/'assets/bishop/reference.png'
im=bpy.data.images.load(str(reference),check_existing=False);im.colorspace_settings.name='Non-Color'
w,h=im.size;target=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1,:,:3].copy()
assert [w,h]==[s.render.resolution_x,s.render.resolution_y]
forward,inverse=processors(s);linear=target.copy();inverse.applyRGB(linear)
back=linear.copy();forward.applyRGB(back)
error=np.max(np.abs(back-target),axis=2)
np.save(out/'reference-srgb.npy',target);np.save(out/'reference-linear.npy',linear)
np.save(out/'inverse-roundtrip-error.npy',error)
bpy.data.images.remove(im)
for link in list(bs.inputs['Base Color'].links):ls.remove(link)
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
s.render.resolution_percentage=100;s.render.use_persistent_data=True;s.cycles.samples=a.samples;s.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'

def render(name):
    path=out/(name+'.exr');s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(path),check_existing=False)
    values=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1].copy()
    np.save(out/(name+'.npy'),values);bpy.data.images.remove(im)
    print('BISHOP_RESPONSE_PASS',name,flush=True)

bs.inputs['Base Color'].default_value=(0,0,0,1);render('black-bsdf')
bs.inputs['Base Color'].default_value=(1,1,1,1);render('white-bsdf')
ls.new(old,bs.inputs['Base Color']);render('linear-beauty')
# Diagnostic emission reads pigment and visibility, not a public beauty pass.
for cut in {m for ob in objects for m in ob.data.materials if m and m!=mat}:
    n=cut.node_tree.nodes;l=cut.node_tree.links
    e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(0,0,0,1)
    l.new(e.outputs[0],next(v for v in n if v.type=='OUTPUT_MATERIAL').inputs['Surface'])
em=ns.new('ShaderNodeEmission');ls.new(old,em.inputs['Color']);ls.new(em.outputs[0],output.inputs['Surface'])
s.cycles.samples=8;render('pigment')
coverage=ns.new('ShaderNodeAttribute');coverage.attribute_name='Pigment coverage'
ls.new(coverage.outputs['Fac'],em.inputs['Color']);render('coverage')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
record={'source':a.source,'source_sha256':digest,'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
    'resolution':[w,h],'samples':a.samples,'diagnostic_only':True,'source_unchanged':True,
    'view':s.view_settings.view_transform,'look':s.view_settings.look,
    'inverse_roundtrip_max_error':float(error.max()),
    'inverse_roundtrip_p99_error':float(np.quantile(error,.99)),
    'caveat':'Approximate diffuse response under inferred lighting, with interreflection. Inverse transforms may be unreliable near clipping; confidence rejects uncertain pixels. Pigment is inferred, not recovered source artwork.'}
(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
print('BISHOP_MATERIAL_RESPONSE_COMPLETE',json.dumps(record),flush=True)

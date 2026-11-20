"""Measure the original pigment blend, without changing the saved model or images."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;objects=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
materials={m for ob in objects for m in ob.data.materials if m};main=objects[0].data.materials[0]
assert all('Pigment coverage' in ob.data.attributes for ob in objects)
image=bpy.data.images.new('Original pigment confidence diagnostic',width=2048,height=2048,alpha=False,float_buffer=True)
image.colorspace_settings.name='Non-Color'
scratch=bpy.data.images.new('Disposable cut confidence target',width=64,height=64,alpha=False)
for mat in materials:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    for n in nodes:n.select=False
    target=nodes.new('ShaderNodeTexImage');target.image=image if mat==main else scratch;target.select=True;nodes.active=target
    em=nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,0,0,1)
    if mat==main:
        attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='Pigment coverage';links.new(attr.outputs['Fac'],em.inputs['Color'])
    links.new(em.outputs[0],nodes['Material Output'].inputs['Surface'])
for ob in s.objects:ob.select_set(False)
for ob in objects:
    ob.select_set(True);ob.data.uv_layers.active=ob.data.uv_layers['Wood atlas'];ob.data.uv_layers['Wood atlas'].active_render=True
bpy.context.view_layer.objects.active=objects[0]
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
s.cycles.samples=1;s.render.bake.margin=8;bpy.ops.object.bake(type='EMIT',use_clear=True)
array=np.array(image.pixels[:],dtype=np.float32).reshape(2048,2048,4)[::-1].copy();np.save(out/'coverage.npy',array[:,:,0])
image.filepath_raw=str(out/'coverage.exr');image.file_format='OPEN_EXR';image.save()
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':sha,'source_unchanged':True,
 'attribute':'Pigment coverage','meaning':'Original per-control-vertex confidence in projected pigment, interpolated on the evaluated surfaces. This is not a new visibility estimate.'},indent=2)+'\n')
print('PIGMENT_COVERAGE_BAKED',flush=True)

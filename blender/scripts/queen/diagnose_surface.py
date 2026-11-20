"""Isolate surface relief and inspect pigment coverage without changing sources.

Only wood.png is a normal BSDF trial. The emission passes are explicitly
diagnostic and must never substitute for a model's beauty render.
"""
from pathlib import Path
import hashlib,json
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'build/queen-mission/063-refined-tones/queen.blend'
before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;o=next(o for o in s.objects if o.type=='MESH' and not o.hide_render)
n=o.data.materials[0].node_tree.nodes;l=o.data.materials[0].node_tree.links
b=n.get('Principled BSDF');output=next(n for n in n if n.type=='OUTPUT_MATERIAL')
for name in ('Normal','Coat Normal'):
 for link in list(b.inputs[name].links):l.remove(link)
cfg=json.loads(s['mission_material_config']);cfg['variant']='067-no-relief'
cfg['surface_diagnostic']={'source':source.relative_to(ROOT).as_posix(),'source_sha256':before,'normal_and_coat_normal_disconnected':True}
s['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission/067-no-relief';out.mkdir(parents=True,exist_ok=True)
s.render.use_persistent_data=True;s.cycles.samples=64;s.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'));bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
em=n.new('ShaderNodeEmission');l.new(b.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);l.new(em.outputs[0],output.inputs['Surface'])
s.view_settings.view_transform='Standard';s.view_settings.look='None'
s.render.filepath=str(out/'diagnostic-pigment.png');bpy.ops.render.render(write_still=True)
att=n.new('ShaderNodeAttribute');att.attribute_name='Inferred pigment coverage';l.new(att.outputs['Fac'],em.inputs['Color'])
s.render.filepath=str(out/'diagnostic-coverage.png');bpy.ops.render.render(write_still=True)
values=np.empty(len(o.data.vertices),dtype=np.float32);o.data.attributes[att.attribute_name].data.foreach_get('value',values)
record={'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==before,'coverage_vertex_histogram':np.histogram(values,bins=[0,.01,.25,.5,.75,.99,1.01])[0].tolist(),'coverage_range':[float(values.min()),float(values.max())],'diagnostic_emission_passes_are_not_beauty_renders':True}
(out/'diagnostics.json').write_text(json.dumps(record,indent=2)+'\n');print('SURFACE_DIAGNOSTIC_DONE',record,flush=True)

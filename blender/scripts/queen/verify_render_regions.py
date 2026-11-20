"""Render-equivalence diagnostic before attempting linked regional lighting."""
from pathlib import Path
import hashlib, json, sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from render_regions import partition, REGION_NAMES
source=ROOT/'models/queen/queen-rebuilt.blend'
source_hash='82100ad9047426b1be46e72d01d769189b4e9f667005fd8c8bcc5d743c16526e'
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
parts,report=partition(scene,obj)
out=ROOT/'build/queen-mission/082-render-regions-equivalence'
out.mkdir(parents=True,exist_ok=True)
settings={'variant':out.name,'source_sha256':source_hash,'regions':report,
          'method':'Exact evaluated faces partitioned by turned region, with original UVs and custom smooth corner normals; all accepted lights still global.'}
scene.render.filepath=str(out/'wood.png')
scene.render.use_persistent_data=True
scene.cycles.samples=64;scene.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
print('RENDER_REGIONS_BEAUTY_DONE',flush=True)
# A separately labeled emission diagnostic supplies discrete region IDs for
# light-fitting masks. It is never a beauty image or a viewer texture.
for index,part in enumerate(parts):
    material=bpy.data.materials.new('Diagnostic region '+REGION_NAMES[index])
    material.use_nodes=True
    nodes=material.node_tree.nodes;nodes.clear()
    emission=nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value=((index+1)/16,0,0,1)
    output=nodes.new('ShaderNodeOutputMaterial')
    material.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
    part.data.materials[0]=material
scene.render.resolution_x=scene.render.resolution_y=418
scene.cycles.use_denoising=False
scene.render.image_settings.file_format='OPEN_EXR'
scene.render.image_settings.color_depth='32'
scene.render.filepath=str(out/'region-ids.exr')
bpy.ops.render.render(write_still=True)
image=bpy.data.images.load(scene.render.filepath,check_existing=False)
array=np.empty(418*418*4,dtype=np.float32);image.pixels.foreach_get(array)
array=array.reshape(418,418,4)[::-1].copy()
np.save(out/'region-ids.npy',array)
(out/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
print('RENDER_REGIONS_EQUIVALENCE_DONE',flush=True)

"""Save, reopen, validate packed pigment and render a chosen bishop checkpoint."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--samples',type=int,default=96)
p.add_argument('--fixed-samples',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;dest=ROOT/a.out
assert dest.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
dest.mkdir(parents=True,exist_ok=True);source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
camera=[float(x) for row in s.camera.matrix_world for x in row]+[s.camera.data.ortho_scale,s.camera.data.shift_x,s.camera.data.shift_y]
s.cycles.samples=a.samples;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
if a.fixed_samples:s.cycles.use_adaptive_sampling=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.render.filepath=str(dest/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(dest/'bishop.blend'))
bpy.ops.wm.open_mainfile(filepath=str(dest/'bishop.blend'),load_ui=False);s=bpy.context.scene
assert camera==[float(x) for row in s.camera.matrix_world for x in row]+[s.camera.data.ortho_scale,s.camera.data.shift_x,s.camera.data.shift_y]
objects=[o for o in s.objects if o.type=='MESH' and not o.hide_render];assert len(objects)==2
texture=ROOT/'assets/bishop/bishop-boxwood-albedo.png';checks={}
disk=bpy.data.images.load(str(texture),check_existing=False);disk_pixels=np.array(disk.pixels[:],dtype=np.float32)
for mat in {m for obj in objects for m in obj.data.materials if m}:
    assert mat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node.type=='BSDF_PRINCIPLED'
    node=mat.node_tree.nodes.get('Baked boxwood pigment')
    if not node:continue
    assert node.image.packed_file
    error=float(np.max(np.abs(np.array(node.image.pixels[:],dtype=np.float32)-disk_pixels)));assert error<1e-6
    checks[mat.name]=error
assert checks
bpy.data.images.remove(disk)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for dev in prefs.devices:dev.use=dev.type=='OPTIX'
s.cycles.device='GPU' if any(dev.use for dev in prefs.devices) else 'CPU'
bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report={'source':a.source,'source_sha256':source_hash,'saved_model_sha256':hashlib.sha256((dest/'bishop.blend').read_bytes()).hexdigest(),
    'render_sha256':hashlib.sha256((dest/'wood.png').read_bytes()).hexdigest(),'texture_sha256':hashlib.sha256(texture.read_bytes()).hexdigest(),
    'reopened_packed_pixel_max_errors':checks,'camera_preserved':True,'shader':'Principled BSDF','samples':a.samples,
    'resolution':[s.render.resolution_x,s.render.resolution_y],'display':s.view_settings.view_transform,'look':s.view_settings.look,
    'source_unchanged':True}
report['adaptive_sampling']=s.cycles.use_adaptive_sampling
report['glossy_bounces']=s.cycles.glossy_bounces
(dest/'reopen-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('BISHOP_FINAL_RENDER_COMPLETE',json.dumps(report),flush=True)

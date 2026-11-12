"""Save, reopen and render an isolated high-frequency wood relief experiment."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('config')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text())
source=ROOT/cfg['source'];out=ROOT/'build/bishop-mission'/cfg['variant']
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source_hash=sha(source);height=ROOT/cfg['height']['height_map']
assert sha(height)==cfg['height']['height_map_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
mat=bpy.data.materials[cfg['material']];nodes=mat.node_tree.nodes;links=mat.node_tree.links
target=nodes['Subtle pigment and pores'].inputs[1]
assert len(target.links)==1 and target.links[0].from_node.name=='Pigment relief'
old=[target.links[0].from_node.name,target.links[0].from_socket.identifier]
uv=nodes['Baked boxwood pigment'].inputs['Vector'].links[0]
im=bpy.data.images.load(str(height),check_existing=False)
im.name='Bishop experimental fine relief';im.colorspace_settings.name='Non-Color';im.pack()
node_name='Bishop band-passed pigment relief'
node=nodes.new('ShaderNodeTexImage');node.name=node_name
node.image=im;node.interpolation='Linear';node.extension='EXTEND'
links.new(uv.from_socket,node.inputs['Vector']);links.new(node.outputs['Color'],target)
s['bishop_fine_relief_trial']=json.dumps(cfg,sort_keys=True)
s.cycles.samples=cfg['samples'];s.cycles.use_adaptive_sampling=False
s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'bishop.blend'),load_ui=False);s=bpy.context.scene
packed=bpy.data.materials[cfg['material']].node_tree.nodes[node_name].image
disk=bpy.data.images.load(str(height),check_existing=False);disk.colorspace_settings.name='Non-Color'
error=float(np.max(np.abs(np.array(packed.pixels[:])-np.array(disk.pixels[:]))));assert error==0
bpy.data.images.remove(disk)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
bpy.ops.render.render(write_still=True)
assert sha(source)==source_hash
(out/'reopen-validation.json').write_text(json.dumps(dict(config=a.config,source=cfg['source'],source_sha256=source_hash,
 model_sha256=sha(out/'bishop.blend'),render_sha256=sha(out/'wood.png'),source_unchanged=True,
 reopened_before_render=True,packed_height_pixel_error=error,old_relief_link=old,samples=cfg['samples']),indent=2)+'\n',newline='\n')
print('FINE_RELIEF_TRIAL_COMPLETE',flush=True)

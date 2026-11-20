"""Build exact socket light receivers, then render the reopened trial scene."""
import argparse,hashlib,json,math,sys
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from render_regions import partition_socket,socket_only

p=argparse.ArgumentParser(description=__doc__);p.add_argument('config')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads((ROOT/a.config).read_text())
source=ROOT/cfg['source'];out=ROOT/'build/bishop-mission'/cfg['variant']
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(source)==cfg['source_sha256'],'Accepted input changed.'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
parts,partition=partition_socket(s,*cfg['socket_z_band'])
arcs=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('socket arc ')]
assert len(arcs)==17
socket_only(arcs,parts)
for lamp in arcs:
    lamp.data.shadow_soft_size=cfg['arc_shadow_soft_size']
    lamp.data.spot_size=math.radians(cfg['arc_spot_degrees'])
rest=next(o for o in parts if o['bishop_render_region']=='body-rest')
receivers=bpy.data.collections.new('Bishop all body except socket');receivers.objects.link(rest)
for name in cfg['exclude_from_socket']:
    bpy.data.objects[name].light_linking.receiver_collection=receivers
s['bishop_receiver_trial']=json.dumps(cfg,sort_keys=True)
s.cycles.samples=cfg['samples'];s.cycles.use_adaptive_sampling=False
s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'bishop.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'bishop.blend'),load_ui=False);s=bpy.context.scene
assert json.loads(s['bishop_receiver_trial'])==cfg
assert len([o for o in s.objects if o.get('bishop_render_region')])==2
for part in [o for o in s.objects if o.get('bishop_render_region')]:
    control=bpy.data.objects[part['bishop_control_name']]
    assert list(part.data.materials)==list(control.data.materials)
    assert all(mat and mat.node_tree.nodes['Material Output'].inputs['Surface'].links[0].from_node.type=='BSDF_PRINCIPLED' for mat in part.data.materials)
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
s.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
bpy.ops.render.render(write_still=True)
assert sha(source)==cfg['source_sha256']
(out/'parameters.json').write_text(json.dumps({'config':cfg,'source_unchanged':True,
 'saved_model_sha256':sha(out/'bishop.blend'),'render_sha256':sha(out/'wood.png'),
 'partition':partition,'reopened_before_render':True},indent=2)+'\n')
print('SOCKET_RECEIVER_TRIAL_COMPLETE',cfg['variant'],flush=True)

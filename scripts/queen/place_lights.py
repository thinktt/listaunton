"""A lighting-only trial, keeping the saved mesh and material untouched."""
from pathlib import Path
import argparse,json,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('config');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);settings=json.loads(Path(args.config).read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/settings['source']),load_ui=False);scene=bpy.context.scene
for light in list(scene.objects):
 if light.type=='LIGHT':bpy.data.objects.remove(light,do_unlink=True)
for spec in settings['lights']:
 data=bpy.data.lights.new(spec['name'],'AREA');data.energy=spec['energy'];data.shape=spec.get('shape','DISK');data.size=spec['size'];data.diffuse_factor=spec.get('diffuse_factor',1)
 if data.shape=='RECTANGLE':data.size_y=spec['size_y']
 light=bpy.data.objects.new(spec['name'],data);scene.collection.objects.link(light);light.location=spec['position'];light.rotation_euler=(Vector(spec.get('target',[0,0,2.3]))-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=settings['world']
cfg=json.loads(scene['mission_material_config']);cfg.update(settings);scene['mission_material_config']=json.dumps(cfg,sort_keys=True)
out=ROOT/'build/queen-mission'/settings['variant'];out.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(out/'wood.png');scene.cycles.samples=settings.get('samples',64);scene.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as exc:print('CPU fallback',exc)
bpy.ops.render.render(write_still=True);(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n');print('LIGHTING_TRIAL_DONE',flush=True)

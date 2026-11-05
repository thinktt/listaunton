"""Preserve accepted lighting while excluding unrelated finial reflections."""
from pathlib import Path
import hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from render_regions import link
source=ROOT/'build/queen-mission/082-render-regions-equivalence/queen.blend'
digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
settings=json.loads(scene['mission_material_config'])
parts={o['mission_render_region']:o for o in scene.objects if o.get('mission_render_region')}
receivers=[v for k,v in parts.items() if k!='finial']
scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
bpy.context.preferences.filepaths.save_version=0
for variant,spots_only in [('086-isolated-finial-reflectors',False),('087-finial-spots-only',True)]:
    linked=[]
    for spec in settings['lights']:
        light=bpy.data.objects[spec['name']]
        intended='finial-' in spec['name'] and (not spots_only or spec['name'].endswith('-spot'))
        if spec.get('diffuse_factor',1)==0 and not intended:
            link(light,receivers,'all-except-finial');linked.append(spec['name'])
        else:light.light_linking.receiver_collection=None
    cfg=dict(settings);cfg['variant']=variant
    cfg['finial_receiver_isolation']={'source_sha256':digest,'excluded_reflectors':linked,'spots_only':spots_only,
        'hypothesis':'Preserve all accepted lights and powers for the rest of the piece; prevent unrelated reflected sources from reaching the finial.'}
    scene['mission_material_config']=json.dumps(cfg,sort_keys=True)
    out=ROOT/'build/queen-mission'/variant;out.mkdir(parents=True,exist_ok=True)
    scene.render.filepath=str(out/'wood.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
    bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
    print('FINIAL_RECEIVER_ISOLATION_DONE',variant,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest

"""Rebuild the minimal two-receiver finial-light isolation from the sixth model."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from render_regions import partition,link
p=argparse.ArgumentParser()
p.add_argument('--variant',default='088-minimal-finial-receivers')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert Path(args.variant).name==args.variant and args.variant not in ('.','..')
source=ROOT/'history/queen-mission-006/queen-rebuilt.blend'
digest='82100ad9047426b1be46e72d01d769189b4e9f667005fd8c8bcc5d743c16526e'
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
parts,report=partition(scene,obj,finial_only=True)
body=next(p for p in parts if p['mission_render_region']=='turned-body')
settings=json.loads(scene['mission_material_config']);excluded=[]
for spec in settings['lights']:
    intended='finial-' in spec['name'] and spec['name'].endswith('-spot')
    if spec.get('diffuse_factor',1)==0 and not intended:
        link(bpy.data.objects[spec['name']],[body],'turned-body');excluded.append(spec['name'])
        spec['receiver_parts']=['turned-body']
settings['variant']=args.variant
settings['finial_receiver_isolation']={'baseline':source.relative_to(ROOT).as_posix(),'source_sha256':digest,
    'spots_only':True,'excluded_reflectors':excluded,'render_regions':report,
    'editable_control_tag':'mission_editable_control','render_region_tag':'mission_render_region',
    'method':'The unchanged closed control mesh is exported to the viewer. Two exact evaluated render receivers preserve its UVs and smooth normals. Only the intended three finial spots can reflect directly on the finial; other accepted reflectors keep their original powers on the turned body.'}
scene['mission_material_config']=json.dumps(settings,sort_keys=True)
out=ROOT/'build/queen-mission'/settings['variant'];out.mkdir(parents=True,exist_ok=True)
scene.render.filepath=str(out/'wood.png');scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.render.use_persistent_data=True
# Keep a single editable piece in the viewport. Eye visibility does not
# disable the two receivers in final rendering.
for part in parts:part.hide_set(True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n')
print('MINIMAL_FINIAL_RECEIVERS_DONE',flush=True)

"""Retain the accepted collar illumination as an independently fitted light basis."""
from pathlib import Path
import bpy,sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from render_regions import link
source=ROOT/'build/queen-mission/141-collar-crescents/queen.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
cfg=json.loads(s['mission_material_config']);part=next(o for o in s.objects if o.get('mission_render_region')=='collars')
specs={p['name']:p for p in cfg['lights']}
for i,name in enumerate(cfg['collar_receiver_isolation']['excluded_reflectors']):
    old=bpy.data.objects[name];new=old.copy();new.data=old.data.copy();new.name='Collar retained %02d'%i
    s.collection.objects.link(new);link(new,[part],'collars')
    spec=dict(specs[name]);spec.update(name=new.name,clone_of=name,receiver_parts=['collars'])
    cfg['lights'].append(spec);cfg['finial_receiver_isolation']['excluded_reflectors'].append(new.name)
cfg['variant']='143-retained-collar-basis';cfg['collar_crescents']['retained_basis']='Copy the accepted reflectors and link copies only to collars, keeping their action everywhere else fixed.'
s['mission_material_config']=json.dumps(cfg);s['mission_variant']=cfg['variant']
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(exist_ok=True,parents=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
(out/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('COLLAR_BASIS_READY',flush=True)

"""Check that only three existing finial reflectors were re-aimed."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from validate_profile_preservation import inspect
p=argparse.ArgumentParser();p.add_argument('current');p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
baseline=ROOT/'history/queen-mission-020/queen-rebuilt.blend';current=ROOT/a.current
before=inspect(baseline);after=inspect(current)
for key in ['material_nodes','material_links','camera','object_matrix']:assert before[key]==after[key],key
names={f'Display fitted finial-{name}-spot' for name in ['left','top','right']}
assert before['lights'].keys()==after['lights'].keys()
for name,old in before['lights'].items():
    new=after['lights'][name]
    if name not in names:
        assert old==new,name
        continue
    assert old['parts']==new['parts']==['finial']
    for key in ['type','color','shadow','diffuse','glossy','parts']:assert old[key]==new[key],(name,key)
    assert abs(old['energy']-new['energy'])<old['energy']*1e-6
    assert abs(old['radius']-new['radius'])<1e-6
settings=json.loads(bpy.context.scene['mission_material_config'])
assert not settings.get('contact_reflection_study'), 'Do not promote the rejected contact emitters'
changes=settings['finial_reflector_aim']['changes'];assert {v['name'] for v in changes}==names
for item in changes:
    lamp=bpy.data.objects[item['name']];spec=item['current'];target=Vector(spec['target'])
    assert (lamp.location-Vector(spec['position'])).length<1e-5
    direction=lamp.rotation_euler.to_matrix()@Vector((0,0,-1))
    assert direction.dot((target-lamp.location).normalized())>.999999
    assert abs(lamp.data.spot_size-math.radians(12))<1e-6
    assert not lamp.visible_diffuse and lamp.visible_glossy and lamp.data.use_shadow
report={'passed':True,'source_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),
        'all_material_nodes_links_and_packed_images_identical':True,'camera_and_object_matrix_identical':True,
        'light_count':len(before['lights']),'moved_lights':sorted(names),'all_other_lights_identical':True,
        'finial_only_receivers':True,'light_colors_and_powers_preserved_with_float_tolerance':True,
        'fixed_12_degree_cones':True,'all_three_lights_cast_shadows':True,'no_contact_emitters_added':True}
(ROOT/a.out/'cap-light-preservation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))

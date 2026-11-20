"""Check the local finial material edit, packed atlas and exact light-edit scope."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('--baseline',default='history/queen-mission-016/queen-rebuilt.blend');p.add_argument('--current',default='models/queen/queen-rebuilt.blend');p.add_argument('--report-dir',default='assets/queen')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])

def light_state(o):
    d=o.data
    return {'matrix':[float(x) for row in o.matrix_world for x in row],'energy':d.energy,'color':list(d.color),'type':d.type,'diffuse':o.visible_diffuse,'glossy':o.visible_glossy,'shadow':d.use_shadow,
            'radius':getattr(d,'shadow_soft_size',None),'spot_size':getattr(d,'spot_size',None),'spot_blend':getattr(d,'spot_blend',None),
            'parts':sorted(x.get('mission_render_region','') for x in o.light_linking.receiver_collection.objects) if o.light_linking.receiver_collection else None}
def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);nodes=obj.data.materials[0].node_tree.nodes;bs=nodes.get('Principled BSDF')
    props={name:float(bs.inputs[name].default_value) for name in ['Roughness','IOR','Specular IOR Level','Coat Weight','Coat Roughness']}
    lights={o.name:light_state(o) for o in s.objects if o.type=='LIGHT'}
    return s,obj,nodes,bs,props,lights
baseline=ROOT/a.baseline;current=ROOT/a.current
_,_,_,_,old_props,old_lights=inspect(baseline)
s,obj,nodes,bs,props,lights=inspect(current)
assert props==old_props,(props,old_props)
allowed={n for n in old_lights if 'finial-' in n and n.endswith('-spot')};assert len(allowed)==3
cfg=json.loads(s['mission_material_config'])
local_power=cfg.get('raised_flare_compact_socket',{}).get('reflection_power',{})
assert set(local_power) <= {'Display fitted base-key','Socket crescent 08'}
for name,prior in old_lights.items():
    if name in allowed:
        continue
    expected=prior.copy()
    if name in local_power:
        change=local_power[name]
        assert prior['energy']==change['before'] and 0<change['factor']<=1
        expected['energy']=float(np.float32(change['before']*change['factor']))
        assert expected['energy']==change['after']
    assert lights[name]==expected,(name,lights[name],expected)
clones={n for n in lights if n not in old_lights};assert len(clones)==3
regions={o['mission_render_region'] for o in s.objects if o.get('mission_render_region')}
for name in allowed:assert lights[name]['parts']==['finial']
for name in clones:
    spec=next(x for x in cfg['lights'] if x['name']==name);prior=old_lights[spec['clone_of']].copy();actual=lights[name].copy()
    assert actual.pop('parts')==sorted(regions-{'finial'});prior.pop('parts')
    for key,value in prior.items():
        if key=='matrix':assert np.allclose(value,actual[key],atol=1e-6,rtol=0),(name,key)
        else:assert actual[key]==value,(name,key,actual[key],value)
color=bs.inputs['Base Color'].links[0].from_node;assert color.type=='TEX_IMAGE'
im=color.image;assert im.colorspace_settings.name=='sRGB' and im.packed_file
texture=ROOT/cfg['texture'];sha=hashlib.sha256(texture.read_bytes()).hexdigest()
assert hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==sha
assert color.inputs['Vector'].links[0].from_node.uv_map=='Pigment atlas'
pixels=np.empty(im.size[0]*im.size[1]*4,dtype=np.float32);im.pixels.foreach_get(pixels)
external=bpy.data.images.load(str(texture),check_existing=False);external.colorspace_settings.name='sRGB'
values=np.empty_like(pixels);external.pixels.foreach_get(values);assert np.array_equal(pixels,values)
bump=nodes.get('Bump.001');distance=bump.inputs['Distance'].links[0].from_node
assert distance.type=='MAP_RANGE'
assert abs(distance.inputs['To Min'].default_value-.007)<1e-8
assert abs(distance.inputs['To Max'].default_value-.00175)<1e-8
assert bs.inputs['Normal'].links[0].from_node==bump and bs.inputs['Coat Normal'].links[0].from_node==bump
coordinates=next(n for n in nodes if n.label=='Local finial coordinates')
assert coordinates.type=='VECT_TRANSFORM' and coordinates.vector_type=='POINT' and coordinates.convert_from=='WORLD' and coordinates.convert_to=='OBJECT'
assert cfg['finial_polish']['coordinate_space']=='OBJECT'
output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');assert output.inputs['Surface'].links[0].from_node==bs
report={'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'current_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),'texture_sha256':sha,
        'roughness_ior_and_coat_parameters_unchanged':True,'other_existing_lights_exact':not bool(local_power),'later_socket_and_flare_powers':local_power,'all_lights_match_documented_scope':True,'changed_existing_lights':sorted(allowed | set(local_power)),'preserved_body_light_copies':sorted(clones),
        'body_copies_match_baseline':True,'finial_lights_linked_only_to_finial':True,'packed_png_bytes_and_decoded_pixels_exact':True,'base_color_uses_fixed_uv_atlas':True,
        'bump_distance_body':.007,'bump_distance_finial':.00175,'finial_polish_in_object_coordinates':True,'real_bsdf_output':True,'passed':True}
(ROOT/a.report_dir/'finial-material-check.json').write_text(json.dumps(report,indent=2)+'\n');print('FINIAL_MATERIAL_VALIDATED',json.dumps(report),flush=True)

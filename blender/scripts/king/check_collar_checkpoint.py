"""Check the exact scope of a king collar-lighting experiment or checkpoint."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import COLLAR_RANGES
from check_base_light_checkpoint import snapshot
from check_socket_checkpoint import extra


def main(before,after,output,baseline=False,middle_shadow_exception=False):
    paths=[ROOT/before,ROOT/after];hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    a,old,_=snapshot(before);ae=extra();old_shadows={o.name:bool(o.data.use_shadow) for o in bpy.context.scene.objects if o.type=='LIGHT'}
    b,new,regions=snapshot(after);be=extra();s=bpy.context.scene
    assert a==b and ae==be,'Control geometry, UVs, attributes, material, packed images, world or camera changed'
    assert s.get('king_split_collars') and regions['receiverCount']==9
    assert bool(s.get('king_collar_broad_excluded'))==(not baseline)
    for name,light in old.items():
        expected=dict(light)
        if light['receivers'] and 'upper-body' in light['receivers']:
            if baseline or name not in ['Upper varnish','Front varnish']:
                expected['receivers']=sorted(set(light['receivers'])|set(COLLAR_RANGES))
        assert new[name]==expected,('Existing light changed',name,new[name],expected)
        assert bool(bpy.data.objects[name].data.use_shadow)==old_shadows[name],('Existing shadow setting changed',name)
    added=sorted(set(new)-set(old))
    expected=[] if baseline else sorted('Collar '+level+' '+side for level in ['upper','middle','lower'] for side in ['left','right'])
    assert added==expected,(added,expected)
    for name in added:
        light=bpy.data.objects[name]
        assert new[name]['receivers']==[name.split()[1]+'-collar']
        assert new[name]['glossy'] and not new[name]['diffuse'] and light.data.type=='AREA'
        expected_shadow=not(middle_shadow_exception and name=='Collar middle left')
        assert bool(light.data.use_shadow)==expected_shadow,(name,expected_shadow)
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]==hashes
    report=dict(before=before,after=after,source_sha256=hashes[0],model_sha256=hashes[1],
        all_control_geometry_uvs_float_attributes_material_packed_images_world_camera_exact=True,
        all_existing_light_settings_exact=True,source_files_unchanged=True,baseline_split_only=baseline,
        collar_profile_intervals=COLLAR_RANGES,intervals_upper_exclusive=True,
        existing_routes_preserved_except_declared_broad_collar_exclusion=not baseline,
        added_lights={name:new[name] for name in added},
        declared_shadow_exceptions=['Collar middle left'] if middle_shadow_exception else [],
        added_light_shadow_settings={name:bool(bpy.data.objects[name].data.use_shadow) for name in added},render_receivers=regions)
    out=ROOT/output;out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('KING_COLLAR_SCOPE_PASS')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');p.add_argument('--baseline',action='store_true');p.add_argument('--middle-shadow-exception',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.before,a.after,a.output,a.baseline,a.middle_shadow_exception)

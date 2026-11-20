"""Check that a socket-lighting experiment preserves accepted geometry and finish."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import controls
from check_base_light_checkpoint import snapshot,digest


def extra():
    s=bpy.context.scene
    attributes={o.name:{a.name:(a.domain,digest([v.value for v in a.data]))
        for a in o.data.attributes if a.data_type=='FLOAT' and a.domain in ('POINT','CORNER') and not a.name.startswith('.')}
        for o in controls(s)}
    images={im.name:hashlib.sha256(bytes(im.packed_file.data)).hexdigest()
            for im in bpy.data.images if im.packed_file}
    return dict(all_float_attributes=attributes,all_packed_images=images)


def main(before,after,output,baseline=False):
    source=ROOT/before;destination=ROOT/after
    hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in (source,destination)]
    a,old,_=snapshot(before);ae=extra()
    b,new,regions=snapshot(after);be=extra();s=bpy.context.scene
    assert a==b and ae==be,'Geometry, UVs, finish, images, world or camera changed'
    assert s.get('king_split_socket') and regions['receiverCount']==5
    assert bool(s.get('king_socket_broad_excluded'))==(not baseline)
    for name,light in old.items():
        expected=dict(light);receivers=light['receivers']
        if receivers and 'upper-body' in receivers and (baseline or name not in ('Upper varnish','Front varnish')):
            expected['receivers']=sorted(set(receivers)|{'socket'})
        assert new[name]==expected,('Unexpected existing light change',name,new[name],expected)
    added=sorted(set(new)-set(old))
    assert (not added) if baseline else (bool(added) and all(n.startswith('Socket ') for n in added))
    for name in added:
        light=bpy.data.objects[name]
        assert new[name]['receivers']==['socket'] and new[name]['glossy'] and not new[name]['diffuse']
        assert light.data.use_shadow
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in (source,destination)]==hashes
    out=ROOT/output;out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(dict(before=before,after=after,source_sha256=hashes[0],model_sha256=hashes[1],
        control_geometry_uvs_all_float_attributes_material_images_camera_world_exact=True,
        existing_light_settings_exact=True,source_files_unchanged=True,baseline_split_only=baseline,
        socket_boundary_profile_ring=28,added_lights={n:new[n] for n in added},
        added_lights_cast_shadows=True,render_receivers=regions),indent=2)+'\n',encoding='utf-8')
    print('KING_SOCKET_SCOPE_PASS')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');p.add_argument('--baseline',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.before,a.after,a.output,a.baseline)

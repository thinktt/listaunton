"""Verify a seam receiver/light checkpoint leaves the accepted king intact."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from check_base_light_checkpoint import snapshot
from check_socket_checkpoint import extra


def main(before,after,output,baseline=False):
    paths=[ROOT/before,ROOT/after];hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
    a,old,_=snapshot(before);ae=extra();b,new,regions=snapshot(after);be=extra();s=bpy.context.scene
    assert a==b and ae==be,'Control geometry, UVs, attributes, material, packed images, world or camera changed'
    assert s.get('king_split_socket_seam') and s.get('king_socket_seam_lights_confined') and regions['receiverCount']==6
    for name,light in old.items():
        expected=dict(light)
        if light['receivers'] and 'socket' in light['receivers']:expected['receivers']=sorted(set(light['receivers'])|{'socket-seam'})
        assert new[name]==expected,('Existing light changed',name,new[name],expected)
    added=sorted(set(new)-set(old));assert added==([] if baseline else ['Socket seam left','Socket seam right'])
    for name in added:
        assert new[name]['receivers']==['socket-seam'] and new[name]['glossy'] and not new[name]['diffuse']
        light=bpy.data.objects[name];assert light.data.type=='AREA' and light.data.use_shadow
    assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]==hashes
    report=dict(before=before,after=after,source_sha256=hashes[0],model_sha256=hashes[1],
        all_control_geometry_uvs_float_attributes_material_packed_images_world_camera_exact=True,
        all_existing_light_settings_exact=True,existing_socket_coverage_preserved=True,source_files_unchanged=True,
        baseline_split_only=baseline,seam_profile_interval=[26.55,27.25],seam_interval_upper_exclusive=True,
        added_lights={n:new[n] for n in added},added_lights_cast_shadows=True,render_receivers=regions)
    out=ROOT/output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('KING_SOCKET_SEAM_SCOPE_PASS')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');p.add_argument('--baseline',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.before,a.after,a.output,a.baseline)

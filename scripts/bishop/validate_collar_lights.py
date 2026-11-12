"""Audit added collar reflectors against every preserved scene-state category."""
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from validate_render_receivers import snapshot,check
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def audit(source,model,config_path):
    cfg=json.loads(config_path.read_text())
    assert ROOT/cfg['source']==source
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
    before=snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
    s=bpy.context.scene;after=snapshot()
    specs={spec['name']:spec for spec in cfg['lights']}
    assert len(specs)==len(cfg['lights']) and specs
    assert set(after['lights'])-set(before['lights'])==set(specs)
    assert set(before['lights'])<=set(after['lights'])
    effective={}
    for name,spec in specs.items():
        assert name.startswith('collar arc ') and spec['type']=='SPOT'
        assert set(spec)=={'name','type','energy','color','position','target',
                           'spot_size','spot_blend','shadow_soft_size','diffuse','glossy','receiver'}
        ob=bpy.data.objects[name];d=ob.data
        assert d.type=='SPOT' and spec['energy']>0
        for key in ['energy','color','spot_size','spot_blend','shadow_soft_size']:
            assert np.allclose(getattr(d,key),spec[key],rtol=2e-6,atol=1e-7),(name,key)
        assert np.allclose(ob.location,spec['position'],rtol=0,atol=1e-6)
        target=(Vector(spec['target'])-ob.location).normalized()
        axis=ob.rotation_euler.to_matrix()@Vector((0,0,-1))
        assert (axis-target).length<1e-6
        assert spec['receiver']=='body' and spec['diffuse'] is False and spec['glossy'] is True
        assert not ob.hide_render and not ob.visible_diffuse and ob.visible_glossy
        assert ob.light_linking.receiver_collection.name=='Bishop light receiver body'
        assert after['lights'][name]['receivers']==before['lights']['head reflection']['receivers']
        effective[name]=after['lights'].pop(name)
    after['objects']=[item for item in after['objects'] if item[0] not in specs]
    for key in before:
        assert json.dumps(before[key],sort_keys=True)==json.dumps(after[key],sort_keys=True),key
    receivers=check(s,json.loads(s['bishop_receiver_trial']))
    return dict(passed=True,source=source.relative_to(ROOT).as_posix(),source_sha256=sha(source),
                model=model.relative_to(ROOT).as_posix(),model_sha256=sha(model),
                config=config_path.relative_to(ROOT).as_posix(),config_sha256=sha(config_path),
                only_declared_collar_lights_added=True,new_lights=effective,
                all_existing_objects_meshes_modifiers_uvs_materials_pixels_lights_camera_world_and_render_paths_preserved=True,
                render_receivers=receivers,reopened_audit=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True);p.add_argument('--model',required=True)
    p.add_argument('--config',required=True);p.add_argument('--out',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    report=audit(ROOT/a.source,ROOT/a.model,ROOT/a.config)
    path=ROOT/a.out;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print('BISHOP_COLLAR_LIGHT_SCOPE_PASSED',flush=True)

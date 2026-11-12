"""Independently verify an isolated packed-atlas replacement after reopening."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from validate_render_receivers import snapshot,check
from bishop_scene import editable_meshes
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def audit(source,model,atlas):
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);before=snapshot()
    mat_name=editable_meshes(bpy.context.scene)[0].data.materials[0].name
    bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False);s=bpy.context.scene;after=snapshot()
    node=bpy.data.materials[mat_name].node_tree.nodes['Baked boxwood pigment'];packed=node.image
    assert packed and packed.packed_file and packed.colorspace_settings.name=='sRGB'
    disk=bpy.data.images.load(str(atlas),check_existing=False)
    error=float(np.max(np.abs(np.array(packed.pixels[:],dtype=np.float32)-np.array(disk.pixels[:],dtype=np.float32))))
    assert error==0;assert list(packed.size)==list(disk.size)
    bpy.data.images.remove(disk)
    before['materials'][mat_name]['nodes']['Baked boxwood pigment']['image']=after['materials'][mat_name]['nodes']['Baked boxwood pigment']['image']
    for key in before:assert json.dumps(before[key],sort_keys=True)==json.dumps(after[key],sort_keys=True),key
    receivers=check(s,json.loads(s['bishop_receiver_trial'])) if s.get('bishop_receiver_trial') else {'used':False}
    return {'passed':True,'source':source.relative_to(ROOT).as_posix(),'source_sha256':sha(source),
     'model':model.relative_to(ROOT).as_posix(),'model_sha256':sha(model),
     'atlas':atlas.relative_to(ROOT).as_posix(),'atlas_sha256':sha(atlas),'packed_pixel_max_error':error,
     'only_declared_atlas_changed':True,'geometry_uvs_material_graph_relief_camera_lights_world_and_render_path_preserved':True,
     'render_receivers':receivers,'reopened_audit':True}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--model',required=True);p.add_argument('--atlas',required=True);p.add_argument('--out',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);record=audit(ROOT/a.source,ROOT/a.model,ROOT/a.atlas)
    out=ROOT/a.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(record,indent=2)+'\n')
    print('ATLAS_SCOPE_PASSED',flush=True)

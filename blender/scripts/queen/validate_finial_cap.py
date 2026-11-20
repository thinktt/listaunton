"""Verify a locally lowered egg cap against the accepted twentieth queen."""
import hashlib
from pathlib import Path
import bpy
import numpy as np
from refine_socket_flare import read_controls
ROOT=Path(__file__).resolve().parents[2]
BASELINE_SHA='652bc91ad251ca5a4ea183256b45bae31c7cffe69121ba21582103d91617a63c'

def check(controls,settings,mesh_name):
    change=settings.get('finial_shape_study')
    if not change:return None,controls
    cfg=change['config'];assert change['source_sha256']==BASELINE_SHA
    assert cfg.get('elevation',54)==54 and cfg.get('axial_scale',1)==1
    assert not cfg.get('radii') and not cfg.get('camera_floor_offset')
    assert not cfg.get('preserve_face_assignments')
    assert cfg['cap_height_factor']==.90 and cfg['anchor_ring']==107
    rings=sorted(map(int,cfg['z_offsets']));assert rings==list(range(108,117))
    path=ROOT/'history/queen-mission-020/queen-rebuilt.blend'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==BASELINE_SHA
    with bpy.data.libraries.load(str(path),link=False) as (names,data):
        assert mesh_name in names.meshes;data.meshes=[mesh_name]
    mesh=data.meshes[0];before=read_controls(mesh,controls.shape[1]);bpy.data.meshes.remove(mesh)
    expected=before.copy()
    for key,delta in cfg['z_offsets'].items():
        i=int(key)
        assert abs(delta-(float(before[i,:,2].mean())-cfg['anchor_height'])*(-.10))<1e-6
        expected[i,:,2]+=delta
    assert np.array_equal(controls,expected),'Unrecorded geometry change'
    assert np.array_equal(controls[:108],before[:108]) and np.array_equal(controls[:,:,:2],before[:,:,:2])
    assert hashlib.sha256(controls.tobytes()).hexdigest()==change['control_sha256']
    reduction=float(before[:,:,2].max()-controls[:,:,2].max())
    assert .0378<reduction<.0382
    assert np.all(np.diff(controls[107:,:,2],axis=0)>0)
    tip=float(controls[90:101,:,2].max())
    return {'baseline_sha256':BASELINE_SHA,'changed_rings':rings,'cap_height_factor':.90,
            'all_radii_identical':True,'bowl_and_all_other_controls_identical':True,
            'top_lowering':reduction,'egg_above_tip_before':float(before[:,:,2].max())-tip,
            'egg_above_tip_after':float(controls[:,:,2].max())-tip},before

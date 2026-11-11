"""Verify the accepted radial-only stem/crown refinement against checkpoint 18."""
import hashlib
from pathlib import Path
import bpy
import numpy as np
from refine_socket_flare import read_controls
ROOT=Path(__file__).resolve().parents[2]
BASELINE_SHA='8420d47bbbd8cb86c1eee77e5b326f945fe57b4e3acf7d30e18414f9aa0864c6'

def check(controls,settings,mesh_name):
    change=settings.get('profile_study')
    if not change:return None,controls
    assert change['source_sha256']==BASELINE_SHA
    cfg=change['config']
    assert cfg.get('elevation',54)==54 and cfg.get('axial_scale',1)==1
    assert not cfg.get('z_offsets') and not cfg.get('camera_floor_offset')
    rings=sorted(map(int,cfg['radii']))
    assert rings==list(range(40,49))+list(range(85,91))
    path=ROOT/'history/queen-mission-018/queen-rebuilt.blend'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==BASELINE_SHA
    with bpy.data.libraries.load(str(path),link=False) as (names,data):
        assert mesh_name in names.meshes;data.meshes=[mesh_name]
    mesh=data.meshes[0];before=read_controls(mesh,controls.shape[1]);bpy.data.meshes.remove(mesh)
    expected=before.copy()
    for key,radius in cfg['radii'].items():
        ring=expected[int(key)];ring[:,:2]*=(radius/np.linalg.norm(ring[:,:2],axis=1))[:,None]
    assert np.array_equal(controls,expected),'Controls differ from the recorded radial-only edit'
    assert np.array_equal(controls[:,:,2],before[:,:,2])
    keep=np.ones(len(controls),dtype=bool);keep[rings]=False
    assert np.array_equal(controls[keep],before[keep])
    assert hashlib.sha256(controls.tobytes()).hexdigest()==change['control_sha256']
    maximum=float(np.linalg.norm(controls-before,axis=2).max());assert maximum<.036
    return {'baseline_sha256':BASELINE_SHA,'changed_rings':rings,'all_heights_identical':True,'all_other_controls_identical':True,'maximum_radial_displacement':maximum,'crown_tips_bowl_finial_base_collars_unchanged':True},before

"""Check the small radial collar edit against the accepted checkpoint 19."""
import hashlib
from pathlib import Path
import bpy
import numpy as np
from refine_socket_flare import read_controls

ROOT = Path(__file__).resolve().parents[2]
BASELINE_SHA = 'd5882d44aa0dc3f2f72ea7449f353e530e59888fb3804ef32233544ce6feffb0'

def check(controls, settings, mesh_name):
    change = settings.get('lower_collar_rounding')
    if not change:
        return None, controls
    assert change['source_sha256'] == BASELINE_SHA
    cfg = change['config']
    assert cfg.get('elevation', 54) == 54 and cfg.get('axial_scale', 1) == 1
    assert not cfg.get('z_offsets') and not cfg.get('camera_floor_offset')
    rings = sorted(map(int, cfg['radii']))
    assert rings == list(range(51, 55))
    archive = ROOT / 'history/queen-mission-019/queen-rebuilt.blend'
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == BASELINE_SHA
    with bpy.data.libraries.load(str(archive), link=False) as (names, data):
        assert mesh_name in names.meshes
        data.meshes = [mesh_name]
    mesh = data.meshes[0]
    before = read_controls(mesh, controls.shape[1])
    bpy.data.meshes.remove(mesh)
    expected = before.copy()
    for key, radius in cfg['radii'].items():
        ring = expected[int(key)]
        ring[:, :2] *= (radius / np.linalg.norm(ring[:, :2], axis=1))[:, None]
    assert np.array_equal(controls, expected), 'Controls differ from the recorded radius edit'
    assert np.array_equal(controls[:, :, 2], before[:, :, 2])
    keep = np.ones(len(controls), dtype=bool)
    keep[rings] = False
    assert np.array_equal(controls[keep], before[keep])
    assert hashlib.sha256(controls.tobytes()).hexdigest() == change['control_sha256']
    maximum = float(np.linalg.norm(controls-before, axis=2).max())
    assert maximum < .055
    return {
        'baseline_sha256': BASELINE_SHA, 'changed_rings': rings,
        'all_heights_identical': True, 'all_other_controls_identical': True,
        'maximum_radial_displacement': maximum,
        'base_socket_stem_upper_collars_and_crown_unchanged': True,
    }, before

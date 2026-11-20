"""Verify the exact, documented base-junction edit against checkpoint 12 controls."""
from pathlib import Path
import hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
BASELINE_SHA='2cb513a71cf36e6bbaa3619b95cc53208e1245f9dbefebc745470e582fc11a9b'

def check(controls, settings):
    refinement=settings.get('base_transition_refinement')
    if not refinement:return None
    assert refinement['source_sha256']==BASELINE_SHA
    snapshot=ROOT/'docs/queen-mission/iteration-013/baseline-controls.npz'
    archive=ROOT/'history/queen-mission-012/queen-rebuilt.blend'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==BASELINE_SHA
    data=np.load(snapshot);baseline=data['controls'];assert str(data['source_sha256'])==BASELINE_SHA
    assert baseline.shape==controls.shape and baseline.dtype==np.float32
    seating=settings['finial_seating']
    assert hashlib.sha256(baseline[:107].tobytes()).hexdigest()==seating['unchanged_body_sha256']
    rings=[entry['ring'] for entry in refinement['rings']];assert rings==[26,27,28,29]
    keep=np.ones(len(controls),dtype=bool);keep[rings]=False
    assert np.array_equal(controls[keep],baseline[keep]),'Controls outside the scoped junction changed'
    assert np.array_equal(controls[:,:,2],baseline[:,:,2]),'A control height changed'
    assert hashlib.sha256(controls[keep].tobytes()).hexdigest()==refinement['unchanged_controls_sha256']
    for entry in refinement['rings']:
        i=entry['ring'];radii=np.linalg.norm(controls[i,:,:2],axis=1)
        old_radii=np.linalg.norm(baseline[i,:,:2],axis=1)
        assert np.allclose(radii,entry['new_radius'],atol=1e-6,rtol=0)
        assert 0<float((radii-old_radii).max())<.020
        # A radial edit may not rotate a ring or introduce height variation.
        assert np.allclose(controls[i,:,:2]/radii[:,None],baseline[i,:,:2]/old_radii[:,None],atol=2e-7,rtol=0)
    radii=np.linalg.norm(controls[25:32,:,:2],axis=2).mean(1)
    assert np.all(np.diff(radii)<=1e-6),'The base/socket junction reverses radially'
    return {'baseline_sha256':BASELINE_SHA,'changed_rings':rings,
            'all_other_controls_identical':True,'all_heights_identical':True,
            'maximum_vertex_displacement':float(np.linalg.norm(controls-baseline,axis=2).max()),
            'original_body_hash_verified':True}

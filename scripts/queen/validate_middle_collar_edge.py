"""Verify the three-ring middle-lip edit against the accepted fifteenth controls."""
from pathlib import Path
import hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2]
BASELINE_SHA='8b1c052b8c6960c6faf6760635090a7c081b04e5ad779641a4b9e49433f628c0'
def check(controls,settings):
 refinement=settings.get('middle_collar_edge_refinement')
 if not refinement:return None,controls
 assert refinement['source_sha256']==BASELINE_SHA
 archive=ROOT/'history/queen-mission-015/queen-rebuilt.blend'
 if not archive.exists():archive=ROOT/'models/queen/queen-rebuilt.blend'
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==BASELINE_SHA
 data=np.load(ROOT/'docs/queen-mission/iteration-016/baseline-controls.npz');before=data['controls'];assert str(data['source_sha256'])==BASELINE_SHA
 assert before.dtype==np.float32 and before.shape==controls.shape
 rings=[p['ring'] for p in refinement['rings']];assert rings==[64,65,66]
 keep=np.ones(len(controls),dtype=bool);keep[rings]=False
 assert np.array_equal(controls[keep],before[keep]),'Controls outside middle collar lower bevel changed'
 assert np.array_equal(controls[:,:,2],before[:,:,2]),'A control height changed'
 assert hashlib.sha256(controls[keep].tobytes()).hexdigest()==refinement['unchanged_controls_sha256']
 assert hashlib.sha256(controls[:,:,2].tobytes()).hexdigest()==refinement['all_heights_sha256']
 for p,target in zip(refinement['rings'],[.565,.580,.584]):
  assert p['new_radius']==target
  i=p['ring'];oldr=np.linalg.norm(before[i,:,:2],axis=1);newr=np.linalg.norm(controls[i,:,:2],axis=1)
  assert np.allclose(newr,target,atol=1e-6,rtol=0)
  assert np.allclose(controls[i,:,:2]/newr[:,None],before[i,:,:2]/oldr[:,None],atol=2e-7,rtol=0)
 displacement=float(np.linalg.norm(controls-before,axis=2).max());assert 0<displacement<.01501
 assert np.array_equal(controls[67],before[67])
 return {'baseline_sha256':BASELINE_SHA,'changed_rings':rings,'all_other_controls_identical':True,'all_heights_identical':True,'peak_ring_identical':True,'maximum_vertex_displacement':displacement},before

"""Validate the stacked-collar revision and the regions it must preserve."""
from pathlib import Path
import json
import sys
import bpy
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from validate_seamless_crown import inspect_scene, coordinates, compare_points, require, sha256

ROOT=Path(__file__).resolve().parents[2]
MODEL=ROOT/'models/queen/queen-rebuilt.blend'
BASELINE=ROOT/'history/queen-hires/before-stacked-collars/queen-rebuilt.blend'
REPORT=ROOT/'assets/queen/model-validation.json'
report={'validation':'Stacked collars, manifold queen, and preserved lower body/crown','passed':False}
fingerprints={str(p):(sha256(p),p.stat().st_mtime_ns) for p in (MODEL,BASELINE)}
try:
 bpy.ops.wm.open_mainfile(filepath=str(MODEL),load_ui=False)
 queen=inspect_scene(report)
 current=coordinates(queen)
 with bpy.data.libraries.load(str(BASELINE),link=False) as (src,dst):
  names=[name for name in src.objects if name.startswith('01 Queen')]
  require(len(names)==1,'Expected one baseline queen')
  dst.objects=names
 old=dst.objects[0]
 collection=bpy.data.collections.new('__validation_baseline__')
 bpy.context.scene.collection.children.link(collection)
 collection.objects.link(old)
 bpy.context.view_layer.update()
 previous=coordinates(old)
 require(current.shape==previous.shape,'Unexpected control topology change')
 lower=previous[:,2]<2.30
 report['preserved_base_socket_lower_stem']=compare_points(current[lower],previous[lower])
 require(report['preserved_base_socket_lower_stem']['passed'],'Lower body changed unexpectedly')
 n=int(queen['ring_segments'])
 crown_start=int(queen['body_preserved_ring_count'])*n
 report['preserved_crown_bowl_finial']=compare_points(current[crown_start:],previous[crown_start:])
 require(report['preserved_crown_bowl_finial']['passed'],'Crown flare, bowl or finial changed')
 new_rings=current.reshape((-1,n,3))
 old_rings=previous.reshape((-1,n,3))
 centers=lambda points:np.array([points[[55,56],:,2].mean(),points[[67,68],:,2].mean(),points[[78,79],:,2].mean()])
 current_centers=centers(new_rings);old_centers=centers(old_rings)
 gaps=np.diff(current_centers)
 require(np.all(gaps>.075) and np.all(gaps<.11),'Collar centers are not a close, ordered stack')
 require(np.all(gaps/np.diff(old_centers)<.65),'Collar spacing did not materially decrease')
 # The sole starts with three coplanar rings; all subsequent rings rise.
 require(np.all(np.diff(new_rings[:89,:,2].mean(axis=1))>=-1e-7),'Turned body rings overlap vertically')
 report['collar_centers']={'previous':old_centers.tolist(),'current':current_centers.tolist(),'center_spacing':gaps.tolist(),'spacing_reduction_percent':((1-gaps/np.diff(old_centers))*100).tolist()}
 spacers=[float(new_rings[63,:,2].mean()-new_rings[60,:,2].mean()),float(new_rings[75,:,2].mean()-new_rings[72,:,2].mean())]
 require(all(0<s<.02 for s in spacers),'Exposed collar spacers remain too tall')
 report['exposed_spacer_heights']=spacers
 report['source_sha256']=sha256(MODEL)
 report['baseline_sha256']=sha256(BASELINE)
 report['authorized_changed_region']='Upper stem, three collar plates and their junction with the crown body'
 report['passed']=True
except Exception as error:
 report['error']=f'{type(error).__name__}: {error}'
finally:
 for name,before in fingerprints.items():
  p=Path(name)
  unchanged=(sha256(p),p.stat().st_mtime_ns)==before
  if not unchanged:report['passed']=False
  report.setdefault('source_files_unchanged',{})[name]=unchanged
 REPORT.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if not report['passed']:raise SystemExit(1)

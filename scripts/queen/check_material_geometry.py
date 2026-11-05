"""Verify unchanged geometry/UVs, or an explicitly requested, narrowly scoped radial edit."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
def read(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
 o=editable_mesh(bpy.context.scene)
 co=np.empty(len(o.data.vertices)*3,dtype=np.float32);o.data.vertices.foreach_get('co',co)
 uv=np.empty(len(o.data.loops)*2,dtype=np.float32);o.data.uv_layers['Pigment atlas'].data.foreach_get('uv',uv)
 loops=np.empty(len(o.data.loops),dtype=np.int32);o.data.loops.foreach_get('vertex_index',loops)
 return co,uv,loops
p=argparse.ArgumentParser();p.add_argument('--baseline',default='history/queen-mission-003/queen-rebuilt.blend');p.add_argument('--current',default='models/queen/queen-rebuilt.blend');p.add_argument('--allow-base-transition',action='store_true');p.add_argument('--allow-middle-collar-edge',action='store_true');p.add_argument('--report-dir',default='assets/queen')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
baseline=ROOT/args.baseline;current=ROOT/args.current
a=read(baseline);b=read(current)
report={'baseline':args.baseline,'current':args.current,'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'current_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),'control_vertices_identical':bool(np.array_equal(a[0],b[0])),'atlas_control_uvs_identical':bool(np.array_equal(a[1],b[1])),'topology_identical':bool(np.array_equal(a[2],b[2]))}
assert not (args.allow_base_transition and args.allow_middle_collar_edge)
if args.allow_middle_collar_edge:
 from validate_middle_collar_edge import check as check_middle_edge
 scoped,before=check_middle_edge(b[0].reshape(-1,192,3),json.loads(bpy.context.scene['mission_material_config']))
 assert scoped and report['baseline_sha256']==scoped['baseline_sha256']
 assert np.array_equal(a[0].reshape(-1,192,3),before)
 report['scoped_geometry_change']=scoped
elif args.allow_base_transition:
 from validate_base_transition import check as check_base_transition
 scoped=check_base_transition(b[0].reshape(-1,192,3),json.loads(bpy.context.scene['mission_material_config']))
 assert scoped and report['baseline_sha256']==scoped['baseline_sha256']
 keep=np.ones(len(a[0])//(192*3),dtype=bool);keep[26:30]=False
 assert np.array_equal(a[0].reshape(-1,192,3)[keep],b[0].reshape(-1,192,3)[keep])
 report['scoped_geometry_change']=scoped
else:
 assert report['control_vertices_identical'],report
assert report['atlas_control_uvs_identical'] and report['topology_identical'],report
report['passed']=True
(ROOT/args.report_dir/'material-geometry-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

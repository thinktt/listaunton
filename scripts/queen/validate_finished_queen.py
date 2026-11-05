"""Check the delivered queen mesh, material, camera and chosen relative size."""
from pathlib import Path
import json, math, hashlib, argparse, sys
import bpy, bmesh
import numpy as np

root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from validate_render_receivers import check as check_receivers
from validate_base_transition import check as check_base_transition
p=argparse.ArgumentParser();p.add_argument('--blend',type=Path,default=root/'models/queen/queen-rebuilt.blend');p.add_argument('--report-dir',type=Path,default=root/'assets/queen')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
model=args.blend
fit=json.loads((root/'assets/queen/finish-fit.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
scene=bpy.context.scene
obj=editable_mesh(scene)
camera=scene.camera
back=camera.matrix_world.to_3x3()@__import__('mathutils').Vector((0,0,1))
elevation=math.degrees(math.atan2(back.z, math.hypot(back.x,back.y)))
assert abs(elevation-54)<1e-4,elevation
assert obj.data.materials and 'Walnut' in obj.data.materials[0].name
assert obj.data.materials[0].use_nodes
controls=np.empty(len(obj.data.vertices)*3,dtype=np.float32)
obj.data.vertices.foreach_get('co',controls);controls=controls.reshape((-1,192,3))
z=controls[:,:,2].mean(1)
assert np.all(np.diff(z[:89])>=-1e-5),'Turned body rings reverse direction'
assert scene.get('continuous_crown') and scene.get('crown_tip_count')==8
graph=bpy.context.evaluated_depsgraph_get();evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
bm=bmesh.new();bm.from_mesh(mesh)
boundary=sum(e.is_boundary for e in bm.edges)
nonmanifold=sum(not e.is_manifold for e in bm.edges)
volume=bm.calc_volume(signed=True)
assert boundary==0 and nonmanifold==0 and volume>0,(boundary,nonmanifold,volume)
co=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',co);co=co.reshape(-1,3)
height=float(np.ptp(co[:,2]));low=co[co[:,2]<=co[:,2].min()+height*.25]
diameter=float((np.ptp(low[:,0])+np.ptp(low[:,1]))/2)
ratio=height/diameter
# The owner's smaller, deeper finial intentionally lowers the maximum height.
# Keep the original tolerance around the adjusted target. All other controls
# remain identical except the four separately validated base-junction rings.
material_settings=json.loads(scene.get('mission_material_config','{}'))
seating=material_settings.get('finial_seating')
base_transition=check_base_transition(controls,material_settings)
adjusted_target=fit['target_height_to_base_width']
if seating:
    assert seating['height_factor']==.90 and seating['radial_factor']==.96
    if not base_transition:
        assert hashlib.sha256(controls[:107].astype(np.float32).tobytes()).hexdigest()==seating['unchanged_body_sha256']
    assert abs(seating['top_lowering']-.0467)<.00001
    adjusted_target-=seating['top_lowering']/diameter
assert abs(ratio-adjusted_target)<.015,(ratio,adjusted_target)
report={'passed':True,'source_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),
        'camera_elevation_degrees':elevation,'camera_type':camera.data.type,
        'height':height,'base_diameter':diameter,'height_to_base_diameter':ratio,
        'target_height_to_base_diameter':fit['target_height_to_base_width'],
        'target_queen_to_king':fit['target_queen_to_king_height'],
        'material':obj.data.materials[0].name,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,
        'signed_volume':volume,'crown_tips':8,'body_rings_monotonic':True}
report['finial_seating']=seating
report['base_transition']=base_transition
report['adjusted_height_target']=adjusted_target
report['render_receivers']=check_receivers(scene,obj)
for name in ('finish-validation.json','model-validation.json'):
    args.report_dir.mkdir(parents=True,exist_ok=True)
    (args.report_dir/name).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
bm.free();evaluated.to_mesh_clear()

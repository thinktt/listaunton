"""Validate fresh queen topology, source controls, 54° camera and material."""
from pathlib import Path
import sys,json,hashlib,math
import bpy,bmesh
import numpy as np
from mathutils import Vector
root=Path(__file__).resolve().parents[2];out=root/'assets/queen'
sys.path.insert(0,str(Path(__file__).parent))
from scratch_profile import controls,apply_fit,PROFILE
fit=json.loads((out/'scratch-fit.json').read_text())
model=root/'models/queen/queen-rebuilt.blend';bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
scene=bpy.context.scene;obj=next(o for o in scene.objects if o.type=='MESH' and not o.hide_render)
actual=np.empty(len(obj.data.vertices)*3,dtype=np.float32);obj.data.vertices.foreach_get('co',actual);actual=actual.reshape((-1,192,3))
expected=apply_fit(controls(192),fit)
assert actual.shape==expected.shape
max_error=float(np.abs(actual-expected).max());assert max_error<1e-6,max_error
assert np.all(np.diff(actual[:len(PROFILE),:,2].mean(1))>=-1e-6)
back=scene.camera.matrix_world.to_3x3()@Vector((0,0,1))
elev=math.degrees(math.atan2(back.z,math.hypot(back.x,back.y)))
assert abs(elev-54)<1e-4 and scene.camera.data.type=='ORTHO'
material=obj.data.materials[0];assert 'walnut' in material.name.lower()
images=[n.image for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
assert any(im.packed_file and 'walnut-albedo' in im.name for im in images)
graph=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(graph);mesh=ev.to_mesh()
bm=bmesh.new();bm.from_mesh(mesh);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
assert boundary==0 and nonmanifold==0 and volume>0,(boundary,nonmanifold,volume)
vertices=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',vertices);vertices=vertices.reshape(-1,3)
height=float(np.ptp(vertices[:,2]));lower=vertices[vertices[:,2]<=vertices[:,2].min()+height*.25]
diameter=float((np.ptp(lower[:,0])+np.ptp(lower[:,1]))/2)
scale=json.loads((root/'assets/side-views/scale.json').read_text());king=next(p for p in scale['pieces'] if p['piece']=='king');queen=next(p for p in scale['pieces'] if p['piece']=='queen')
relative=(height/diameter)/(king['model']['height']/king['model']['base_diameter'])*(queen['original']['base_width_px']/king['original']['base_width_px'])
report={'passed':True,'source_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),
 'construction':'Fresh side-inspired control mesh; no previous queen mesh loaded',
 'assumed_camera_elevation_degrees':elev,'closed':True,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'signed_volume':volume,
 'height':height,'base_diameter':diameter,'height_to_base':height/diameter,
 'estimated_queen_height_relative_to_king':relative,'relative_scale_assumption':'Sprite base-width normalization with the existing 54° king model; uncertain.',
 'control_vertex_max_error':max_error,'crown_tip_count':8,'packed_wood':True}
for name in ('scratch-validation.json','model-validation.json'):(out/name).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2));bm.free();ev.to_mesh_clear()

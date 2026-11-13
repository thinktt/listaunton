"""Validate saved material trials against the accepted rook's actual surface."""
from pathlib import Path
import sys,json,hashlib,math
import bpy,bmesh,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from render_regions import closed_body,validate as validate_receivers
args=sys.argv[sys.argv.index('--')+1:]
variant=args[0];out=ROOT/'build/rook-mission'/variant
out.mkdir(parents=True,exist_ok=True)
surfaces={}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();parts={};arrays={}
    for ob in s.objects:
        if ob.type!='MESH' or ob.get('rook_render_receiver'):continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        positions=np.array([v.co[:] for v in me.vertices],np.float32)
        faces=np.array([t.vertices[:] for t in me.loop_triangles],np.int32)
        bm=bmesh.new();bm.from_mesh(me)
        assert all(e.is_manifold for e in bm.edges),ob.name
        volume=bm.calc_volume(signed=True);assert volume>0
        control=np.array([v.co[:] for v in ob.data.vertices],np.float32)
        normals=np.array([row.vector[:] for row in me.corner_normals],np.float32)
        arrays[ob.name]=(positions,normals)
        parts[ob.name]={'control_position_hash':hashlib.sha256(control.tobytes()).hexdigest(),'position_hash':hashlib.sha256(positions.tobytes()).hexdigest(),'triangle_hash':hashlib.sha256(faces.tobytes()).hexdigest(),'volume':volume,'hidden_render':ob.hide_render,'matrix':list(map(list,ob.matrix_world))}
        bm.free();ev.to_mesh_clear()
    surfaces[str(path)]=arrays;c=s.camera
    return {'parts':parts,'camera':{'matrix':list(map(list,c.matrix_world)),'type':c.data.type,'scale':c.data.ortho_scale,'shift':[c.data.shift_x,c.data.shift_y]},'resolution':[s.render.resolution_x,s.render.resolution_y]}
baseline=Path(args[args.index('--baseline')+1]) if '--baseline' in args else ROOT/'models/rook/rook-rebuilt.blend'
expected=snapshot(baseline)
trial=Path(args[args.index('--model')+1]) if '--model' in args else out/'rook.blend'
actual=snapshot(trial)
(out/'geometry-snapshots.json').write_text(json.dumps({'expected':expected,'actual':actual},indent=2))
assert actual['camera']==expected['camera'] and actual['resolution']==expected['resolution']
assert actual['parts'].keys()==expected['parts'].keys()
precision={}
for name,before in expected['parts'].items():
    after=actual['parts'][name]
    for key in ['control_position_hash','triangle_hash','hidden_render','matrix']:assert before[key]==after[key],(name,key)
    a,an=surfaces[str(baseline)][name];b,bn=surfaces[str(trial)][name]
    assert a.shape==b.shape and an.shape==bn.shape
    dp=float(np.max(np.abs(a-b)));dn=float(np.max(np.abs(an-bn)))
    assert dp<=1e-6 and dn<=2e-5,(name,dp,dn)
    assert abs(before['volume']-after['volume'])<1e-7
    precision[name]={'max_position_delta':dp,'max_normal_component_delta':dn}
s=bpy.context.scene
body=closed_body(s)
receiver_report=validate_receivers(s)
mat=body.data.materials[0]
surface=mat.node_tree.nodes.get('Material Output').inputs['Surface'].links[0].from_node
assert surface.type=='BSDF_PRINCIPLED'
assert surface.inputs['Emission Strength'].default_value==0
images=[node.image for node in mat.node_tree.nodes if node.type=='TEX_IMAGE']
assert len(images)>=2
for im in images:
    assert im.packed_file
    a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);assert np.isfinite(a).all()
if s.get('rook_pigment_uv'):
    for ob in s.objects:
        if ob.type!='MESH' or ob.get('rook_render_receiver'):continue
        uv=ob.data.uv_layers.get(s['rook_pigment_uv']);assert uv
        values=np.array([row.uv[:] for row in uv.data]);assert np.isfinite(values).all()
        assert values.min()>=0 and values.max()<=1
report={'geometry_camera_identical':True,'closed_positive_components':len(actual['parts']),'model_sha256':digest(trial),'accepted_sha256':digest(baseline),'packed_images':len(images),'packed_float_images':sum(im.is_float for im in images),'real_principled_surface':True,'atlas_uvs_checked':bool(s.get('rook_pigment_uv')),'source_references':{name:digest(ROOT/'assets/rook'/name) for name in ['ref.png','original.png','original-white.png']},'scope':'Geometry, evaluated topology, component visibility, object transforms, saved reference camera and dimensions, packed texture finiteness, and actual BSDF surface. Not a visual-match certificate.'}
report['render_receivers']=receiver_report
report['geometry_camera_identical']=actual==expected
report['control_and_camera_exact']=True
report['evaluated_surface_precision']=precision
report['precision_note']='UV layers alter subdivision floating-point evaluation slightly; controls and evaluated triangle indices stay byte-exact. Position tolerance 1e-6 model units, normal component 2e-5, volume 1e-7. Actual deltas reported above.'
(out/'validation.json').write_text(json.dumps(report,indent=2))
print('ROOK_MATERIAL_VALIDATION',json.dumps(report))

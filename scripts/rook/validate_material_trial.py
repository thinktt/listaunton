"""Validate saved material trials against the accepted rook's actual surface."""
from pathlib import Path
import sys,json,hashlib,math
import bpy,bmesh,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
args=sys.argv[sys.argv.index('--')+1:]
variant=args[0];out=ROOT/'build/rook-mission'/variant
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
    s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();parts={}
    for ob in s.objects:
        if ob.type!='MESH':continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
        positions=np.array([v.co[:] for v in me.vertices],np.float32)
        faces=np.array([t.vertices[:] for t in me.loop_triangles],np.int32)
        bm=bmesh.new();bm.from_mesh(me)
        assert all(e.is_manifold for e in bm.edges),ob.name
        volume=bm.calc_volume(signed=True);assert volume>0
        parts[ob.name]={'position_hash':hashlib.sha256(positions.tobytes()).hexdigest(),'triangle_hash':hashlib.sha256(faces.tobytes()).hexdigest(),'volume':volume,'hidden_render':ob.hide_render,'matrix':list(map(list,ob.matrix_world))}
        bm.free();ev.to_mesh_clear()
    c=s.camera
    return {'parts':parts,'camera':{'matrix':list(map(list,c.matrix_world)),'type':c.data.type,'scale':c.data.ortho_scale,'shift':[c.data.shift_x,c.data.shift_y]},'resolution':[s.render.resolution_x,s.render.resolution_y]}
baseline=ROOT/'models/rook/rook-rebuilt.blend';expected=snapshot(baseline)
trial=out/'rook.blend';actual=snapshot(trial)
assert actual==expected,'Geometry or reference camera changed in material-only study'
s=bpy.context.scene
body=next(o for o in s.objects if o.type=='MESH' and not o.hide_render)
mat=body.data.materials[0]
surface=mat.node_tree.nodes.get('Material Output').inputs['Surface'].links[0].from_node
assert surface.type=='BSDF_PRINCIPLED'
assert surface.inputs['Emission Strength'].default_value==0
images=[node.image for node in mat.node_tree.nodes if node.type=='TEX_IMAGE']
assert len(images)==2
for im in images:
    assert im.packed_file and im.is_float
    a=np.empty(len(im.pixels),np.float32);im.pixels.foreach_get(a);assert np.isfinite(a).all()
report={'geometry_camera_identical':True,'closed_positive_components':len(actual['parts']),'model_sha256':digest(trial),'accepted_sha256':digest(baseline),'packed_float_images':len(images),'real_principled_surface':True,'source_references':{name:digest(ROOT/'assets/rook'/name) for name in ['ref.png','original.png','original-white.png']},'scope':'Geometry, evaluated topology, component visibility, object transforms, saved reference camera and dimensions, packed texture finiteness, and actual BSDF surface. Not a visual-match certificate.'}
(out/'validation.json').write_text(json.dumps(report,indent=2))
print('ROOK_MATERIAL_VALIDATION',json.dumps(report))

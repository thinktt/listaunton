"""Validate light receiver copies against the closed editable rook surface."""
import bpy,numpy as np,hashlib

def closed_body(scene):
    tagged=[o for o in scene.objects if o.type=='MESH' and o.get('rook_editable_control')]
    if tagged:
        assert len(tagged)==1
        return tagged[0]
    visible=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
    assert len(visible)==1
    return visible[0]

def face_records(mesh):
    uv=np.array([v.uv[:] for v in mesh.uv_layers['Pigment atlas'].data],np.float32)
    co=np.array([v.co[:] for v in mesh.vertices],np.float32)
    normals=np.array([v.vector[:] for v in mesh.corner_normals],np.float32)
    lv=np.array([v.vertex_index for v in mesh.loops]);records={}
    for face in mesh.polygons:
        ids=np.array(list(face.loop_indices));rows=co[lv[ids]].copy();rows[rows==0]=0
        order=np.lexsort((rows[:,2],rows[:,1],rows[:,0]));key=hashlib.sha256(rows[order].tobytes()).hexdigest()
        assert key not in records
        records[key]=(normals[ids][order],uv[ids][order])
    return records

def validate(scene):
    parts=[o for o in scene.objects if o.get('rook_render_receiver')]
    if not parts:return None
    body=closed_body(scene);assert body.hide_render
    graph=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(graph);mesh=ev.to_mesh();expected=face_records(mesh);ev.to_mesh_clear()
    actual={};maximum=0;uv_error=0
    for ob in parts:
        assert not ob.hide_render and ob.matrix_world==body.matrix_world
        assert list(ob.data.materials)==list(body.data.materials)
        for key,(normals,uv) in face_records(ob.data).items():
            assert key not in actual and key in expected,(ob.name,key,'duplicate' if key in actual else 'missing')
            before,old_uv=expected[key]
            assert normals.shape==before.shape and uv.shape==old_uv.shape
            uv_error=max(uv_error,float(np.max(np.abs(uv-old_uv))))
            maximum=max(maximum,float(np.max(np.abs(normals-before))));actual[key]=True
    assert actual.keys()==expected.keys()
    # Blender custom-normal encoding is quantized; report it rather than claim exactness.
    assert maximum<.001
    # Reopened depth-edited Boolean surfaces show up to 1.1920929e-7 UV roundoff.
    # Bound stays below 0.000615 texel at 3072px; geometry coverage stays exact.
    assert uv_error<=2e-7, ("receiver UV roundoff",uv_error)
    foot=bpy.data.objects.get('Rook foot strip')
    if foot:
        linked=foot.light_linking.receiver_collection
        assert linked and {o.get('rook_render_receiver') for o in linked.objects}=={'foot'}
        assert foot.visible_glossy and not foot.visible_diffuse
    shoulder=bpy.data.objects.get('Rook shoulder strip')
    if shoulder:
        assert shoulder.light_linking.receiver_collection
        assert {o.get('rook_render_receiver') for o in shoulder.light_linking.receiver_collection.objects}=={'shoulder'}
        assert shoulder.visible_glossy and not shoulder.visible_diffuse
    floor=bpy.data.objects.get('Rook floor-edge strip')
    if floor:
        linked=floor.light_linking.receiver_collection
        assert linked and {o.get('rook_render_receiver') for o in linked.objects}=={'floor_edge'}
        assert floor.visible_glossy and not floor.visible_diffuse
    return {'parts':len(parts),'faces':len(expected),'all_faces_once':True,'positions_exact':True,'maximum_uv_error':uv_error,'uv_tolerance':2e-7,'same_material':True,'maximum_normal_component_error':maximum,'normal_tolerance':.001,'closed_control_retained':True,'foot_light_receiver_only':bool(foot),'shoulder_light_receiver_only':bool(shoulder),'floor_light_receiver_only':bool(floor)}

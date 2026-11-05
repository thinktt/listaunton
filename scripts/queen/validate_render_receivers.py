"""Verify optional render receivers preserve the closed editable surface."""
import hashlib,json
import bpy,numpy as np

def records(mesh):
    co=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',co);co=co.reshape(-1,3)
    indices=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',indices)
    uv=np.empty(len(mesh.loops)*2,dtype=np.float32);mesh.uv_layers['Pigment atlas'].data.foreach_get('uv',uv);uv=uv.reshape(-1,2)
    rows=np.ascontiguousarray(np.concatenate((co[indices],uv),axis=1))
    normals=np.empty(len(mesh.loops)*3,dtype=np.float32);mesh.corner_normals.foreach_get('vector',normals);normals=normals.reshape(-1,3)
    faces=[hashlib.sha256(rows[p.loop_start:p.loop_start+p.loop_total].tobytes()).digest() for p in mesh.polygons]
    mesh.calc_loop_triangles()
    return rows,normals,faces,len(mesh.loop_triangles)

def check(scene,control):
    parts=[o for o in scene.objects if o.type=='MESH' and o.get('mission_render_region')]
    if not parts:return {'used':False}
    assert control.hide_render
    assert {o['mission_render_region'] for o in parts}=={'turned-body','finial'}
    for part in parts:
        assert not part.hide_render and not part.modifiers
        assert part.matrix_world==control.matrix_world
        assert part.data.materials[0]==control.data.materials[0]
    levels=[(m,m.levels) for m in control.modifiers if m.type=='SUBSURF']
    for modifier,_ in levels:modifier.levels=modifier.render_levels
    bpy.context.view_layer.update()
    evaluated=control.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    original=records(mesh)
    received=[records(part.data) for part in parts]
    rows=np.concatenate([r[0] for r in received]);normals=np.concatenate([r[1] for r in received])
    faces=[f for r in received for f in r[2]]
    assert sorted(faces)==sorted(original[2]),'Receiver faces or atlas UVs diverged from the editable mesh'
    assert sum(r[3] for r in received)==original[3]
    source_keys=original[0].view('V20').reshape(-1);receiver_keys=rows.view('V20').reshape(-1)
    source_order=np.argsort(source_keys,kind='stable');receiver_order=np.argsort(receiver_keys,kind='stable')
    assert np.array_equal(source_keys[source_order],receiver_keys[receiver_order])
    normal_error=abs(original[1][source_order]-normals[receiver_order])
    assert float(normal_error.max())<.0002,float(normal_error.max())
    cfg=json.loads(scene['mission_material_config'])['finial_receiver_isolation']
    for name in cfg['excluded_reflectors']:
        receiver=bpy.data.objects[name].light_linking.receiver_collection
        assert receiver and {o.get('mission_render_region') for o in receiver.objects}=={'turned-body'}
    result={'used':True,'receivers':len(parts),'surface_faces_and_atlas_uvs_exact':True,
            'triangles':original[3],'custom_normal_max_component_error':float(normal_error.max()),
            'custom_normal_mean_component_error':float(normal_error.mean()),
            'materials_shared':True,'excluded_reflector_count':len(cfg['excluded_reflectors']),
            'closed_editable_control_retained':True}
    evaluated.to_mesh_clear()
    for modifier,level in levels:modifier.levels=level
    return result

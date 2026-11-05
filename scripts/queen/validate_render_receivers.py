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
    settings=json.loads(scene['mission_material_config'])
    socket=settings.get('stem_socket_receiver_isolation')
    collar=settings.get('collar_receiver_isolation')
    subdivisions=settings.get('subdivided_collar_receivers')
    if settings.get('glossy_interreflection'):
        assert scene.cycles.glossy_bounces==settings['glossy_interreflection']['glossy_bounces']==0
    expected_parts={'turned-body','stem-socket','finial'} if socket else {'turned-body','finial'}
    if collar:
        assert socket
        expected_parts.update(subdivisions['regions'] if subdivisions else ['collars'])
    assert {o['mission_render_region'] for o in parts}==expected_parts
    if socket:
        assert socket['z_interval']==[.83,2.78]
        controls=np.empty(len(control.data.vertices)*3,dtype=np.float32)
        control.data.vertices.foreach_get('co',controls)
        assert hashlib.sha256(controls.tobytes()).hexdigest()==socket['closed_controls_sha256']
        region=next(o for o in parts if o['mission_render_region']=='stem-socket')
        centers=np.array([tuple(p.center) for p in region.data.polygons])
        assert np.all((centers[:,2]>=.83)&(centers[:,2]<2.78))
    if collar:
        assert collar['z_interval']==[2.78,3.34]
        assert hashlib.sha256(controls.tobytes()).hexdigest()==collar['closed_controls_sha256']
        regions=subdivisions['regions'] if subdivisions else {'collars':[2.78,3.34]}
        if subdivisions:
            assert regions=={'lower-collar':[2.78,2.97],'middle-collar':[2.97,3.16],'upper-collar':[3.16,3.34]}
            assert subdivisions['nonshadowing_fills']==[f'Collar crescent {i:02d}' for i in range(6,17 if settings.get('full_collar_fill') else 9)]
            for name in subdivisions['nonshadowing_fills']:assert not bpy.data.objects[name].data.use_shadow
        for name,(lo,hi) in regions.items():
            region=next(o for o in parts if o['mission_render_region']==name)
            centers=np.array([tuple(p.center) for p in region.data.polygons])
            assert np.all((centers[:,2]>=lo)&(centers[:,2]<hi))
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
    cfg=settings['finial_receiver_isolation']
    specifications={spec['name']:spec for spec in settings['lights']}
    for name in cfg['excluded_reflectors']:
        receiver=bpy.data.objects[name].light_linking.receiver_collection
        expected={'turned-body'}
        if socket:
            if name.startswith('Socket crescent '):expected={'stem-socket'}
            elif name not in socket['excluded_reflectors']:expected={'turned-body','stem-socket'}
            if collar:
                if name.startswith(('Collar crescent ','Collar retained ')):expected={'collars'}
                else:
                    if 'turned-body' in expected:expected.add('collars')
                    if name in collar['excluded_reflectors']:expected.discard('collars')
            if subdivisions and 'collars' in expected:
                expected.remove('collars');expected.update(subdivisions['regions'])
                if name.startswith('Collar crescent '):
                    index=int(name.split()[-1]);expected={'upper-collar' if index<6 else 'middle-collar' if index<17 else 'lower-collar'}
                    assert bpy.data.objects[name].data.use_shadow==(name not in subdivisions['nonshadowing_fills'])
            assert set(specifications[name]['receiver_parts'])==expected
        assert receiver and {o.get('mission_render_region') for o in receiver.objects}==expected
        assert 'finial' not in expected
    result={'used':True,'receivers':len(parts),'surface_faces_and_atlas_uvs_exact':True,
            'triangles':original[3],'custom_normal_max_component_error':float(normal_error.max()),
            'custom_normal_mean_component_error':float(normal_error.mean()),
            'materials_shared':True,'excluded_reflector_count':len(cfg['excluded_reflectors']),
            'closed_editable_control_retained':True,
            'collar_control_hash_verified':bool(collar) if collar else None,
            'collar_controls_unchanged':bool(collar) and not bool(settings.get('middle_collar_edge_refinement')) if collar else None,
            'nonshadowing_collar_fills':subdivisions['nonshadowing_fills'] if subdivisions else [],
            'receiver_regions':sorted(expected_parts),'socket_controls_unchanged':bool(socket) if socket else None}
    evaluated.to_mesh_clear()
    for modifier,level in levels:modifier.levels=level
    return result

"""Validate exact derived surfaces, every UV/float attribute, normals and links."""
import hashlib
import bpy,numpy as np
from render_regions import controls

def records(mesh):
    indices=np.array([l.vertex_index for l in mesh.loops]);values=[np.array([v.co[:] for v in mesh.vertices],dtype=np.float32)[indices]]
    schema=[]
    for layer in mesh.uv_layers:
        schema.append(('uv',layer.name));values.append(np.array([v.uv[:] for v in layer.data],dtype=np.float32))
    for a in mesh.attributes:
        if a.data_type=='FLOAT' and a.domain in ('POINT','CORNER') and not a.name.startswith('.'):
            schema.append((a.domain,a.name));value=np.array([v.value for v in a.data],dtype=np.float32);values.append((value[indices] if a.domain=='POINT' else value)[:,None])
    rows=np.ascontiguousarray(np.concatenate(values,axis=1));normals=np.array([n.vector[:] for n in mesh.corner_normals],dtype=np.float32)
    faces=[hashlib.sha256(rows[p.loop_start:p.loop_start+p.loop_total].tobytes()).digest() for p in mesh.polygons];mesh.calc_loop_triangles()
    return rows,normals,faces,len(mesh.loop_triangles),schema

def check(scene):
    parts=[o for o in scene.objects if o.get('king_render_region')]
    if not parts:return {'used':False}
    split=bool(scene.get('king_split_flare',False))
    socket=bool(scene.get('king_split_socket',False))
    seam=bool(scene.get('king_split_socket_seam',False));assert not seam or socket
    expected_regions=({'foot','lower-flare','upper-flare','upper-body'} if split else {'foot','flare','upper-body'})
    if socket:expected_regions.add('socket')
    if seam:expected_regions.add('socket-seam')
    assert {o['king_render_region'] for o in parts}==expected_regions
    body=next(o for o in controls(scene) if 'body' in o.name);assert body.hide_render and body.get('king_editable_control')
    for part in parts:
        assert not part.hide_render and not part.modifiers and part.matrix_world==body.matrix_world
        assert part.data.materials[0]==body.data.materials[0]
        if seam and part['king_render_region'] in ('socket','socket-seam'):
            me=part.data;rings=np.array([a.value for a in me.attributes['King profile ring'].data],dtype=np.float32)
            loops=np.array([l.vertex_index for l in me.loops]);starts=np.array([p.loop_start for p in me.polygons]);counts=np.array([p.loop_total for p in me.polygons])
            mean=np.add.reduceat(rings[loops],starts)/counts;inside=(mean>=26.55)&(mean<27.25)
            assert inside.all() if part['king_render_region']=='socket-seam' else not inside.any()
    levels=[(m,m.levels) for m in body.modifiers if m.type=='SUBSURF']
    for m,_ in levels:m.levels=m.render_levels
    bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();original=records(me);received=[records(o.data) for o in parts]
    assert all(r[4]==original[4] for r in received)
    assert sorted(f for r in received for f in r[2])==sorted(original[2]),'Receiver surface/UV/attributes diverged'
    assert sum(r[3] for r in received)==original[3]
    rows=np.concatenate([r[0] for r in received]);normals=np.concatenate([r[1] for r in received]);dtype='V'+str(original[0].shape[1]*4)
    a=original[0].view(dtype).reshape(-1);b=rows.view(dtype).reshape(-1);ia=np.argsort(a,kind='stable');ib=np.argsort(b,kind='stable');assert np.array_equal(a[ia],b[ib]);error=float(abs(original[1][ia]-normals[ib]).max());assert error<.0002,error
    routes={}
    for light in scene.objects:
        if light.type!='LIGHT' or not light.light_linking.receiver_collection:continue
        names={o.get('king_render_region') or o.name for o in light.light_linking.receiver_collection.objects};routes[light.name]=sorted(names)
        if light.name in ('Upper varnish','Front varnish'):
            expected={'upper-body','socket'} if socket and not scene.get('king_socket_broad_excluded',False) else {'upper-body'}
            if seam and 'socket' in expected:expected.add('socket-seam')
            assert names==expected,(light.name,names,expected)
        if light.name.startswith('Base '):
            expected={'flare'}
            if split:
                expected=({'upper-flare'} if light.name=='Base upper focused' else ({'lower-flare'} if light.name.startswith('Base lower shaped ') else {'lower-flare','upper-flare'}))
            assert names==expected,(light.name,names,expected)
        if light.name.startswith('Foot '):assert names=={'foot'}
        if light.name.startswith('Socket '):
            expected={'socket','socket-seam'} if seam else {'socket'}
            if seam and light.name.startswith('Socket seam ') and scene.get('king_socket_seam_lights_confined',False):expected={'socket-seam'}
            assert socket and names==expected,(light.name,names,expected)
        if light.name.startswith('Cross '):assert not any(o.get('king_render_region') for o in light.light_linking.receiver_collection.objects)
    ev.to_mesh_clear()
    for m,level in levels:m.levels=level
    return dict(used=True,receiverCount=len(parts),exactSurfaceFacesUvsFloatAttributes=True,triangles=original[3],normalMaxError=error,materialsShared=True,closedControlRetained=True,lightRoutes=routes)

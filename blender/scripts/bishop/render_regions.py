"""Exact evaluated bishop receivers; retain the closed body as editable control."""
import bpy
import numpy as np

BODY='Bishop - continuous turned body'
BUTTON='Bishop - domed button finial'

def partition_socket(scene,z_min=1.20,z_max=1.38):
    assert 0<z_min<z_max
    assert not any(o.get('bishop_render_region') for o in scene.objects),'Regenerate deliberately; never layer stale receivers.'
    obj=bpy.data.objects[BODY]
    assert not obj.hide_render
    for mod in obj.modifiers:
        if mod.type=='SUBSURF':assert mod.levels==mod.render_levels
    bpy.context.view_layer.update();ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    xyz=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',xyz);xyz=xyz.reshape(-1,3)
    vi=np.empty(len(mesh.loops),dtype=np.int32);mesh.loops.foreach_get('vertex_index',vi)
    starts=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_start',starts)
    counts=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('loop_total',counts)
    centers=np.add.reduceat(xyz[vi],starts,axis=0)/counts[:,None]
    labels=((centers[:,2]>=z_min)&(centers[:,2]<z_max)).astype(np.int32)
    normal=np.empty(len(mesh.loops)*3,dtype=np.float32);mesh.corner_normals.foreach_get('vector',normal);normal=normal.reshape(-1,3)
    smooth=np.empty(len(mesh.polygons),dtype=bool);mesh.polygons.foreach_get('use_smooth',smooth)
    material=np.empty(len(mesh.polygons),dtype=np.int32);mesh.polygons.foreach_get('material_index',material)
    uv={}
    for layer in mesh.uv_layers:
        values=np.empty(len(mesh.loops)*2,dtype=np.float32);layer.data.foreach_get('uv',values);uv[layer.name]=values.reshape(-1,2)
    floats={}
    for attr in mesh.attributes:
        if attr.data_type=='FLOAT' and attr.domain in {'POINT','CORNER'} and not attr.name.startswith('.'):
            values=np.empty(len(attr.data),dtype=np.float32);attr.data.foreach_get('value',values);floats[attr.name]=(attr.domain,values)
    collection=bpy.data.collections.new('Bishop exact render regions');scene.collection.children.link(collection)
    parts=[];report=[]
    for label,name in enumerate(['body-rest','socket-lip']):
        faces=np.flatnonzero(labels==label);assert len(faces)
        loops=np.concatenate([np.arange(starts[f],starts[f]+counts[f]) for f in faces])
        verts,inverse=np.unique(vi[loops],return_inverse=True)
        polygons=[v.tolist() for v in np.split(inverse,np.cumsum(counts[faces])[:-1])]
        me=bpy.data.meshes.new('Bishop receiver '+name);me.from_pydata(xyz[verts].tolist(),[],polygons);me.update()
        me.polygons.foreach_set('use_smooth',smooth[faces]);me.polygons.foreach_set('material_index',material[faces])
        # Evaluated material pointers render in-memory but do not survive a
        # save/reopen. Use the persistent control slots with the same ordering.
        assert [m.name if m else None for m in mesh.materials]==[m.name if m else None for m in obj.data.materials]
        for mat in obj.data.materials:me.materials.append(mat)
        for uvname,values in uv.items():
            layer=me.uv_layers.new(name=uvname);layer.data.foreach_set('uv',values[loops].reshape(-1))
            layer.active_render=mesh.uv_layers[uvname].active_render
        me.uv_layers.active_index=mesh.uv_layers.active_index
        for attrname,(domain,values) in floats.items():
            attr=me.attributes.new(attrname,'FLOAT',domain)
            attr.data.foreach_set('value',values[verts if domain=='POINT' else loops])
        # Preserve provenance for an independent reopening audit.
        attr=me.attributes.new('bishop_source_face','INT','FACE');attr.data.foreach_set('value',faces)
        attr=me.attributes.new('bishop_source_vertex','INT','POINT');attr.data.foreach_set('value',verts)
        me.normals_split_custom_set(normal[loops].tolist())
        part=bpy.data.objects.new('Bishop receiver '+name,me);collection.objects.link(part)
        part.matrix_world=obj.matrix_world.copy();part['bishop_render_region']=name;part['bishop_control_name']=BODY
        parts.append(part)
        actual=np.empty(len(me.loops)*3,dtype=np.float32);me.corner_normals.foreach_get('vector',actual)
        error=float(np.max(np.abs(actual.reshape(-1,3)-normal[loops])))
        assert error<2e-4,('Custom normals changed',error)
        report.append({'name':name,'faces':len(faces),'triangles':int((counts[faces]-2).sum()),'vertices':len(verts),
          'z_min':float(centers[faces,2].min()),'z_max':float(centers[faces,2].max()),'uv_layers':list(uv),
          'max_custom_normal_component_error':error})
    assert sum(row['faces'] for row in report)==len(mesh.polygons)
    ev.to_mesh_clear()
    # All existing body-linked lamps must still reach both exact surfaces.
    old_receivers={o.light_linking.receiver_collection for o in scene.objects if o.type=='LIGHT' and o.light_linking.receiver_collection and obj.name in o.light_linking.receiver_collection.objects}
    for receiver in old_receivers:
        for part in parts:receiver.objects.link(part)
    obj['bishop_editable_control']=True;obj.hide_render=True
    scene['bishop_socket_partition']={'z_min':z_min,'z_max':z_max}
    return parts,report

def socket_only(lights,parts):
    socket=next(o for o in parts if o['bishop_render_region']=='socket-lip')
    collection=bpy.data.collections.new('Bishop isolated socket reflector receivers');collection.objects.link(socket)
    for lamp in lights:lamp.light_linking.receiver_collection=collection
    return collection

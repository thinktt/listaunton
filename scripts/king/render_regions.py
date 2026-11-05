"""Exact evaluated king body surfaces for independent light receivers.

Adapted from this project's queen render-region method. Keep the continuous
closed control for editing/export; derived receivers carry identical geometry,
UVs, float attributes, corner normals and material.
"""
import bpy,numpy as np
from mathutils import Vector

def controls(scene):
    return [o for o in scene.objects if o.type=='MESH' and not o.get('king_render_region') and (not o.hide_render or o.get('king_editable_control'))]

def partition(scene,body,profile_sections=False):
    assert not any(o.get('king_render_region') for o in scene.objects),'Start from an unpartitioned source.'
    if profile_sections:
        attr=body.data.attributes.get('King profile ring') or body.data.attributes.new('King profile ring','FLOAT','POINT')
        attr.data.foreach_set('value',(np.arange(len(body.data.vertices))//96).astype(np.float32))
    levels=[(m,m.levels) for m in body.modifiers if m.type=='SUBSURF']
    for m,_ in levels:m.levels=m.render_levels
    bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(graph);mesh=ev.to_mesh()
    co=np.array([v.co[:] for v in mesh.vertices],dtype=np.float32);lv=np.array([l.vertex_index for l in mesh.loops]);starts=np.array([p.loop_start for p in mesh.polygons]);counts=np.array([p.loop_total for p in mesh.polygons]);centers=np.add.reduceat(co[lv],starts,axis=0)/counts[:,None]
    names=['foot','flare','upper-body']
    if profile_sections:
        ring=np.array([v.value for v in mesh.attributes['King profile ring'].data],dtype=np.float32)
        face_ring=np.add.reduceat(ring[lv],starts)/counts;labels=np.digitize(face_ring,[8,19.8])
    else:labels=np.digitize(centers[:,2],[.24,.88])
    normals=np.array([n.vector[:] for n in mesh.corner_normals],dtype=np.float32)
    uvs={layer.name:np.array([v.uv[:] for v in layer.data],dtype=np.float32) for layer in mesh.uv_layers}
    attrs={a.name:(a.domain,np.array([v.value for v in a.data],dtype=np.float32)) for a in mesh.attributes if a.data_type=='FLOAT' and a.domain in ('POINT','CORNER') and not a.name.startswith('.')}
    collection=bpy.data.collections.new('King evaluated light receivers');scene.collection.children.link(collection);parts=[];report=[]
    for label,name in enumerate(names):
        face_ids=np.flatnonzero(labels==label);assert len(face_ids)
        loop_ids=np.concatenate([np.arange(starts[i],starts[i]+counts[i]) for i in face_ids]);vertex_ids,inverse=np.unique(lv[loop_ids],return_inverse=True);polygons=[a.tolist() for a in np.split(inverse,np.cumsum(counts[face_ids])[:-1])]
        data=bpy.data.meshes.new('King receiver '+name);data.from_pydata(co[vertex_ids].tolist(),[],polygons);data.update()
        data.polygons.foreach_set('use_smooth',np.ones(len(face_ids),dtype=bool))
        for uv_name,values in uvs.items():data.uv_layers.new(name=uv_name).data.foreach_set('uv',values[loop_ids].reshape(-1))
        data.uv_layers.active=data.uv_layers['Pigment atlas'];data.uv_layers.active.active_render=True
        for attr_name,(domain,values) in attrs.items():data.attributes.new(attr_name,'FLOAT',domain).data.foreach_set('value',values[vertex_ids if domain=='POINT' else loop_ids])
        data.normals_split_custom_set(normals[loop_ids].tolist());data.materials.append(body.data.materials[0])
        part=bpy.data.objects.new('King receiver '+name,data);collection.objects.link(part);part.matrix_world=body.matrix_world.copy();part['king_render_region']=name;part['king_control_source']=body.name;parts.append(part)
        report.append(dict(name=name,faces=len(face_ids),triangles=int((counts[face_ids]-2).sum()),vertices=len(vertex_ids),custom_normals=data.has_custom_normals))
    assert sum(row['faces'] for row in report)==len(mesh.polygons)
    ev.to_mesh_clear()
    for m,level in levels:m.levels=level
    # Existing body receivers must illuminate the identical replacement surface.
    receiver_collections={o.light_linking.receiver_collection for o in scene.objects if o.type=='LIGHT' and o.light_linking.receiver_collection and body.name in o.light_linking.receiver_collection.objects}
    for receiver in receiver_collections:
        receiver.objects.unlink(body)
        for part in parts:receiver.objects.link(part)
    body['king_editable_control']=True;body.hide_render=True;scene['king_render_regions']=True
    scene['king_partition_spec']=('Interpolated profile-ring bins 8 and 19.8' if profile_sections else 'Face-center Z bins 0.24 and 0.88')+': foot, flare, upper body; exact evaluated control surface.'
    bpy.context.view_layer.update();return parts,report

def link(light,parts,name):
    receiver=bpy.data.collections.new('King receivers '+name)
    for part in parts:receiver.objects.link(part)
    light.light_linking.receiver_collection=receiver

def visible_hit(scene,origin,direction):
    graph=bpy.context.evaluated_depsgraph_get();best=None
    for ob in scene.objects:
        if ob.type!='MESH' or ob.hide_render:continue
        ev=ob.evaluated_get(graph);inverse=ob.matrix_world.inverted();hit,point,normal,face=ev.ray_cast(inverse@origin,(inverse.to_3x3()@direction).normalized())
        if not hit:continue
        world=ob.matrix_world@point;distance=(world-origin).length
        if best is None or distance<best[0]:best=(distance,world,(ob.matrix_world.to_3x3().inverted().transposed()@normal).normalized(),face,ob)
    assert best is not None
    _,point,normal,face,ob=best;return True,point,normal,face,ob,None


def assign_material(scene,control,material):
    control.data.materials[0]=material
    for ob in scene.objects:
        if ob.get('king_render_region') and ob.get('king_control_source')==control.name:ob.data.materials[0]=material

def regenerate(scene):
    """Rebuild derived surfaces after changing control positions, UVs or attributes."""
    if not scene.get('king_render_regions'):return
    old=[o for o in scene.objects if o.get('king_render_region')]
    body=next(o for o in controls(scene) if 'body' in o.name)
    routing=[]
    for light in scene.objects:
        if light.type!='LIGHT' or not light.light_linking.receiver_collection:continue
        members=list(light.light_linking.receiver_collection.objects)
        if any(o in old for o in members):routing.append((light,[(o.get('king_render_region'),o.name) for o in members]))
    by_profile='profile-ring' in scene.get('king_partition_spec','')
    for ob in old:bpy.data.objects.remove(ob,do_unlink=True)
    body.hide_render=False;scene['king_render_regions']=False
    parts,report=partition(scene,body,profile_sections=by_profile);mapping={o['king_render_region']:o for o in parts}
    for light,members in routing:
        receivers=[mapping[region] if region else bpy.data.objects[name] for region,name in members]
        link(light,receivers,light.name+' regenerated')
    bpy.context.view_layer.update();return report

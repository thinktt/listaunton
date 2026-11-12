"""Exact evaluated king body surfaces for independent light receivers.

Adapted from this project's queen render-region method. Keep the continuous
closed control for editing/export; derived receivers carry identical geometry,
UVs, float attributes, corner normals and material.
"""
import bpy,numpy as np
from mathutils import Vector

COLLAR_RANGES={'lower-collar':(34.5,45.5),'middle-collar':(45.5,53.5),'upper-collar':(53.5,61.5)}
def controls(scene):
    return [o for o in scene.objects if o.type=='MESH' and not o.get('king_render_region') and (not o.hide_render or o.get('king_editable_control'))]

def partition(scene,body,profile_sections=False,split_flare=False,split_socket=False,split_socket_seam=False,split_collars=False):
    assert not any(o.get('king_render_region') for o in scene.objects),'Start from an unpartitioned source.'
    if profile_sections:
        attr=body.data.attributes.get('King profile ring') or body.data.attributes.new('King profile ring','FLOAT','POINT')
        attr.data.foreach_set('value',(np.arange(len(body.data.vertices))//96).astype(np.float32))
    levels=[(m,m.levels) for m in body.modifiers if m.type=='SUBSURF']
    for m,_ in levels:m.levels=m.render_levels
    bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(graph);mesh=ev.to_mesh()
    co=np.array([v.co[:] for v in mesh.vertices],dtype=np.float32);lv=np.array([l.vertex_index for l in mesh.loops]);starts=np.array([p.loop_start for p in mesh.polygons]);counts=np.array([p.loop_total for p in mesh.polygons]);centers=np.add.reduceat(co[lv],starts,axis=0)/counts[:,None]
    names=['foot','lower-flare','upper-flare'] if split_flare else ['foot','flare']
    assert not split_socket_seam or split_socket
    names+=(['socket','socket-seam','upper-body'] if split_socket_seam else ['socket','upper-body']) if split_socket else ['upper-body']
    if split_collars:names.extend(COLLAR_RANGES)
    assert not (split_flare or split_socket or split_collars) or profile_sections
    if profile_sections:
        ring=np.array([v.value for v in mesh.attributes['King profile ring'].data],dtype=np.float32)
        bins=([8,17,19.8] if split_flare else [8,19.8])+([28] if split_socket else [])
        face_ring=np.add.reduceat(ring[lv],starts)/counts;labels=np.digitize(face_ring,bins)
        if split_socket_seam:
            seam_index=names.index('socket-seam');labels[labels==seam_index]=seam_index+1
            labels[(face_ring>=26.55)&(face_ring<27.25)]=seam_index
        if split_collars:
            for name,(lo,hi) in COLLAR_RANGES.items():labels[(face_ring>=lo)&(face_ring<hi)]=names.index(name)
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
    scene['king_split_flare']=split_flare
    scene['king_split_socket']=split_socket
    scene['king_split_socket_seam']=split_socket_seam
    scene['king_split_collars']=split_collars
    scene['king_partition_spec']=('Interpolated profile-ring bins '+', '.join(str(x) for x in bins) if profile_sections else 'Face-center Z bins 0.24 and 0.88')+('; socket seam [26.55, 27.25)' if split_socket_seam else '')+('; collars '+str(COLLAR_RANGES) if split_collars else '')+': '+', '.join(names)+'; exact evaluated control surface.'
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

def regenerate(scene,split_flare=None,split_socket=None,split_socket_seam=None,split_collars=None):
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
    if split_flare is None:split_flare=bool(scene.get('king_split_flare',False))
    old_split_socket=bool(scene.get('king_split_socket',False))
    if split_socket is None:split_socket=old_split_socket
    old_socket_seam=bool(scene.get('king_split_socket_seam',False))
    if split_socket_seam is None:split_socket_seam=old_socket_seam
    old_split_collars=bool(scene.get('king_split_collars',False))
    if split_collars is None:split_collars=old_split_collars
    for ob in old:bpy.data.objects.remove(ob,do_unlink=True)
    body.hide_render=False;scene['king_render_regions']=False
    parts,report=partition(scene,body,profile_sections=by_profile,split_flare=split_flare,split_socket=split_socket,split_socket_seam=split_socket_seam,split_collars=split_collars);mapping={o['king_render_region']:o for o in parts}
    for light,members in routing:
        receivers=[]
        for region,name in members:
            if region=='flare' and split_flare:receivers.extend([mapping['lower-flare'],mapping['upper-flare']])
            elif region in ('lower-flare','upper-flare') and not split_flare:receivers.append(mapping['flare'])
            elif region=='upper-body' and split_socket and not old_split_socket:receivers.extend([mapping[k] for k in (['socket','socket-seam','upper-body'] if split_socket_seam else ['socket','upper-body'])])
            elif region=='socket' and split_socket_seam and not old_socket_seam:receivers.extend([mapping['socket'],mapping['socket-seam']])
            elif region=='socket-seam' and not split_socket_seam:receivers.append(mapping['socket'] if split_socket else mapping['upper-body'])
            elif region=='socket' and not split_socket:receivers.append(mapping['upper-body'])
            elif region in COLLAR_RANGES and not split_collars:receivers.append(mapping['upper-body'])
            else:receivers.append(mapping[region] if region else bpy.data.objects[name])
        if split_collars and not old_split_collars and mapping['upper-body'] in receivers:receivers.extend(mapping[n] for n in COLLAR_RANGES)
        receivers=list(dict.fromkeys(receivers))
        link(light,receivers,light.name+' regenerated')
    bpy.context.view_layer.update();return report


def clear_light_path(scene,point,normal,direction,distance):
    """Ignore hidden controls and reject reflectors shadowed by the visible model."""
    graph=bpy.context.evaluated_depsgraph_get();origin=point+normal*.0002
    for ob in scene.objects:
        if ob.type!='MESH' or ob.hide_render:continue
        inverse=ob.matrix_world.inverted();ev=ob.evaluated_get(graph)
        hit,location,_,_=ev.ray_cast(inverse@origin,(inverse.to_3x3()@direction).normalized())
        if hit and .0001<(ob.matrix_world@location-origin).length<distance:return False
    return True

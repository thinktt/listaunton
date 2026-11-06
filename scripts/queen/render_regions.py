"""Create light-link receivers from an evaluated continuous queen.

The editable closed mesh is retained. Render regions preserve its exact face
positions, smooth corner normals, UVs and active wood material. This utility
retains the closed control mesh for editing and the public mesh export.
"""
import bpy
import numpy as np

REGION_NAMES = ['foot', 'base', 'socket', 'stem', 'lower-collar',
                'middle-collar', 'upper-collar', 'crown-body', 'bowl', 'finial']

def partition(scene, obj, finial_only=False, socket_band=False, collar_band=False, split_collars=False,
              socket_face_count=None):
    assert not collar_band or socket_band, 'Collar partition requires the accepted socket partition'
    assert not split_collars or collar_band, 'Subdivided collars require the collar partition'
    old_levels = [(m, m.levels) for m in obj.modifiers if m.type == 'SUBSURF']
    for modifier, _ in old_levels:
        modifier.levels = modifier.render_levels
    bpy.context.view_layer.update()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    coordinates = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', coordinates)
    coordinates = coordinates.reshape(-1, 3)
    loop_vertices = np.empty(len(mesh.loops), dtype=np.int32)
    mesh.loops.foreach_get('vertex_index', loop_vertices)
    starts = np.empty(len(mesh.polygons), dtype=np.int32)
    counts = np.empty_like(starts)
    mesh.polygons.foreach_get('loop_start', starts)
    mesh.polygons.foreach_get('loop_total', counts)
    centers = np.add.reduceat(coordinates[loop_vertices], starts, axis=0) / counts[:, None]
    labels = np.digitize(centers[:, 2], [.29, .83, 1.32, 2.78, 2.97, 3.16, 3.34, 3.95])
    labels[(np.linalg.norm(centers[:, :2], axis=1) < .235) & (centers[:, 2] > 4.04)] = 9
    names = REGION_NAMES
    if socket_band:
        finial = labels == 9
        labels = np.zeros(len(centers), dtype=np.int32)
        socket_floor = .83
        if socket_face_count is not None:
            # The turned body has horizontal rings. Carry the original socket faces
            # with a deformed shoulder so its lighting follows the same wood.
            below_collar = centers[centers[:, 2] < 2.78, 2]
            boundary = len(below_collar) - socket_face_count
            if not 0 < boundary < len(below_collar):
                raise ValueError("Socket face count falls outside the turned body")
            ranked = np.partition(below_collar, (boundary - 1, boundary))
            lower, upper = ranked[boundary-1:boundary+1]
            if upper - lower < 1e-5:
                raise ValueError("Socket light boundary would split a meridian row")
            socket_floor = float((lower + upper) / 2)
        labels[(centers[:, 2] >= socket_floor) & (centers[:, 2] < 2.78)] = 1
        labels[finial] = 2
        names = ['turned-body', 'stem-socket', 'finial']
        if collar_band:
            labels[(centers[:, 2] >= 2.78) & (centers[:, 2] < 3.34)] = 3
            names.append('collars')
            if split_collars:
                labels[(centers[:, 2] >= 2.97) & (centers[:, 2] < 3.16)] = 4
                labels[(centers[:, 2] >= 3.16) & (centers[:, 2] < 3.34)] = 5
                names = ['turned-body', 'stem-socket', 'finial', 'lower-collar', 'middle-collar', 'upper-collar']
    elif finial_only:
        labels = (labels == 9).astype(np.int32)
        names = ['turned-body', 'finial']
    normals = np.empty(len(mesh.loops) * 3, dtype=np.float32)
    mesh.corner_normals.foreach_get('vector', normals)
    normals = normals.reshape(-1, 3)
    uv_layers = {}
    for layer in mesh.uv_layers:
        uv = np.empty(len(mesh.loops) * 2, dtype=np.float32)
        layer.data.foreach_get('uv', uv)
        uv_layers[layer.name] = uv.reshape(-1, 2)
    float_attributes = {}
    for attribute in mesh.attributes:
        if attribute.data_type == 'FLOAT' and attribute.domain in ('POINT', 'CORNER') and not attribute.name.startswith('.'):
            values = np.empty(len(attribute.data), dtype=np.float32)
            attribute.data.foreach_get('value', values)
            float_attributes[attribute.name] = (attribute.domain, values)
    collection = bpy.data.collections.new('Queen render regions')
    scene.collection.children.link(collection)
    parts, reports = [], []
    for label, name in enumerate(names):
        faces = np.flatnonzero(labels == label)
        assert len(faces), name
        selected_loops = np.concatenate([np.arange(starts[i], starts[i] + counts[i]) for i in faces])
        selected_vertices, inverse = np.unique(loop_vertices[selected_loops], return_inverse=True)
        boundaries = np.cumsum(counts[faces])[:-1]
        polygons = [p.tolist() for p in np.split(inverse, boundaries)]
        part_mesh = bpy.data.meshes.new('Queen region ' + name)
        part_mesh.from_pydata(coordinates[selected_vertices].tolist(), [], polygons)
        part_mesh.update()
        part_mesh.polygons.foreach_set('use_smooth', np.ones(len(faces), dtype=bool))
        for uv_name, values in uv_layers.items():
            layer = part_mesh.uv_layers.new(name=uv_name)
            layer.data.foreach_set('uv', values[selected_loops].reshape(-1))
        for attribute_name, (domain, values) in float_attributes.items():
            attribute = part_mesh.attributes.new(attribute_name, 'FLOAT', domain)
            selected = selected_vertices if domain == 'POINT' else selected_loops
            attribute.data.foreach_set('value', values[selected])
        part_mesh.normals_split_custom_set(normals[selected_loops].tolist())
        part_mesh.materials.append(obj.data.materials[0])
        part = bpy.data.objects.new('Queen region ' + name, part_mesh)
        collection.objects.link(part)
        part.matrix_world = obj.matrix_world.copy()
        part['mission_render_region'] = name
        part.pass_index = label + 1
        parts.append(part)
        reports.append({'name': name, 'faces': len(faces), 'vertices': len(selected_vertices),
                        'triangles': int((counts[faces] - 2).sum()), 'uv_layers': list(uv_layers),
                        'custom_corner_normals': part_mesh.has_custom_normals})
        if name == 'stem-socket' and socket_face_count is not None:
            reports[-1]['lower_height'] = socket_floor
    assert sum(r['faces'] for r in reports) == len(mesh.polygons)
    evaluated.to_mesh_clear()
    for modifier, level in old_levels:
        modifier.levels = level
    obj['mission_editable_control'] = True
    obj.hide_render = True
    scene['mission_render_partitions'] = True
    return parts, reports

def link(light, parts, name):
    collection = bpy.data.collections.get('Receivers ' + name)
    if collection:
        assert {o.name for o in collection.objects} == {o.name for o in parts}
    else:
        collection = bpy.data.collections.new('Receivers ' + name)
        for part in parts:
            collection.objects.link(part)
    light.light_linking.receiver_collection = collection
    return collection

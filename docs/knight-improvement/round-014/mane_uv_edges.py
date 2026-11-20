"""Find UV seam pairs on the real mane; take two samples of the same physical point."""
import hashlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np

root, model, out = [Path(x).resolve() for x in sys.argv[sys.argv.index('--')+1:]]
sys.path.insert(0, str(root/'scripts/knight'))
from lower_carving_fit import rest_coords

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def packed_array(collection, field, columns, dtype):
    array = np.empty((len(collection), columns), dtype)
    collection.foreach_get(field, array.ravel())
    return array

def fingerprint(*items):
    h = hashlib.sha256()
    for item in items:
        h.update(item.tobytes())
    return h.hexdigest()

source = digest(model.read_bytes())
bpy.ops.wm.open_mainfile(filepath=str(model), load_ui=False)
scene = bpy.context.scene
graph = bpy.context.evaluated_depsgraph_get()
pose = json.loads(scene['knight_mission_pose'])
camera = scene.camera
parts = {}
out.parent.mkdir(parents=True,exist_ok=True)
for obj in scene.objects:
    if obj.type != 'MESH' or obj.hide_render:
        continue
    ev = obj.evaluated_get(graph)
    mesh = ev.to_mesh()
    try:
        mesh.calc_loop_triangles()
        points = packed_array(mesh.vertices, 'co', 3, np.float32)
        tri = packed_array(mesh.loop_triangles,'vertices',3,np.int32)
        loops = packed_array(mesh.loop_triangles,'loops',3,np.int32)
        normals = packed_array(mesh.vertices,'normal',3,np.float32)
        links = obj.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links
        tex = links[0].from_node
        uv_name = tex.inputs['Vector'].links[0].from_node.uv_map
        uv = packed_array(mesh.uv_layers[uv_name].data,'uv',2,np.float32)[loops]
        attrib = mesh.attributes['Knight varnish coverage']
        varnish = packed_array(attrib.data,'value',1,np.float32)
        mat = np.array(ev.matrix_world,dtype=np.float64)
        parts[obj.name] = {'geometry':fingerprint(points,tri,mat),'normals':fingerprint(normals),
                           'uv':fingerprint(uv),'varnish':fingerprint(varnish),'uv_layer':uv_name,
                           'packed_atlas':digest(tex.image.packed_file.data)}
        if obj.name != 'Knight | swept rounded mane':
            continue
        rest = rest_coords((points@mat[:3,:3].T+mat[:3,3]),[pose[k] for k in ('dx','dy','twist_degrees')])
        # Each sorted vertex pair names one physical edge irrespective of UV islands.
        edges = {}
        pairs = []
        for face, vertices in enumerate(tri):
            for a, b, opposite in [(0,1,2),(1,2,0),(2,0,1)]:
                i,j = vertices[a],vertices[b]
                if i > j:
                    i,j = j,i
                    a,b = b,a
                key = (int(i),int(j))
                current = uv[face,[a,b,opposite],:]
                other = edges.pop(key, None)
                if other is None:
                    edges[key] = current
                    continue
                center = (rest[i]+rest[j])/2
                # The freely visible hanging mane, from below the ears down to the neck.
                if 2.43 <= center[2] <= 4.30:
                    pairs.append((center, np.linalg.norm(rest[j]-rest[i]), other, current))
        assert not edges
        xyz,lengths,left,right = map(np.array,zip(*pairs))
        np.savez_compressed(out.with_suffix('.npz'),xyz=xyz,lengths=lengths,left=left,right=right)
    finally:
        ev.to_mesh_clear()
lamps = {}
for obj in scene.objects:
    if obj.type=='LIGHT' and not obj.hide_render:
        lamp = obj.data
        lamps[obj.name] = [np.array(obj.matrix_world).ravel().tolist(),lamp.type,lamp.energy,list(lamp.color),
                           getattr(lamp,'shape',None),getattr(lamp,'size',None),getattr(lamp,'size_y',None)]
assert len(parts)==7 and digest(model.read_bytes())==source
settings = {'camera_matrix':np.array(camera.matrix_world).ravel().tolist(),'camera_type':camera.data.type,
            'ortho_scale':camera.data.ortho_scale,'shift':[camera.data.shift_x,camera.data.shift_y],
            'lamps':lamps,'view_transform':scene.view_settings.view_transform}
out.with_suffix('.json').write_text(json.dumps({'source_sha256':source,'parts':parts,'settings':settings,
   'sample_pairs':len(pairs),'physical_uv_pairs_sha256':digest(out.with_suffix('.npz').read_bytes())},indent=2)+'\n')
print('Analyzed',len(pairs),'pairs of faces on the physical mane.')

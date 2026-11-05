"""Measure distant-reflector responses aimed from reference highlight locations.

The reference chooses candidate light directions, never the beauty-image pixels.
Each response is an actual Cycles render of the accepted black wood BSDF.
"""
from pathlib import Path
import hashlib, json, math, sys
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'models/queen/queen-rebuilt.blend'
SOURCE_HASH = '82100ad9047426b1be46e72d01d769189b4e9f667005fd8c8bcc5d743c16526e'
OUT = ROOT / 'build/queen-mission/directional-reflections-006'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False)
scene = bpy.context.scene
obj = next(o for o in scene.objects if o.type == 'MESH' and not o.hide_render)
settings = json.loads(scene['mission_material_config'])
reference = np.load(ROOT / 'build/queen-mission/pigment-fit-039/reference-srgb.npy')

# Derive mirror directions from smooth geometric normals in the fixed camera.
for modifier in obj.modifiers:
    if modifier.type == 'SUBSURF':
        modifier.levels = modifier.render_levels
bpy.context.view_layer.update()
graph = bpy.context.evaluated_depsgraph_get()
evaluated = obj.evaluated_get(graph)
mesh = evaluated.to_mesh()
mesh.calc_loop_triangles()
vertices = np.empty(len(mesh.vertices) * 3)
normals = np.empty_like(vertices)
mesh.vertices.foreach_get('co', vertices)
mesh.vertices.foreach_get('normal', normals)
vertices, normals = vertices.reshape(-1, 3), normals.reshape(-1, 3)
triangles = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int32)
mesh.loop_triangles.foreach_get('vertices', triangles)
triangles = triangles.reshape(-1, 3)
tree = BVHTree.FromPolygons(vertices.tolist(), triangles.tolist(), all_triangles=True)
camera = scene.camera
inverse = (camera.calc_matrix_camera(graph, x=1254, y=1254) @ camera.matrix_world.inverted()).inverted()
view = camera.matrix_world.to_3x3() @ Vector((0, 0, 1))
view.normalize()
minimum, maximum = reference.min(2), reference.max(2)
highlight = (minimum > .13) & (minimum / np.maximum(maximum, .001) > .40) & (maximum > .45)
sample = np.zeros(highlight.shape, dtype=bool)
sample[::4, ::4] = True
ys, xs = np.nonzero(highlight & sample)
directions, weights, pixels = [], [], []
for x, y in zip(xs, ys):
    near = inverse @ Vector((2 * (x + .5) / 1254 - 1, 1 - 2 * (y + .5) / 1254, -1, 1))
    near = near.xyz / near.w
    location, _, index, _ = tree.ray_cast(near, -view, 100)
    if location is None:
        continue
    tri = triangles[index]
    a, b, c = vertices[tri]
    uv = np.linalg.lstsq(np.column_stack((b - a, c - a)), np.array(location) - a, rcond=None)[0]
    normal = Vector(normals[tri[0]] * (1 - sum(uv)) + normals[tri[1]] * uv[0] + normals[tri[2]] * uv[1])
    normal.normalize()
    direction = 2 * normal.dot(view) * normal - view
    directions.append(list(direction.normalized()))
    weights.append(float(minimum[y, x]))
    pixels.append([int(x), int(y)])
evaluated.to_mesh_clear()
directions, weights = np.array(directions), np.array(weights)
assert len(directions) >= 36
# Deterministic spherical clustering covers the useful directions without a
# large arbitrary render sweep. Two angular sizes test compact/broad emitters.
centers = [directions[np.argmax(weights)]]
for _ in range(35):
    distance = 1 - (directions @ np.array(centers).T).max(1)
    centers.append(directions[np.argmax(distance * np.sqrt(weights))])
centers = np.array(centers)
for _ in range(30):
    membership = np.argmax(directions @ centers.T, axis=1)
    previous = centers.copy()
    for index in range(len(centers)):
        selected = membership == index
        if selected.any():
            centers[index] = np.average(directions[selected], axis=0, weights=weights[selected])
            centers[index] /= np.linalg.norm(centers[index])
    if np.max(abs(centers - previous)) < 1e-6:
        break
specs = []
for index, direction in enumerate(centers):
    for angle in (3, 10):
        specs.append({'name': f'distant-{index:02d}-{angle:02d}', 'type': 'SUN',
                      'position': list(direction * 10), 'target': [0, 0, 0],
                      'energy': 1.0, 'angle_degrees': angle,
                      'diffuse_factor': 0, 'specular_factor': 1})

scene.render.resolution_x = scene.render.resolution_y = 418
scene.render.resolution_percentage = 100
scene.render.use_persistent_data = True
scene.cycles.samples = 64
scene.cycles.use_denoising = False
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_depth = '32'
scene.render.image_settings.color_mode = 'RGBA'
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for device in prefs.devices:
    device.use = device.type == 'OPTIX'
if any(device.use for device in prefs.devices):
    scene.cycles.device = 'GPU'

def render(name):
    path = OUT / (name + '.exr')
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(str(path), check_existing=False)
    array = np.empty(418 * 418 * 4, dtype=np.float32)
    image.pixels.foreach_get(array)
    array = array.reshape(418, 418, 4)[::-1].copy()
    bpy.data.images.remove(image)
    np.save(OUT / (name + '.npy'), array)

for light in scene.objects:
    if light.type == 'LIGHT':
        light.visible_glossy = False
render('diffuse-baseline')
for light in list(scene.objects):
    if light.type == 'LIGHT':
        bpy.data.objects.remove(light, do_unlink=True)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0
nodes, links = obj.data.materials[0].node_tree.nodes, obj.data.materials[0].node_tree.links
bsdf = nodes.get('Principled BSDF')
for link in list(bsdf.inputs['Base Color'].links):
    links.remove(link)
bsdf.inputs['Base Color'].default_value = (0, 0, 0, 1)
for index, spec in enumerate(specs):
    data = bpy.data.lights.new(spec['name'], 'SUN')
    data.energy, data.angle = 1, math.radians(spec['angle_degrees'])
    light = bpy.data.objects.new(spec['name'], data)
    scene.collection.objects.link(light)
    light.location = spec['position']
    light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
    light.visible_diffuse = False
    light.visible_glossy = True
    render(spec['name'])
    bpy.data.objects.remove(light, do_unlink=True)
    print('DIRECTIONAL_RESPONSE', index + 1, len(specs), spec['name'], flush=True)
manifest = {'source': SOURCE.relative_to(ROOT).as_posix(), 'source_sha256': SOURCE_HASH,
            'reference_sha256': hashlib.sha256((ROOT / 'assets/queen/reference.png').read_bytes()).hexdigest(),
            'samples': 64, 'size': 418, 'specs': specs, 'sampled_highlight_pixels': len(pixels),
            'method': '36 spherical clusters of mirror directions at bright low-chroma reference locations; actual 3- and 10-degree distant reflection responses.'}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH
print('DIRECTIONAL_REFLECTION_CAPTURE_DONE', flush=True)

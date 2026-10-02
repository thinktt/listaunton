import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT = Path(r'C:\Users\toby\Documents\Codex\2026-10-01\go-x20')
OUT = ROOT / 'outputs' / 'queen-model'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
model_collection = bpy.data.collections.new('QUEEN - editable geometry')
scene.collection.children.link(model_collection)

def move_model(obj):
    for c in list(obj.users_collection): c.objects.unlink(obj)
    model_collection.objects.link(obj)

def material(name, color, roughness):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color,1)
    mat.use_nodes=True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=roughness
    return mat
clay = material('Warm neutral clay - geometry review',(.47,.36,.24),.36)

def mesh_object(name, verts, faces):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); model_collection.objects.link(obj)
    obj.data.materials.append(clay)
    for p in mesh.polygons: p.use_smooth=True
    return obj

def lathe(name, profile, segments=128, subdiv=2):
    # Profile traverses a closed section from bottom axis to outer wall to top axis.
    verts=[]
    for r,z in profile:
        for i in range(segments):
            a=2*math.pi*i/segments
            verts.append((r*math.cos(a),r*math.sin(a),z))
    faces=[]
    for j in range(len(profile)-1):
        for i in range(segments):
            k=(i+1)%segments
            faces.append((j*segments+i,j*segments+k,(j+1)*segments+k,(j+1)*segments+i))
    faces.append(tuple(reversed(range(segments))))
    faces.append(tuple((len(profile)-1)*segments+i for i in range(segments)))
    obj=mesh_object(name,verts,faces)
    if subdiv:
        mod=obj.modifiers.new('Smooth turned profile','SUBSURF'); mod.levels=subdiv; mod.render_levels=subdiv
    return obj

# Radius, height. A shallow foot supports a raised stem socket.
# The single narrow groove below the shoulder is the only turned line at the foot.
body_profile=[
(.001,.035),(.80,.035),(1.04,.035),(1.10,.055),(1.125,.10),
(1.13,.145),(1.125,.178),(1.105,.196),(1.094,.211),
(1.105,.228),(1.124,.246),(1.13,.276),(1.12,.314),(1.10,.35),
(1.060,.436),(1.00,.524),(.91,.615),(.80,.692),(.70,.770),
(.650,.860),(.614,.980),(.591,1.10),(.577,1.20),(.565,1.28),
(.553,1.35),(.545,1.397),(.557,1.438),
(.544,1.479),(.510,1.508),(.470,1.521),(.446,1.550),
(.419,1.601),(.386,1.694),(.350,1.81),(.31,1.96),(.284,2.10),(.273,2.21),
(.284,2.29),(.31,2.39),(.353,2.47),(.402,2.515),
(.486,2.54),(.567,2.565),(.637,2.61),(.669,2.658),(.670,2.70),
(.647,2.741),(.60,2.767),(.568,2.785),
(.56,2.813),(.58,2.842),(.593,2.877),(.587,2.91),(.563,2.939),
(.512,2.956),(.467,2.967),(.452,2.993),(.46,3.023),(.465,3.061),
(.453,3.094),(.427,3.116),(.407,3.18),(.400,3.31),(.413,3.49),
(.448,3.64),(.476,3.717),(.480,3.74),(.001,3.74)]
body_profile = [(r, z + (.055*max(0,1-max(0,z-2.70)/.18) if 2.54 <= z <= 2.88 else 0)) for r,z in body_profile]
assert all(b[1] >= a[1] for a,b in zip(body_profile,body_profile[1:])), 'Turned body profile folds back on itself'
body=lathe('01 Turned base, stem and double collar',body_profile)

# The coronet is a shallow saucer, not a deep cup. Its basin flows directly
# into a partly submerged egg-shaped finial, with no separate support ring.
# Tuple = radius, height, amount of crown-tip deformation.
crown_profile=[(.001,3.712,0),(.395,3.712,0),(.487,3.732,0),
(.536,3.768,.08),(.573,3.826,.24),(.588,3.904,.57),
(.594,3.974,.90),(.590,3.997,1),(.569,4.004,1),
(.536,3.996,.92),(.512,3.977,.60),(.485,3.947,.22),
(.461,3.931,.04),(.395,3.925,0),(.310,3.925,0),
(.252,3.927,0),(.223,3.939,0),(.209,3.965,0),
(.204,4.005,0),(.190,4.063,0),(.165,4.116,0),
(.130,4.159,0),(.085,4.187,0),(.036,4.202,0),(.001,4.205,0)]
N=192
verts=[]
for r,z,amp in crown_profile:
    for i in range(N):
        a=2*math.pi*i/N
        peak=((1+math.cos(8*(a-math.pi/8)))/2)**3
        rr=r+amp*(.065*peak)
        zz=z+amp*(.110*peak)
        verts.append((rr*math.cos(a),rr*math.sin(a),zz))
faces=[]
for j in range(len(crown_profile)-1):
    for i in range(N):
        k=(i+1)%N
        faces.append((j*N+i,j*N+k,(j+1)*N+k,(j+1)*N+i))
faces.append(tuple(reversed(range(N))))
faces.append(tuple((len(crown_profile)-1)*N+i for i in range(N)))
verts = [(x*1.035,y*1.035,z) for x,y,z in verts]
crown=mesh_object('02 Shallow scalloped crown and integrated egg finial',verts,faces)
mod=crown.modifiers.new('Soften carved crown edges','SUBSURF'); mod.levels=2; mod.render_levels=2

# Keep both supplied originals packed inside the file for future comparison.
refs=bpy.data.collections.new('REFERENCES - packed originals, hidden in viewport')
scene.collection.children.link(refs)
for index,color in enumerate(('White','Black')):
    path=ROOT/'outputs'/'lichess-staunton-3d'/f'{color}-Queen.webp'
    im=bpy.data.images.load(str(path)); im.pack()
    obj=bpy.data.objects.new(f'{color} queen source',None); refs.objects.link(obj)
    obj.empty_display_type='IMAGE'; obj.data=im; obj.empty_display_size=4.4
    obj.location=(3.5+index*3,0,2); obj.rotation_euler=(math.pi/2,0,0)
    obj.hide_render=True; obj.hide_viewport=True

world=bpy.data.worlds.new('Studio world'); scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.16,.16,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.45

def point_at(obj,p): obj.rotation_euler=(Vector(p)-obj.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,power,size):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
    obj=bpy.data.objects.new(name,data); scene.collection.objects.link(obj); obj.location=loc; point_at(obj,(0,0,2))
area('Large softbox upper left',(-3,-4,8),550,4)
area('Gentle front fill',(4,-2,4),130,3)
area('Back edge light',(2,4,6),260,3)
cam_data=bpy.data.cameras.new('Reference camera'); cam=bpy.data.objects.new('Reference camera',cam_data)
scene.collection.objects.link(cam); scene.camera=cam
cam_data.type='ORTHO'; cam_data.ortho_scale=4.77; cam_data.shift_x=.1183; cam_data.shift_y=-.060

def camera(elevation=47,azimuth=-90):
    target=Vector((0,0,1.95)); elev=math.radians(elevation); az=math.radians(azimuth)
    cam.location=target+Vector((10*math.cos(elev)*math.cos(az),10*math.cos(elev)*math.sin(az),10*math.sin(elev)))
    point_at(cam,target)
camera()
scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=32
scene.render.resolution_x=900; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(OUT/'queen-reference-view.png')
scene['project_notes']='Geometry revision: wider shallow foot with one turned groove; raised stem socket; shallow crown basin with partly submerged egg-shaped center. Both Lichess queen sprites are packed references. Wood material intentionally deferred. Units arbitrary.'
# Useful opening state for interactive inspection.
bpy.ops.object.select_all(action='DESELECT')
for obj in model_collection.objects: obj.select_set(True)
bpy.context.view_layer.objects.active=body
for screen in bpy.data.screens:
    for area_ in screen.areas:
        if area_.type=='VIEW_3D':
            space=area_.spaces.active
            space.region_3d.view_distance=7.5
            space.region_3d.view_location=(0,0,2)
            space.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
            space.shading.type='MATERIAL'
            space.overlay.show_overlays=False
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'staunton-queen.blend'))
bpy.ops.render.render(write_still=True)
# Secondary view shows depth without the steep source projection.
camera(20,-55)
cam_data.shift_x=0; cam_data.shift_y=0; cam_data.ortho_scale=5.0
scene.render.filepath=str(OUT/'queen-three-quarter.png')
bpy.ops.render.render(write_still=True)
print('QUEEN_MODEL_AND_RENDERS_COMPLETE')







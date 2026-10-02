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

# Radius, height. Total height is roughly 4.2 Blender units; scale is intentionally arbitrary.
body_profile=[
(.001,.055),(.80,.055),(.91,.055),(.98,.07),(1.025,.105),(1.047,.15),
(1.05,.205),(1.035,.245),(1.003,.266),(.985,.285),(.993,.311),
(1.018,.336),(1.027,.373),(1.025,.418),(1.003,.455),(.975,.484),
(.963,.527),(.951,.60),(.927,.694),(.88,.80),(.815,.917),(.732,1.032),
(.637,1.137),(.566,1.203),(.526,1.237),
(.515,1.257),(.516,1.286),(.541,1.312),(.551,1.35),(.540,1.389),
(.508,1.415),(.472,1.425),(.448,1.445),
(.425,1.49),(.391,1.577),(.350,1.72),(.31,1.88),(.284,2.04),(.273,2.18),
(.284,2.29),(.31,2.39),(.353,2.47),(.402,2.515),
(.486,2.54),(.567,2.565),(.637,2.61),(.669,2.658),(.670,2.70),
(.647,2.741),(.60,2.767),(.568,2.785),
(.56,2.813),(.58,2.842),(.593,2.877),(.587,2.91),(.563,2.939),
(.512,2.956),(.467,2.967),(.452,2.993),(.46,3.023),(.465,3.061),
(.453,3.094),(.427,3.116),(.407,3.145),(.400,3.21),(.413,3.29),
(.448,3.39),(.476,3.451),(.480,3.475),(.001,3.475)]
body_profile = [(r + (.085*math.exp(-((z-.75)/.26)**2) if .50 < z < 1.25 else 0), z + (.08*math.exp(-((z-.80)/.22)**2) if .50 < z < 1.25 else 0) + (.055*max(0,1-max(0,z-2.70)/.18) if 2.54 <= z <= 2.88 else 0)) for r,z in body_profile]
body_profile = [(r, z + .18 * min(1.0, max(0.0, (z - 3.10) / .375))) for r,z in body_profile]
assert all(b[1] >= a[1] for a,b in zip(body_profile,body_profile[1:])), 'Turned body profile folds back on itself'
body=lathe('01 Turned base, stem and double collar',body_profile)

# Hollow coronet: eight rounded points connected by shallow scallops.
# Tuple = radius, height, amount of crown-tip deformation.
crown_profile=[(.001,3.42,0),(.395,3.42,0),(.491,3.43,0),(.530,3.46,0),
(.550,3.51,.05),(.569,3.59,.2),(.583,3.68,.45),(.588,3.77,.8),
(.588,3.805,1),(.576,3.825,1),(.535,3.817,.95),(.520,3.79,.84),
(.525,3.74,.60),(.493,3.665,.28),(.448,3.612,.05),(.399,3.579,0),
(.327,3.566,0),(.23,3.563,0),(.001,3.563,0)]
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
verts = [(x*1.035,y*1.035,z+.18) for x,y,z in verts]
crown=mesh_object('02 Eight-point scalloped coronet with recessed bowl',verts,faces)
mod=crown.modifiers.new('Soften carved crown edges','SUBSURF'); mod.levels=2; mod.render_levels=2

lathe('03 Finial pedestal',[(.001,3.54),(.18,3.54),(.215,3.575),(.205,3.615),(.17,3.645),(.001,3.66)],96,2)
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=.208,location=(0,0,3.773))
ball=bpy.context.object; ball.name='04 Central spherical finial'; move_model(ball)
ball.scale=(1,1,1.06); ball.data.materials.append(clay)
for p in ball.data.polygons:p.use_smooth=True

for obj in model_collection.objects:
    if obj.name.startswith(('03 ', '04 ')): obj.location.z += .18

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
scene['project_notes']='Geometry reconstruction from the white and black Lichess Staunton queen sprites. Eightfold crown symmetry inferred; wood material intentionally deferred. Units arbitrary.'
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







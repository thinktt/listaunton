"""Matched clay and walnut views for the saved round seven model."""
from pathlib import Path
import json
import sys
import bpy
from mathutils import Vector

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path[:0] = [str(ROOT/'scripts/knight'), str(OUT)]
from mission_scene import configure_render, json_file, render, sha, use_side_camera, visible_meshes
def load(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name),load_ui=False)
    return bpy.context.scene

def flat(scene):
    for obj in visible_meshes(scene):
        for slot in obj.material_slots:
            slot.material=bpy.data.materials['Neutral satin clay']
    for obj in scene.objects:
        if obj.type=='LIGHT':
            obj.hide_render=True
    for i,loc in enumerate([(4,5,8),(4,-5,8),(-4,5,8),(-4,-5,8)]):
        lamp=bpy.data.lights.new('Clay bank '+str(i),'AREA')
        lamp.energy=440
        lamp.shape='DISK'
        lamp.size=4.5
        obj=bpy.data.objects.new(lamp.name,lamp)
        scene.collection.objects.link(obj)
        obj.location=loc
        obj.rotation_euler=(Vector((0,0,2.8))-obj.location).to_track_quat('-Z','Y').to_euler()

def flat_views(name,prefix):
    scene=load(name)
    configure_render(scene,40)
    scene.render.resolution_percentage=64
    flat(scene)
    render(scene,OUT/(prefix+'clay-fixed.png'))
    use_side_camera(scene)
    render(scene,OUT/(prefix+'clay-side.png'))

def studio():
    scene=load('knight.blend')
    configure_render(scene,144)
    render(scene,OUT/'wood.png')
    use_side_camera(scene)
    render(scene,OUT/'wood-side.png')
    data=json.loads((OUT/'parameters.json').read_text())
    data.update({'fixed_sha256':sha(OUT/'wood.png'),'side_sha256':sha(OUT/'wood-side.png'),'samples':144})
    json_file(OUT/'parameters.json',data)

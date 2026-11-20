from pathlib import Path
import sys, math, json
import bpy
from mathutils import Vector
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[2]/"scripts/knight"))
from mission_scene import render, visible_meshes
def camera(scene,angle,elevation=10):
    a,e=map(math.radians,(angle,elevation))
    target=Vector((0,0,2.62))
    cam=scene.camera;cam.data.ortho_scale=6.1;cam.data.shift_x=cam.data.shift_y=0
    cam.location=target+Vector((12*math.sin(a)*math.cos(e),-12*math.cos(a)*math.cos(e),12*math.sin(e)))
    cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
    bpy.context.view_layer.update()

def diagnostics(scene, prefix, clay=False, skip_existing=False):
    scene.render.resolution_x=scene.render.resolution_y=640
    scene.cycles.samples=32
    yaw=json.loads(scene["knight_mission_pose"])["twist_degrees"]
    for name,az in (("front",90),("opposite",180),("rear-quarter",225),("rear",270),("near",0)):
        camera(scene,yaw+az)
        path=OUT/f"{prefix}wood-{name}.png"
        if not skip_existing or not path.exists():
            render(scene,path)
    if clay:
        for obj in visible_meshes(scene):
            for slot in obj.material_slots:slot.material=bpy.data.materials["Neutral satin clay"]
        for obj in scene.objects:
            if obj.type=="LIGHT":obj.hide_render=True
        target=Vector((0,0,2.62))
        for i,point in enumerate([(5,5,8),(5,-5,8),(-5,5,8),(-5,-5,8)]):
            light=bpy.data.lights.new(f"Clay softbox {i}","AREA");light.energy=420;light.shape="DISK";light.size=5.5
            box=bpy.data.objects.new(light.name,light);scene.collection.objects.link(box);box.location=point
            box.rotation_euler=(target-box.location).to_track_quat("-Z","Y").to_euler()
        for i in range(16):
            camera(scene,yaw+22.5*i,8)
            path=OUT/f"clay-{i:02d}.png"
            if not skip_existing or not path.exists():
                render(scene,path)

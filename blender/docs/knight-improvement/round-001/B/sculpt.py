"""Round 1B. Run in Blender with --build, --wood or --diagnostics after --."""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / "scripts/knight"))
from mission_pose import posed
from mission_scene import configure_render, json_file, render, save_model, sha
from mission_scene import use_side_camera, visible_meshes, world_vertices
from refine_eye import apply_world, unpose

SOURCE = OUT / "parent-007.blend"
MODEL = OUT / "knight.blend"
PARENT_SHA = "c1254b0087c39e4506b34575d88b52d92a1cd376ed9ee4b891c207d5ce51995c"


def compact(t):
    t = np.clip(t, 0, 1)
    return t*t*(3-2*t)


def orbit(rest, eye):
    center = np.array([.42, 4.155])
    line = np.array([1., -.76])
    line /= np.linalg.norm(line)
    normal = np.array([-line[1], line[0]])
    xz = rest[:, [0, 2]]
    off = xz - center
    u, v = off @ line, off @ normal
    side = np.sign(rest[:, 1])
    # Local coordinate warp carries the existing closed lens, socket and upper
    # lip together. The falloff leaves the cheek and the nose tip anchored.
    influence = compact((.49 - np.abs(u)) / .23) * compact((.29 - np.abs(v)) / .16)
    influence *= compact((np.abs(rest[:, 1]) - .11) / .13)
    advance = .18*u + .008
    drop = -.080*u + .009
    rest[:, 0] += influence * (advance*line[0] + drop*normal[0])
    rest[:, 2] += influence * (advance*line[1] + drop*normal[1])
    rest[:, 1] += side * influence * (.062*u - .004)
    if eye:
        # Seat the lens under the rim on both flanks.
        rest[:, 1] -= side * influence * .006
        return
    # Shallow crescent with pointed corners. The lower lid is carved into
    # the cheek rather than appended as a separate overlapping mesh.
    limit = np.abs(u / .305)
    half = np.maximum(0., 1 - limit**1.72)
    axis = -.032 - .060*half
    length = compact((.32 - abs(u)) / .145)
    crest = .019 * np.exp(-((v-axis)/.056)**2)
    incision = .004 * np.exp(-((v-axis+.061)/.055)**2)
    upper = .004 * np.exp(-((v-.07*half-.018)/.054)**2)
    extent = compact((np.abs(rest[:, 1])-.15)/.14)
    rest[:, 1] += side * extent * length * (crest-incision+upper)


def build():
    assert sha(SOURCE) == PARENT_SHA
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False)
    scene = bpy.context.scene
    pose = json.loads(scene["knight_mission_pose"])
    args = [pose["dx"], pose["dy"], pose["twist_degrees"]]
    changes = {}
    for obj in scene.objects:
        name = obj.name
        if obj.type != "MESH" or name.endswith(("pedestal", "neck and chest")):
            continue
        world = world_vertices(obj)
        original = unpose(world, pose)
        rest = original.copy()
        if name.endswith(("head and neck", "conical muzzle", "eye")):
            orbit(rest, name.endswith("eye"))
        elif name.endswith("swept ear"):
            rings = rest.reshape(7, 64, 3)
            side = np.sign(rings[0,0,1])
            # A slightly flatter, continuous swept edge tapers into the
            # forehead. The two sides receive the same cross-section changes.
            for index, ring in enumerate(rings):
                center = ring.mean(0)
                ring[:,2] = center[2] + (ring[:,2]-center[2])*[1,.93,.90,.89,.87,.84,1][index]
                ring[:,2] += [0,.001,.006,.010,.013,.017,.019][index]
                ring[:,1] -= side*np.array([0,.006,.010,.008,.010,.035,.044])[index]
                ring[:,0] += np.array([-.022,-.014,-.008,.004,.014,.027,.046])[index]
        elif name.endswith("swept rounded mane"):
            rings = rest.reshape(-1, 64, 3)
            # Carve a firmer shoulder along the crest plane. Each ring keeps
            # its crown at the parent height and the change fades at the neck.
            for index, gain in enumerate([.14,.20,.21,.19,.11,.045]):
                ring = rings[index]
                center = ring.mean(0)
                d = ring[:,1] - center[1]
                norm = np.abs(d)/np.max(np.abs(d))
                ring[:,1] += np.sign(d)*gain*np.max(np.abs(d))*(np.sqrt(norm)-norm)
                if index < 3:
                    ring[:,0] -= [.029,.022,.009][index]
        else:
            continue
        new_world = world + (posed(rest, *args) - posed(original, *args))
        dist = np.linalg.norm(new_world-world, axis=1)
        changes[name] = {"vertices_moved": int(np.sum(dist>1.e-5)), "max_displacement": float(max(dist))}
        apply_world(obj, new_world)
    bpy.context.view_layer.update()
    config = {"name":"Long orbital rim and seated brow","round":1,"parent_sha256":PARENT_SHA,
              "mesh_edits":changes}
    scene["knight_improvement_001_B"] = json.dumps(config)
    configure_render(scene, 144)
    save_model(scene, MODEL)
    config["candidate_sha256"] = sha(MODEL)
    json_file(OUT / "sculpt.json", config)


def camera_at(scene, azimuth, elevation=7):
    a, e = math.radians(azimuth), math.radians(elevation)
    camera = scene.camera
    camera.data.shift_x = 0
    camera.data.shift_y = 0
    target = Vector((scene.get("knight_foot_center_x", 0),0,2.548305))
    camera.location = target + Vector((12*math.sin(a)*math.cos(e),-12*math.cos(a)*math.cos(e),12*math.sin(e)))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()


def deliver(diagnostics=False):
    bpy.ops.wm.open_mainfile(filepath=str(MODEL), load_ui=False)
    scene = bpy.context.scene
    configure_render(scene, 144)
    if not diagnostics:
        render(scene, OUT / "wood.png")
        use_side_camera(scene)
        render(scene, OUT / "wood-side.png")
        json_file(OUT / "reopened.json", {"blend":sha(MODEL),"wood":sha(OUT/"wood.png"),
                  "wood-side":sha(OUT/"wood-side.png"),"samples":scene.cycles.samples,
                  "width":scene.render.resolution_x,"height":scene.render.resolution_y,
                  "device":json.loads(scene["knight_render_device"])})
        return
    scene.cycles.samples=32
    scene.render.resolution_percentage=51
    use_side_camera(scene)
    for name, angle in [("front",90),("rear",-90),("opposite",180)]:
        camera_at(scene, angle)
        render(scene,OUT/f"wood-{name}.png")
    # A pair of broad, equal banks on each axis makes the volume readable
    # throughout the clay turn. The walnut views all use the parent studio.
    for obj in scene.objects:
        if obj.type=="LIGHT":
            obj.hide_render=True
    for i, location in enumerate([(5,4,8),(5,-4,8),(-5,4,8),(-5,-4,8)]):
        data=bpy.data.lights.new(f"Clay softbox {i}","AREA")
        data.energy=440
        data.shape="DISK"
        data.size=4
        obj=bpy.data.objects.new(data.name,data)
        scene.collection.objects.link(obj)
        obj.location=location
        obj.rotation_euler=(Vector((0,0,2.55))-obj.location).to_track_quat("-Z","Y").to_euler()
    clay = bpy.data.materials.get("Neutral satin clay") or bpy.data.materials.new("Diagnostic clay")
    clay.use_nodes=True
    shader=clay.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value=(.32,.34,.37,1.)
    shader.inputs["Roughness"].default_value=.48
    for obj in visible_meshes(scene):
        for slot in obj.material_slots:
            slot.material=clay
    for name,angle in [("side",0),("quarter-front",45),("front",90),("far-front",135),
                       ("opposite",180),("far-rear",225),("rear",270),("near-rear",315)]:
        camera_at(scene,angle)
        render(scene, OUT/f"clay-{name}.png")


if __name__=="__main__":
    options=sys.argv[sys.argv.index("--")+1:]
    if "--build" in options:
        build()
    if "--wood" in options:
        deliver()
    if "--diagnostics" in options:
        deliver(True)

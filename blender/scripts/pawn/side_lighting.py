"""Set up photographic area lights for the level side camera."""
import math

import bpy

from fit_lighting import make_light, shape
from mission_render import ASSETS, ROOT, Surface, area, render, sha


def set_profile_angle(camera, degrees):
    """Orbit a level orthographic camera about its original target."""
    from mathutils import Vector

    # The dedicated side camera orbits the lathe's vertical axis at its aim height.
    back = (camera.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    distance = math.hypot(camera.location.x, camera.location.y) / math.hypot(back.x, back.y)
    target = camera.location - distance * back
    horizontal = Vector((back.x, back.y, 0)).normalized()
    angle = math.radians(degrees)
    new_back = math.cos(angle) * horizontal + math.sin(angle) * Vector((0, 0, 1))
    camera.location = target + distance * new_back
    camera.rotation_euler = (-new_back).to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()


def set_side_lighting(scene, body, recipe):
    """Replace only lights belonging exclusively to the editable side scene."""
    if bpy.context.window.scene != scene or scene.get("pawn_side_scene"):
        raise ValueError("Select the side scene before assigning its studio lights.")
    if abs(scene.camera.matrix_world.to_3x3().col[2].z) > 0.001:
        raise ValueError("The side camera must be level.")
    for light in list(scene.objects):
        if light.type == "LIGHT":
            if len(light.users_scene) != 1:
                raise ValueError(f"{light.name} belongs to another scene.")
            bpy.data.objects.remove(light, do_unlink=True)
    if scene.world.users > 1:
        scene.world = scene.world.copy()
    background = scene.world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (*recipe["world_color"], 1)
    background.inputs["Strength"].default_value = recipe["world_strength"]
    for card in recipe["cards"]:
        lamp = area(scene, card["name"], card["location"], card["target"], card["power"],
             card["width"], size_y=card.get("height"), color=card["color"],
             diffuse=card.get("diffuse", True), glossy=card.get("glossy", True))
        lamp.data.spread = math.radians(card.get("spread", 180))
    if recipe.get("reflections"):
        surface = Surface(scene, body)
        for reflection in recipe["reflections"]:
            lamp = shape(surface, reflection)
            lamp["energy"] = reflection["power"]
            make_light(scene, lamp)
    scene["pawn_lighting_preset"] = recipe["name"]
    scene["pawn_presentation"] = recipe["description"]
    bpy.context.view_layer.update()


def portrait_camera(scene, degrees):
    """Save an additional camera in the side studio, sharing its subject and lights."""
    source = scene.camera
    camera = scene.objects.get(scene.get("pawn_portrait_camera", ""))
    if camera is None:
        camera = source.copy()
        camera.data = source.data.copy()
        camera.name = "Pawn guide-angle camera"
        scene.collection.objects.link(camera)
    camera.matrix_world = source.matrix_world.copy()
    bpy.context.view_layer.update()
    set_profile_angle(camera, degrees)
    scene["pawn_portrait_camera"] = camera.name
    scene["pawn_portrait_degrees"] = degrees
    return camera


def render_portrait(scene):
    level = scene.camera
    if abs(level.matrix_world.to_3x3().col[2].z) > 0.00001:
        raise ValueError("Expected the saved level camera before rendering the portrait.")
    scene.camera = scene.objects[scene["pawn_portrait_camera"]]
    try:
        elevation = math.degrees(math.asin(scene.camera.matrix_world.to_3x3().col[2].normalized().z))
        if abs(elevation - scene["pawn_portrait_degrees"]) > 0.001:
            raise ValueError("The saved portrait camera differs from its recorded elevation.")
        path = ASSETS / "guide-angle.png"
        render(scene, path)
        return {"file": path.relative_to(ROOT).as_posix(), "sha256": sha(path),
                "camera": scene.camera.name, "elevation": round(elevation, 3)}
    finally:
        scene.camera = level

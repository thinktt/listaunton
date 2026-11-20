"""Change only named diffuse sources' elevation around the pawn contact."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from mission_render import BUILD, save_json
from polish_trial import open_source, save_trial


def shift(scene, cfg):
    pivot = Vector(cfg["pivot"])
    records = []
    for name in cfg["lights"]:
        lamp = scene.objects[name]
        assert lamp.type == "LIGHT" and lamp.data.type == "AREA"
        assert lamp.visible_diffuse and not lamp.visible_glossy
        before = list(lamp.location)
        offset = lamp.location - pivot
        distance = offset.length
        elevation = math.asin(offset.z / distance)
        new_elevation = elevation + math.radians(cfg["elevation_delta"])
        horizontal = Vector((offset.x, offset.y, 0)).normalized()
        lamp.location = pivot + horizontal * (distance * math.cos(new_elevation)) + Vector((0, 0, distance * math.sin(new_elevation)))
        lamp.rotation_euler = (Vector(cfg["aim"])-lamp.location).to_track_quat("-Z", "Y").to_euler()
        records.append({"name": name, "before": before, "after": list(lamp.location),
                        "before_elevation": math.degrees(elevation), "after_elevation": math.degrees(new_elevation),
                        "power": lamp.data.energy, "size": lamp.data.size})
    return records


def run(cfg):
    scene, _ = open_source(cfg)
    records = shift(scene, cfg)
    out = BUILD / cfg["variant"]
    out.mkdir(parents=True, exist_ok=True)
    save_json(out / "light-change.json", {"pivot": cfg["pivot"], "changes": records})
    save_trial(scene, cfg)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("config", type=Path)
    a = p.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(json.loads(a.config.read_text()))

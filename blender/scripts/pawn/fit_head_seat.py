"""Build lower-sphere and shallow collar controls in the original sprite units."""
from pathlib import Path
import argparse
import json
import math

ROOT = Path(__file__).resolve().parents[2]


def profiles(settings):
    guide = json.loads((ROOT / "scripts/pawn/profile.json").read_text())
    alignment = json.loads((ROOT / "assets/pawn/original-alignment.json").read_text())
    units = 1254 / (300 * alignment["scale"] * guide["scale"])
    vertical = units / math.cos(math.radians(54))
    # The upper sphere and its position were established at checkpoint 001.
    center_z = (guide["y0"] - guide["head_seating"]["center_y"] + 3.7) * vertical
    radius = guide["head_seating"]["radius"] * units
    contact = settings["contact_radius_fraction"]
    theta0 = -math.acos(contact)
    contact_z = center_z + radius * math.sin(theta0)
    result = {}
    for index, radius_original, height_relative in settings["collar"]:
        result[str(index)] = [radius_original, guide["y0"] - (contact_z + height_relative) / vertical]
    for i in range(42, 53):
        theta = theta0 * (52 - i) / 10
        z = center_z + radius * math.sin(theta)
        result[str(i)] = [radius * math.cos(theta) / units, guide["y0"] - z / vertical]
    return {i: [round(r, 7), round(y, 7)] for i, (r, y) in result.items()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("settings", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    spec = json.loads(args.settings.read_text())
    cfg = dict(spec["trial"])
    cfg["profiles"] = profiles(spec)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf8")

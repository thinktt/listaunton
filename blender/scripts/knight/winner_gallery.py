"""Keep an immutable pair of saved-scene renders for every knight round."""
import argparse
import hashlib
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets/knight"
GALLERY = ASSETS / "winners"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(content):
    return hashlib.sha256(content).hexdigest()


def record(number, winner, reason):
    checkpoint = read(ASSETS / "mission-checkpoint.json")
    side = read(ASSETS / "side-registration.json")
    model = digest((ROOT / "models/knight/knight-rebuilt.blend").read_bytes())
    if model != checkpoint["source_sha256"] or model != side["source_blend_sha256"]:
        raise ValueError("The two views must come from the accepted scene.")
    if (checkpoint["camera_degrees"], checkpoint["side_degrees"]) != (54, 7):
        raise ValueError("Unexpected camera angles.")
    GALLERY.mkdir(parents=True, exist_ok=True)
    previous = sorted(GALLERY.glob("round-*.json"))
    target = GALLERY / f"round-{number:04d}.json"
    if number < 0 or number > 9999 or number != len([p for p in previous if p < target]):
        raise ValueError("Record rounds consecutively, starting at zero.")
    if (number == 0) != (winner == "Baseline"):
        raise ValueError("Only round zero is the baseline.")
    if number:
        parent = read(previous[number - 1])["model"]
        if (model == parent) != (winner == "Parent retained"):
            raise ValueError("Winner does not agree with the accepted parent model.")
    row = {"round": number, "winner": winner, "reason": reason, "model": model}
    for view, source, expected in [
        ("fixed", "render.png", checkpoint["render_sha256"]),
        ("side", "guide-render.png", side["profile_sha256"]),
    ]:
        pixels = (ASSETS / source).read_bytes()
        if digest(pixels) != expected:
            raise ValueError(f"Stale {view} render")
        name = f"{expected}.png"
        path = GALLERY / name
        if path.exists():
            if digest(path.read_bytes()) != expected:
                raise ValueError(f"Archived render changed: {path}")
        else:
            path.write_bytes(pixels)
        row[view] = name
    if target.exists() and read(target) != row:
        raise ValueError("Existing round entries are immutable.")
    target.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def gallery_panel():
    cards = []
    for path in sorted(GALLERY.glob("round-*.json"), reverse=True):
        row = read(path)
        title = "Starting knight" if not row["round"] else f'Round {row["round"]} · {escape(row["winner"])}'
        pairs = []
        for view, label in [("fixed", "54° reference view"), ("side", "Side view")]:
            src = "assets/knight/winners/" + escape(row[view], quote=True)
            pairs.append(f'<figure><figcaption>{label}</figcaption><a href="{src}"><img loading="lazy" src="{src}" alt="{title}, {label}"></a></figure>')
        cards.append(f'<article><h2>{title}</h2><p>{escape(row["reason"])}</p><div class="winner-pair">{"".join(pairs)}</div></article>')
    return '<section id="panel-improvement" role="tabpanel" aria-labelledby="tab-improvement" hidden>' + "".join(cards) + "</section>"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("round", type=int)
    parser.add_argument("winner", choices=["Baseline", "Candidate A", "Candidate B", "Parent retained"])
    parser.add_argument("reason")
    args = parser.parse_args()
    record(args.round, args.winner, args.reason)

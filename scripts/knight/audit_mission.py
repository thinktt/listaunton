"""Audit actual knight renders at the unchanged candidate and sprite registration."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets/knight"
sys.path.insert(0, str(ROOT/"scripts/queen"))
from overlay_qa import largest_component, fill_holes, font


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def open_rgba(path):
    return Image.open(path).convert("RGBA")


def black(image):
    return Image.alpha_composite(Image.new("RGBA", image.size, (0,0,0,255)), image).convert("RGB")


def registered():
    selected = open_rgba(ASSETS/"ref.png")
    align = json.loads((ASSETS/"original-alignment.json").read_text())
    scale = align["scale"] * 300 / selected.width
    black_original = open_rgba(ASSETS/"original.png").transform(selected.size, Image.Transform.AFFINE,
        (scale,0,align["x"]*3,0,scale,align["y"]*3), Image.Resampling.BILINEAR)
    white_adjust = json.loads((ASSETS/"white-registration.json").read_text())
    w = white_adjust["scale"]
    white_original = open_rgba(ASSETS/"white-original.png").transpose(Image.Transpose.FLIP_LEFT_RIGHT).transform(
        selected.size, Image.Transform.AFFINE, (scale/w,0,(align["x"]-white_adjust["x"])*3/w,
        0,scale/w,(align["y"]-white_adjust["y"])*3/w), Image.Resampling.BILINEAR)
    return {"original":black_original,"selected":selected,"white_mirrored":white_original}


def silhouette(image, reference=False):
    rgba = np.asarray(image)
    mask = rgba[:,:,3] > 127
    if reference: mask &= rgba[:,:,:3].max(2) > 12
    return fill_holes(largest_component(mask))


def iou(left, right):
    return float((left & right).sum() / (left | right).sum())


def panel(path, images, box, width):
    height = round(width * (box[3]-box[1]) / (box[2]-box[0]))
    sheet = Image.new("RGB", ((width+8)*len(images)+8,height+46), "#17191c")
    draw = ImageDraw.Draw(sheet)
    for index, (label, image) in enumerate(images):
        x = 8+index*(width+8)
        draw.text((x,6), label, fill="#f1eeea", font=font(16))
        sheet.paste(black(image).crop(box).resize((width,height), Image.Resampling.LANCZOS), (x,36))
    sheet.save(path)


def audit(trial, render_path, previous_path):
    refs = registered()
    current = open_rgba(render_path)
    previous = open_rgba(previous_path)
    a, b = silhouette(current), silhouette(previous)
    report = {"trial":trial.name, "model_sha256":sha(trial/"knight.blend"), "render_sha256":sha(render_path),
              "previous_render_sha256":sha(previous_path), "registration":"Saved 54-degree, 12-degree-yaw orthographic camera and signed source alignments.",
              "scores":{}}
    for key, ref in refs.items():
        reference = silhouette(ref, True)
        report["scores"][key] = {"iou":iou(a,reference), "previous_iou":iou(b,reference)}
    report["source_sha256"] = {name:sha(ASSETS/name) for name in ["original.png","white-original.png","ref.png"]}
    views = [("Lichess original",refs["original"]),("Black candidate 2",refs["selected"]),
             ("Previous accepted",previous),("Trial "+trial.name.split("-")[0],current)]
    panel(trial/"comparison.png", views, (158,260,805,1090), 305)
    for name, box in [("head",(175,270,785,575)),("chest",(230,470,750,840)),("base",(195,680,785,1070))]:
        panel(trial/(name+".png"),views[1:],box,390)
    for name in ["original","selected"]:
        Image.blend(black(refs[name]), black(current), .5).save(trial/("overlay-"+name+".png"))
    (trial/"metrics.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report["scores"],indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("variant")
    parser.add_argument("--render",default="wood.png")
    parser.add_argument("--previous",type=Path,default=ASSETS/"render.png")
    args = parser.parse_args()
    directory = ROOT/"build/knight-mission"/args.variant
    audit(directory, directory/args.render, args.previous)

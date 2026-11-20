"""Compare the lower queen at the saved camera and from the side."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets/queen"
ZONES = {
    "roll_and_socket": (323, 651, 644, 855),
    "flare": (257, 786, 711, 994),
    "whole_lower_body": (206, 570, 763, 1080),
}


def registered_original():
    reg = json.loads((ASSETS / "original-reference-alignment.json").read_text())
    scale, dx, dy = reg["scale"], reg["offset_x"], reg["offset_y"]
    source = Image.open(ROOT / reg["source"]).convert("RGBA")
    return source.transform(tuple(reg["canvas_size"]), Image.Transform.AFFINE,
                            (1/scale, 0, -dx/scale, 0, 1/scale, -dy/scale),
                            Image.Resampling.BILINEAR)


def on_black(im):
    return Image.alpha_composite(Image.new("RGBA", im.size, "black"), im.convert("RGBA")).convert("RGB")


def compare_colors(target, before, after, blur):
    def blurred(im):
        return np.asarray(on_black(im).filter(ImageFilter.GaussianBlur(blur)), dtype=np.float32)

    target_rgb, old_rgb, new_rgb = (blurred(im) for im in (target, before, after))
    valid = (np.asarray(before)[:, :, 3] > 240) & (np.asarray(after)[:, :, 3] > 240)
    valid &= target_rgb.max(axis=2) > 16
    result = {}
    for name, (x0, y0, x1, y1) in ZONES.items():
        box = np.s_[y0:y1, x0:x1]
        expected = target_rgb[box][valid[box]]
        old, new = (float(np.square(rgb[box][valid[box]] - expected).mean(dtype=np.float64))
                    for rgb in (old_rgb, new_rgb))
        result[name] = {"previous_mse": old, "current_mse": new,
                        "percent_error_reduction": 100*(1-new/old)}
    return result


def strip(images, box, width):
    height = round(width*(box[3]-box[1])/(box[2]-box[0]))
    sheet = Image.new("RGB", (len(images)*(width+6)-6, height+34), "#191919")
    font = ImageFont.load_default(size=18)
    draw = ImageDraw.Draw(sheet)
    for column, (name, image) in enumerate(images):
        x = column*(width+6)
        draw.text((x+8, 5), name, fill="#f6f3ef", font=font)
        sheet.paste(on_black(image).crop(box).resize((width,height), Image.Resampling.LANCZOS), (x,34))
    return sheet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, default=ROOT / "history/queen-mission-017")
    parser.add_argument("--current", type=Path, default=ASSETS)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    original, highres = registered_original(), Image.open(ASSETS/"reference.png")
    before, after = (Image.open(p/"queen-brown.png").convert("RGBA") for p in (args.previous,args.current))
    assert before.size == after.size == original.size == highres.size
    for name, ref, label in (("original", original, "Lichess original"), ("high-res", highres, "Selected high-res")):
        strip([(label,ref),("Previous",before),("Revised",after)],
              (231,573,736,930),415).save(args.out/f"{name}-socket.png")
    rows = []
    for file, surface in (("queen-finished-profile.png","shape"), ("queen-wood-profile.png","wood")):
        old_side, new_side = (Image.open(p/file) for p in (args.previous,args.current))
        rows.append(strip([(f"Previous {surface}",old_side),(f"Revised {surface}",new_side)],
                          (145,570,455,801),370))
    side = Image.new("RGB",(rows[0].width,sum(row.height for row in rows)))
    side.paste(rows[0],(0,0))
    side.paste(rows[1],(0,rows[0].height))
    side.save(args.out/"socket-side.png")
    result = {
        "method": "Mean squared RGB error in display space on shared opaque piece pixels. Both inputs receive the same blur, 2.5 pixels for the enlarged original and 1 pixel for high-res.",
        "boxes": ZONES,
        "original": compare_colors(original, before, after, 2.5),
        "selected_highres": compare_colors(highres, before, after, 1),
    }
    (args.out/"socket-image-check.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()

"""Repeatable pixel-aligned queen reconstruction comparisons.

Run with the bundled Python after Blender has written queen-matched.png.
No registration, scaling, or shifting is applied to either source image.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = WORKSPACE / "outputs" / "queen-hires"
CYAN = (46, 225, 244)
MAGENTA = (255, 76, 215)
BG = (11, 13, 18)


def font(size: int, bold: bool = False):
    for name in ("segoeuib.ttf" if bold else "segoeui.ttf", "arial.ttf"):
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def largest_component(mask: np.ndarray) -> np.ndarray:
    """Find the largest 8-connected component via row runs, without SciPy."""
    parents: list[int] = []
    runs: list[tuple[int, int, int, int]] = []
    previous: list[tuple[int, int, int]] = []

    def root(i: int) -> int:
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    for y, row in enumerate(mask):
        transitions = np.diff(np.pad(row.astype(np.int8), (1, 1)))
        starts = np.flatnonzero(transitions == 1)
        ends = np.flatnonzero(transitions == -1) - 1
        current = []
        p = 0
        for start, end in zip(starts.tolist(), ends.tolist()):
            ident = len(parents)
            parents.append(ident)
            while p < len(previous) and previous[p][1] < start - 1:
                p += 1
            q = p
            while q < len(previous) and previous[q][0] <= end + 1:
                other = root(previous[q][2])
                this = root(ident)
                if this != other:
                    parents[this] = other
                q += 1
            current.append((start, end, ident))
            runs.append((y, start, end, ident))
        previous = current

    if not runs:
        raise ValueError("Foreground mask is empty.")
    areas: dict[int, int] = {}
    for _, start, end, ident in runs:
        key = root(ident)
        areas[key] = areas.get(key, 0) + end - start + 1
    biggest = max(areas, key=areas.get)
    result = np.zeros_like(mask, dtype=bool)
    for y, start, end, ident in runs:
        if root(ident) == biggest:
            result[y, start:end + 1] = True
    return result


def fill_holes(mask: np.ndarray) -> np.ndarray:
    # Padding guarantees a background flood seed even if a model touches an edge.
    # fromarray may be read-only; floodfill silently fails on that pixel buffer.
    padded = Image.fromarray(np.pad(mask.astype(np.uint8) * 255, 1)).copy()
    ImageDraw.floodfill(padded, (0, 0), 128, thresh=0)
    return np.asarray(padded)[1:-1, 1:-1] != 128


def contour(mask: np.ndarray) -> np.ndarray:
    bitmap = Image.fromarray(mask.astype(np.uint8) * 255)
    outer = np.asarray(bitmap.filter(ImageFilter.MaxFilter(3))) > 0
    inner = np.asarray(bitmap.filter(ImageFilter.MinFilter(3))) > 0
    return outer & ~inner


def bounds(mask: np.ndarray):
    y, x = np.nonzero(mask)
    return [int(x.min()), int(y.min()), int(x.max()), int(y.max())]


def legend(image: Image.Image, title: str, subtitle: str) -> Image.Image:
    result = image.convert("RGB").copy()
    draw = ImageDraw.Draw(result)
    # The supplied reference has ample unused space on the right.
    x, y = min(802, result.width - 445), 29
    draw.rounded_rectangle((x - 12, y - 10, result.width - 20, y + 147), 12,
                           fill=(14, 17, 23), outline=(48, 54, 68))
    draw.text((x, y), title, font=font(25, True), fill=(238, 242, 250))
    draw.text((x, y + 40), subtitle, font=font(18), fill=(179, 188, 203))
    if "Contour" in title:
        draw.line((x, y + 85, x + 35, y + 85), fill=CYAN, width=4)
        draw.text((x + 48, y + 72), "Reference", font=font(19), fill=CYAN)
        draw.line((x, y + 119, x + 35, y + 119), fill=MAGENTA, width=4)
        draw.text((x + 48, y + 106), "Model", font=font(19), fill=MAGENTA)
    else:
        draw.text((x, y + 83), "Reference + model at 50%", font=font(19),
                  fill=(218, 224, 236))
        draw.text((x, y + 115), "No image alignment adjustments", font=font(17),
                  fill=(162, 173, 190))
    return result


def comparison(title: str, subtitle: str, box: tuple[int, int, int, int],
               images: list[Image.Image], path: Path, panel_width: int = 530):
    gap, margin, header, footer = 22, 24, 105, 48
    w, h = box[2] - box[0], box[3] - box[1]
    panel_height = round(h * panel_width / w)
    canvas = Image.new("RGB", (margin * 2 + panel_width * 3 + gap * 2,
                               header + panel_height + footer), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 17), title, font=font(27, True), fill=(242, 245, 252))
    draw.text((margin, 54), subtitle, font=font(17), fill=(168, 181, 204))
    for index, (name, image) in enumerate(zip(
            ("REFERENCE", "MODEL", "50% OVERLAY"), images)):
        x = margin + index * (panel_width + gap)
        crop = image.crop(box).resize((panel_width, panel_height), Image.Resampling.LANCZOS)
        canvas.paste(crop.convert("RGB"), (x, header))
        draw.text((x, header - 24), name, font=font(15, True), fill=(215, 224, 241))
    draw.text((margin, header + panel_height + 14),
              "Identical pixel coordinates in all panels. Shape only; wood material is deferred.",
              font=font(16), fill=(160, 173, 195))
    canvas.save(path)


def feature_curves(reference: Image.Image, landmark_path: Path, output: Path):
    """Project actual model circles onto the reference without image fitting."""
    if not landmark_path.is_file():
        return None
    landmarks = json.loads(landmark_path.read_text(encoding="utf-8"))
    scale = float(landmarks["scale"])
    elevation = np.deg2rad(float(landmarks["elevation"]))
    cx, y0 = float(landmarks["cx"]), float(landmarks["y0"])
    pixels = (np.asarray(reference.convert("RGB"), dtype=np.float32) * .76).astype(np.uint8)
    result = Image.fromarray(pixels)
    draw = ImageDraw.Draw(result)
    colors = [(251, 135, 86), (255, 208, 78), (172, 230, 88), (47, 225, 174),
              (46, 219, 247), (108, 159, 255), (181, 130, 255), (251, 113, 215),
              (247, 247, 252)]
    features = []
    for index, (name, coordinates) in enumerate(landmarks["rings"].items()):
        radius, height = map(float, coordinates)
        cy = y0 - scale * height * np.cos(elevation)
        a, b = scale * radius, scale * radius * np.sin(elevation)
        theta = np.linspace(0, np.pi, 401)
        points = list(zip((cx + a * np.cos(theta)).tolist(),
                          (cy + b * np.sin(theta)).tolist()))
        color = colors[index % len(colors)]
        draw.line(points, fill=color, width=2, joint="curve")
        front = (cx, cy + b)
        draw.ellipse((front[0] - 3, front[1] - 3, front[0] + 3, front[1] + 3), fill=color)
        features.append({"name": name, "r": radius, "z": height,
                         "axis_y": float(cy), "front_y": float(cy + b),
                         "radius_px": float(a), "color": color})
    draw.rounded_rectangle((793, 27, reference.width - 20, 154), 12,
                           fill=(14, 17, 23), outline=(48, 54, 68))
    draw.text((807, 41), "Projected model feature curves", font=font(22, True), fill=(244, 245, 250))
    draw.text((807, 78), "Circles from actual model r / z", font=font(17), fill=(183, 195, 216))
    draw.text((807, 108), f"Camera elevation {np.rad2deg(elevation):.2f} degrees", font=font(17),
              fill=(183, 195, 216))
    previous_y = 176
    for item in sorted(features, key=lambda value: value["front_y"]):
        label_y = max(item["front_y"] - 16, previous_y + 49)
        previous_y = label_y
        # Leader starts in the right/front quadrant, clear of the central details.
        curve_x = cx + item["radius_px"] * .77
        curve_y = item["axis_y"] + item["radius_px"] * np.sin(elevation) * np.sqrt(1 - .77 ** 2)
        draw.line([(curve_x, curve_y), (783, label_y + 9), (803, label_y + 9)],
                  fill=item["color"], width=1)
        draw.text((811, label_y), item["name"].replace("_", " ").title(),
                  font=font(18, True), fill=item["color"])
        draw.text((811, label_y + 24),
                  f"r {item['r']:.3f} · z {item['z']:.3f} · front y {item['front_y']:.1f}",
                  font=font(14), fill=(168, 179, 198))
    draw.text((24, result.height - 33),
              "Front semicircles projected onto the reference. Curve placement is diagnostic; no image warping.",
              font=font(17), fill=(175, 188, 209))
    result.save(output / "feature-curves.png")
    (output / "feature-curves.json").write_text(json.dumps(features, indent=2), encoding="utf-8")
    return features


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=DEFAULT_OUTPUT / "reference.png")
    parser.add_argument("--render", type=Path, default=DEFAULT_OUTPUT / "queen-matched.png")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reference-mask", choices=("luminance", "max-channel"), default="max-channel",
                        help="Max-channel avoids mistaking dark brown surfaces for the black backdrop.")
    parser.add_argument("--threshold", type=int, default=12)
    args = parser.parse_args()
    for path in (args.reference, args.render):
        if not path.is_file():
            raise SystemExit(f"Required image does not exist yet: {path}")
    reference = Image.open(args.reference).convert("RGBA")
    model = Image.open(args.render).convert("RGBA")
    if reference.size != model.size:
        raise SystemExit(f"Pixel registration requires identical sizes: reference={reference.size}, model={model.size}")
    if np.asarray(model.getchannel("A")).min() == 255:
        raise SystemExit("Render has no transparent background; export Blender RGBA with film_transparent=True.")
    args.output.mkdir(parents=True, exist_ok=True)
    reference_rgb = reference.convert("RGB")
    feature_curves(reference_rgb, args.output / "profile-landmarks.json", args.output)
    dark = Image.new("RGBA", reference.size, (0, 0, 0, 255))
    model_rgb = Image.alpha_composite(dark, model).convert("RGB")
    half_model = model.copy()
    half_model.putalpha(model.getchannel("A").point(lambda value: round(value * 0.5)))
    overlay = Image.alpha_composite(reference, half_model).convert("RGB")
    overlay.save(args.output / "overlay-50.png")
    legend(overlay, "50% geometry overlay", "Original framing · matched camera").save(
        args.output / "overlay-50-labeled.png")

    reference_signal = (np.asarray(reference_rgb.convert("L")) if args.reference_mask == "luminance"
                        else np.asarray(reference_rgb).max(axis=2))
    reference_mask = fill_holes(largest_component(reference_signal > args.threshold))
    model_mask = fill_holes(largest_component(np.asarray(model.getchannel("A")) > 127))
    reference_edge, model_edge = contour(reference_mask), contour(model_mask)
    contour_pixels = (np.asarray(reference_rgb, dtype=np.float32) * 0.70).astype(np.uint8)
    contour_pixels[reference_edge] = CYAN
    contour_pixels[model_edge] = MAGENTA
    contour_pixels[reference_edge & model_edge] = (249, 244, 255)
    contour_image = Image.fromarray(contour_pixels)
    contour_image.save(args.output / "contour-overlay.png")
    legend(contour_image, "Contour comparison", "Coincident edges appear white").save(
        args.output / "contour-overlay-labeled.png")

    for slug, title, crop in (
        ("crown", "Crown and central finial", (285, 40, 685, 367)),
        ("collars", "Upper body and collar stack", (285, 296, 685, 576)),
        ("base", "Raised stem socket and broad base", (185, 572, 785, 1108)),
        ("full", "Queen reconstruction · camera-matched comparison", (180, 35, 790, 1110)),
    ):
        comparison(title, "Reference image, neutral geometry, and transparent overlay",
                   crop, [reference_rgb, model_rgb, overlay],
                   args.output / f"comparison-{slug}.png")

    union = reference_mask | model_mask
    intersection = reference_mask & model_mask
    rows = []
    for y in (100, 160, 260, 340, 420, 500, 560, 600, 700, 800, 840, 940, 1000, 1060):
        if y >= reference.height:
            continue
        record = {"y": y}
        for name, mask in (("reference", reference_mask), ("model", model_mask)):
            x = np.flatnonzero(mask[y])
            record[name] = [int(x.min()), int(x.max())] if x.size else None
        rows.append(record)
    metrics = {
        "reference": str(args.reference), "render": str(args.render),
        "size": list(reference.size), "registration": "No shifts or scaling applied",
        "mask_method": f"Reference {args.reference_mask} >{args.threshold}; model alpha >127; largest 8-connected component, holes filled",
        "reference_bbox": bounds(reference_mask), "model_bbox": bounds(model_mask),
        "silhouette_iou": float(intersection.sum() / union.sum()),
        "reference_area_px": int(reference_mask.sum()), "model_area_px": int(model_mask.sum()),
        "missing_reference_px": int((reference_mask & ~model_mask).sum()),
        "excess_model_px": int((model_mask & ~reference_mask).sum()),
        "row_extents": rows,
        "caution": "Silhouette overlap does not assess internal geometry, shading, material, or unseen surfaces.",
    }
    (args.output / "overlay-metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Comparisons saved in {args.output}")


if __name__ == "__main__":
    main()

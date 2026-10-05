"""Measure original base widths and register transparent side views without editing pixels.

Requires Pillow and NumPy. Run before build_set_comparison.py after replacing cutouts.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'assets/side-views/manifest.json'
MODEL_SOURCES = {
    'king': ('assets/king-projections/angle-54/mesh.json', 'assets/king-projections/angle-54/profile.json'),
    'queen': ('assets/queen-projections/angle-54/mesh.json', 'assets/queen-projections/angle-54/fit.json'),
    'rook': ('assets/rook-projections/angle-54/mesh.json', 'assets/rook-projections/angle-54/profile.json'),
    'bishop': ('assets/bishop/mesh.json', 'scripts/bishop/profile.json'),
    'knight': ('assets/knight/mesh.json', 'assets/knight/reconstruction.json'),
    'pawn': ('assets/pawn/mesh.json', 'scripts/pawn/profile.json'),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def widest_row(mask, start, stop):
    rows = []
    for y in range(start, stop):
        xs = np.flatnonzero(mask[y])
        if len(xs):
            rows.append((int(xs[-1] - xs[0] + 1), y, int(xs[0]), int(xs[-1] + 1)))
    width = max(row[0] for row in rows)
    matches = [row for row in rows if row[0] == width]
    return matches[len(matches) // 2]


def original_measurement(piece):
    # The white sprites expose the same base geometry more clearly than the dark ones.
    file = f'references/lichess-staunton-3d/White-{piece.title()}.png'
    path = ROOT / file
    im = np.array(Image.open(path).convert('RGBA'))
    assert im.shape == (300, 300, 4), file
    red, blue, alpha = im[:, :, 0].astype(float), im[:, :, 2].astype(float), im[:, :, 3]
    widths = {}
    for threshold in [25, 35, 45, 55, 65]:
        mask = (alpha >= 200) & (red > threshold) & (red > 1.3 * blue)
        measurement = widest_row(mask, 150, 260)
        widths[str(threshold)] = measurement[0]
        if threshold == 35:
            width, y, left, right = measurement
    return dict(file=file, sha256=digest(path), base_width_px=width,
                measured_row=y, left_px=left, right_px=right,
                threshold_sensitivity_widths_px=widths)


def cutout_measurement(file):
    path = ROOT / file
    im = Image.open(path)
    assert im.mode == 'RGBA', file
    alpha = np.array(im.getchannel('A'))
    assert alpha.min() == 0 and alpha.max() == 255
    assert (alpha == 0).mean() > .5, 'Expected genuinely transparent surrounding background'
    mask = alpha >= 128
    ys, xs = np.where(mask)
    top, bottom = int(ys.min()), int(ys.max() + 1)
    bounds = [int(xs.min()), top, int(xs.max() + 1), bottom]
    width, y, left, right = widest_row(mask, int(top + .75 * (bottom - top)), bottom)
    return dict(file=file, sha256=digest(path), width=im.width, height=im.height,
                bounds_px=bounds, base_width_px=width, base_center_x_px=(left + right) / 2,
                measured_row=y, left_px=left, right_px=right, ground_y_px=bottom,
                fully_transparent_fraction=round(float((alpha == 0).mean()), 5))


def model_measurement(piece):
    file, camera_file = MODEL_SOURCES[piece]
    path = ROOT / file
    meta = json.loads(path.read_text(encoding='utf-8'))
    camera = json.loads((ROOT / camera_file).read_text(encoding='utf-8'))
    elevation = camera['reference_camera']['elevation_degrees'] if piece == 'knight' else camera['elevation']
    assert elevation == 54, (piece, elevation)
    binary = str(Path(file).with_suffix('.bin')).replace('\\', '/')
    raw = (ROOT / binary).read_bytes()
    assert len(raw) == meta['totalByteLength']
    vertices = np.ndarray((meta['vertexCount'], 3), dtype='<f4', buffer=raw,
                          offset=meta.get('vertexByteOffset', 0) + meta.get('positionOffsetBytes', 0),
                          strides=(meta['vertexStrideBytes'], 4)).astype(float)
    lo, hi = vertices.min(axis=0), vertices.max(axis=0)
    assert np.allclose(hi - lo, meta['bounds']['size'], atol=1e-5)
    height = float(hi[2] - lo[2])
    # In particular, do not mistake the knight's overhanging muzzle for its base.
    base = vertices[vertices[:, 2] <= lo[2] + .25 * height]
    xy_widths = base[:, :2].max(axis=0) - base[:, :2].min(axis=0)
    assert abs(xy_widths[0] / xy_widths[1] - 1) < .01, (piece, xy_widths)
    diameter = float(max(xy_widths))
    return dict(file=file, sha256=text_digest(path), binary=binary, binary_sha256=digest(ROOT / binary),
                camera_file=camera_file, camera_sha256=text_digest(ROOT / camera_file), text_hash_normalization='CRLF to LF',
                assumed_elevation_degrees=elevation, height=height, base_diameter=diameter,
                base_xy_widths=xy_widths.tolist(), base_search_max_z=float(lo[2] + .25 * height),
                base_vertex_count=len(base), height_to_base=height / diameter)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    measured = []
    for item in manifest['pieces']:
        measured.append(dict(piece=item['piece'], original=original_measurement(item['piece']),
                             cutout=cutout_measurement(item['file']), model=model_measurement(item['piece'])))
    king = measured[0]
    assert king['piece'] == 'king'
    king_height = king['cutout']['ground_y_px'] - king['cutout']['bounds_px'][1]
    king_scale = 430 / king_height
    for row in measured:
        original, cutout = row['original'], row['cutout']
        ratio = original['base_width_px'] / king['original']['base_width_px']
        # Models use arbitrary world units; normalize by their round bases, then
        # recover cross-piece scale from the original sprites' diameter ratios.
        height_ratio = ratio * row['model']['height_to_base'] / king['model']['height_to_base']
        target_height = 430 * height_ratio
        cutout_height = cutout['ground_y_px'] - cutout['bounds_px'][1]
        baseline_scale = king_scale * king['cutout']['base_width_px'] * ratio / cutout['base_width_px']
        scale = target_height / cutout_height
        row['height_check'] = dict(height_ratio_to_king=height_ratio,
                                   previous_height_ratio_to_king=cutout_height * baseline_scale / 430,
                                   uniform_correction_factor=scale / baseline_scale)
        row['base_ratio_to_king'] = ratio
        row['display'] = dict(scale=scale, image_width_px=cutout['width'] * scale,
                              image_height_px=cutout['height'] * scale,
                              left_from_center_px=-cutout['base_center_x_px'] * scale,
                              top_px=450 - cutout['ground_y_px'] * scale,
                              visible_height_px=(cutout['ground_y_px'] - cutout['bounds_px'][1]) * scale,
                              base_width_px=cutout['base_width_px'] * scale)
        print(f"{row['piece']:6s}: original base {original['base_width_px']:3d}px; "
              f"estimated height {height_ratio:.1%} of king; displayed {target_height:.1f}px")
    report = dict(date='2026-10-05', anchor='king',
                  method='For every piece, multiply its model height/base-diameter ratio by its original sprite base-width ratio to the king, then divide by the king model height/base ratio. Uniformly scale the cutout to that estimated relative height. King is 430px tall; all feet share one ground line. No image stretching.',
                  assumptions='Model interpretations at a common assumed 54-degree elevation, not recovered exact physical dimensions. Original sprites are assumed to share render scale. Generated side-image proportions differ from model proportions, so their displayed base widths need not exactly match original width ratios. Knight geometry prioritizes its approved generated side guide; its original-view fit is weaker.',
                  model_measurement=dict(base_search='Lower quarter of mesh height; use maximum XY extent of the round base, excluding the knight muzzle', elevation_degrees=54),
                  original_measurement=dict(rows=[150, 260], alpha_min=200, red_min_exclusive=35,
                                            red_to_blue_min_exclusive=1.3,
                                            note='Exclude blurred shadows; brightest white side gives the clearest outline. Threshold sensitivity records the few-pixel ambiguity.'),
                  cutout_measurement=dict(alpha_min=128, base_search='Lower quarter of opaque object',
                                          bounds='[left, top, right, bottom], right/bottom exclusive'),
                  display=dict(king_height_px=430, ground_y_px=450, stage_height_px=452, min_slot_width_px=220),
                  pieces=measured)
    (ROOT / 'assets/side-views/scale.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

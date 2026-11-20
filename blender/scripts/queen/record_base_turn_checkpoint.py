"""Reproduce checkpoint 33 measurements and comparisons from saved evidence.

The meridian plot is a cubic B-spline approximation, not an evaluated Blender
mesh. Actual Cycles renders and the scoped Blender validator are authoritative.
Run after the accepted model's fixed/side renders and comparison reports exist.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.interpolate import BSpline

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/queen-mission/iteration-033'
ASSETS = ROOT / 'assets/queen'
PRIOR = ROOT / 'history/queen-mission-032'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def background(im):
    im = im.convert('RGBA')
    canvas = Image.new('RGBA', im.size, (15, 20, 26, 255))
    canvas.alpha_composite(im)
    return canvas.convert('RGB')


def main():
    controls = np.load(OUT / 'control-comparison.npz')
    before, after = controls['before'], controls['after']
    changed = np.flatnonzero(np.any(before != after, axis=(1, 2))).tolist()
    assert changed == list(range(9, 22)), changed
    assert np.array_equal(before[:, :, 2], after[:, :, 2])
    assert np.array_equal(before[:9], after[:9])
    assert np.array_equal(before[22:], after[22:])
    r0, r1 = [np.linalg.norm(c[:, :, :2], axis=2).mean(1) for c in (before, after)]
    z = before[:, :, 2].mean(1)
    save_json('geometry-delta.json', {
        'changed_rings_from_checkpoint_32': changed,
        'all_heights_bit_identical': True,
        'controls_0_to_8_and_22_onward_bit_identical': True,
        'foot_wall_socket_stem_collars_crown_egg_preserved': True,
        'radii_before_after': {str(i): [float(r0[i]), float(r1[i])] for i in changed},
        'socket_seat_height': float(z[38]),
        'socket_wall_height': float(z[33] - z[29]),
        'socket_wall_radius': float(r1[31]),
        'socket_shelf_radial_span': float(r1[33] - r1[38]),
        'max_radius_change': float(np.max(np.abs(r1 - r0))),
        'source_blend_sha256': sha(PRIOR / 'queen-rebuilt.blend'),
        'accepted_blend_sha256': sha(ROOT / 'models/queen/queen-rebuilt.blend'),
    })

    refs = ['references/lichess-staunton-3d/Black-Queen.png',
            'references/lichess-staunton-3d/White-Queen.png',
            'assets/queen/reference.png', 'assets/queen/concepts/side-01.png',
            'assets/side-views/defaults.json']
    hashes = {p: sha(ROOT / p) for p in refs}
    assert hashes == json.loads((ROOT / 'docs/queen-mission/iteration-032/source-hashes.json').read_text())
    save_json('source-hashes.json', hashes)

    fit = json.loads((ASSETS / 'finish-comparison.json').read_text())['silhouette_iou']['revised_54_degree']
    original = 100 * fit['original_black']
    save_json('scores.json', {
        'original_black_iou_percent': original,
        'selected_highres_iou_percent': 100 * fit['selected_highres'],
        'subjective': {'interior_and_side_shape': 90, 'wood_color': 85,
                       'grain_texture': 79, 'lighting': 76},
        'working_mean_percent': (original + 90 + 85 + 79 + 76) / 5,
        'holistic_range_percent': [80, 85],
        'reason': 'One continuous lower-flare turn replaces the extra inflection and shading band; the groove is slightly shallower. All heights and the socket shelf/drop remain exact. Material and lighting are unchanged.',
        'complete': False,
    })

    # Cubic limit meridian diagnostic; actual render geometry uses subdivision 2.
    knots = np.arange(-3, len(z) + 1)
    t = np.linspace(11, 22, 1000) - 1
    bz = BSpline(knots, z, 3)
    zz, dz, d2z = bz(t), bz(t, 1), bz(t, 2)
    chart = Image.new('RGB', (880,700), (15,20,26))
    draw = ImageDraw.Draw(chart)
    measures = []
    for radius, name, color in [(r0, 'Checkpoint 32', '#c8cbd1'), (r1, 'Checkpoint 33', '#79d3ed')]:
        br = BSpline(knots, radius, 3)
        rr, dr, d2r = br(t), br(t, 1), br(t, 2)
        curvature = (d2r * dz - dr * d2z) / (dr * dr + dz * dz) ** 1.5
        take = (t + 1 > 14) & (t + 1 < 20)
        reversals = int(np.count_nonzero(np.diff(np.sign(curvature[take]))))
        measures.append({'model': name, 'curvature_sign_changes_rings_14_to_20': reversals,
                         'sampled_peak_radius': float(rr.max()), 'peak_height': float(zz[rr.argmax()])})
        draw.line(list(zip(65+(rr-.98)*6200, 650-(zz-.22)*2000)), fill=color, width=3)
        draw.text((440, 90 + 65*(len(measures)-1)), f'{name}: {reversals} curvature reversals', fill=color)
    draw.text((25,15), 'Cubic subdivision meridian approximation: lower flare / groove', fill='white')
    draw.text((440,300), 'Actual Cycles renders use subdivision level 2.', fill='white')
    draw.text((440,330), 'Radius horizontal; physical height vertical.', fill='white')
    chart.save(OUT / 'accepted-meridians.png')
    save_json('accepted-curvature.json', measures)

    font_path = Path('C:/Windows/Fonts/segoeui.ttf')
    font = ImageFont.truetype(str(font_path), 21) if font_path.exists() else ImageFont.load_default(size=21)
    side = Image.new('RGB', (670,695), (15,20,26))
    d = ImageDraw.Draw(side)
    for i, (name, path) in enumerate([('Before - checkpoint 32', PRIOR / 'queen-finished-profile.png'),
                                     ('After - checkpoint 33', ASSETS / 'queen-finished-profile.png')]):
        x = i*330+5
        d.text((x,12), name, font=font, fill='white')
        side.paste(background(Image.open(path)).crop((140,175,460,810)), (x,52))
    side.save(OUT / 'side-before-after.png')
    detail = Image.new('RGB', (800,600), (15,20,26))
    d = ImageDraw.Draw(detail)
    for i, (name, folder) in enumerate([('Checkpoint 32', PRIOR), ('Checkpoint 33', ASSETS)]):
        d.text((i*400+8,10), name, font=font, fill='white')
        for row, filename in enumerate(['queen-wood-profile.png', 'queen-finished-profile.png']):
            crop = background(Image.open(folder / filename)).crop((145,615,455,810)).resize((400,252))
            detail.paste(crop, (i*400,40+row*275))
    detail.save(OUT / 'base-before-after.png')
    for name in ['finish-comparison.json','finish-validation.json','model-validation.json',
                 'profile-landmarks.json','side-registration.json','overlay-metrics.json']:
        (OUT / name).write_bytes((ASSETS / name).read_bytes())
    print('Checkpoint 33 scope, source preservation, scorecard and comparisons recorded.')


if __name__ == '__main__':
    main()

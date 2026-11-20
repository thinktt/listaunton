"""Make comparison plates from the approved references and actual saved-scene renders."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
from reference_images import black, registered, silhouette, iou

INK = '#ece8e1'
BG = '#262a29'
SMALL = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 16)
HEAD = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 22)
RES = Image.Resampling.LANCZOS


def read(filename):
    return Image.open(OUT / filename).convert('RGBA')


def card(canvas, image, rect, color=None):
    x, y, w, h = rect
    if color:
        image = Image.alpha_composite(Image.new('RGBA', image.size, color), image.convert('RGBA'))
    else:
        image = black(image)
    image = ImageOps.contain(image, (w, h), RES)
    canvas.paste(image.convert('RGB'), (x + (w - image.width) // 2, y + (h - image.height) // 2))


def title(canvas, xy, value, font=SMALL):
    ImageDraw.Draw(canvas).text(xy, value, fill=INK, font=font)


def compare_fixed():
    sources = registered()
    names = ['Original', 'Black 2', '12B parent', '13B eye carving']
    full = [sources['original'], sources['selected'], read('parent-wood.png'), read('wood.png')]
    canvas = Image.new('RGB', (1120, 798), BG)
    title(canvas, (12, 4), 'Registered carving at 54°', HEAD)
    for i, (name, im) in enumerate(zip(names, full)):
        x = i*280
        title(canvas, (x+10, 40), name)
        card(canvas, im.crop((151, 270, 791, 1070)), (x, 66, 280, 350))
        card(canvas, im.crop((448, 444, 565, 524)), (x, 434, 280, 192))
        # At native game scale the whole piece occupies an 80-pixel square.
        card(canvas, im.crop((143, 268, 943, 1068)), (x+100, 670, 80, 80))
    title(canvas, (12, 758), '80 px board crop, with the original registration and equal scale in all four columns.')
    canvas.save(OUT/'fixed-and-board.png')
    parent, candidate = [silhouette(im) for im in full[2:]]
    alpha = [np.asarray(im)[:, :, 3] for im in full[2:]]
    side_alpha = [np.asarray(read(name))[:, :, 3] for name in ['parent-side.png','wood-side.png']]
    score = {
        'fixed_parent_candidate_mask_iou': iou(parent, candidate),
        'alpha_above_127_number_changed': int(np.count_nonzero((alpha[0]>127) != (alpha[1]>127))),
        'side_alpha_above_127_number_changed': int(np.count_nonzero((side_alpha[0]>127) != (side_alpha[1]>127))),
        'candidate': {},
        'parent': {},
    }
    for name, ref in zip(['original', 'black2'], full[:2]):
        reference_mask=silhouette(ref, True)
        score['parent'][name]=iou(parent, reference_mask)
        score['candidate'][name]=iou(candidate, reference_mask)
    return score


def profiles():
    candidate = OUT/'portraits-B'
    parent = OUT/'portraits-parent'
    for folder,model in [(parent,'parent.blend'),(candidate,'knight.blend')]:
        index = json.loads((folder/'source.json').read_text())
        assert index['model'] == hashlib.sha256((OUT/model).read_bytes()).hexdigest()
        for name,expected in index['views'].items():
            assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == expected
    canvas = Image.new('RGB', (1140, 680), BG)
    title(canvas, (10, 7), 'The two flanks under matched broad lamps', HEAD)
    for ci, (name, folder) in enumerate([('12B parent', parent), ('13B', candidate)]):
        for j, side in enumerate(['near', 'far']):
            x = (2*ci + j)*285
            title(canvas, (x+10, 48), f'{name} · {side} side')
            for row, material in enumerate(['walnut', 'clay']):
                im = Image.open(folder/f'{material}-{side}.png')
                # Keep each recorded face in its actual left/right orientation.
                card(canvas, im.crop((75, 20, 450, 324)), (x, 82+row*262, 285, 239))
    title(canvas, (10, 622), 'Native walnut above, neutral clay below. Both eyes use the same real-world framing and lamp arrangement.')
    canvas.save(OUT/'two-flanks.png')


def moving(side):
    canvas = Image.new('RGB', (1020, 856), BG)
    title(canvas, (10, 5), 'A broad lamp moving across the '+side+' eye', HEAD)
    for ci, label in enumerate(['Behind', 'Overhead', 'Noseward']):
        title(canvas, (100+ci*303, 42), label)
    for row, (version, finish) in enumerate([('parent','walnut'),('B','walnut'),('parent','clay'),('B','clay')]):
        y = 70+row*191
        title(canvas, (7, y+18), '12B' if version=='parent' else '13B')
        title(canvas, (7, y+42), finish)
        for ci in range(3):
            im = read(f'moving-{version}-{side}-{finish}-{ci}.png')
            card(canvas, im.crop((93, 40, 348, 217)), (98+ci*303, y, 266, 185))
    canvas.save(OUT/('moving-'+side+'.png'))


def common_fixed():
    canvas=Image.new('RGB',(890,414),BG)
    title(canvas,(10,5),'Fixed eye under common lighting',HEAD)
    for i,(version,label) in enumerate([('parent','12B'),('B','13B')]):
        y=65+i*170
        title(canvas,(7,y+50),label)
        studio='parent-wood.png' if version=='parent' else 'wood.png'
        panels=[('Parent studio',read(f'common-fixed-{version}-walnut.png')),
                ('Neutral clay',read(f'common-fixed-{version}-clay.png')),
                ('Saved studio',read(studio).crop((448,444,594,527)))]
        for j,(heading,im) in enumerate(panels):
            if i==0:title(canvas,(67+j*277,36),heading)
            card(canvas,im,(61+j*277,y,248,166))
    canvas.save(OUT/'common-fixed.png')


def orbit():
    columns = [('Near','near',0),('Front','front',4),('Far','opposite',8),('Rear quarter','rear-quarter',10),('Rear','rear',12)]
    canvas = Image.new('RGB', (1200, 566), BG)
    title(canvas, (10, 6), '13B in the round', HEAD)
    for i, (label, wood, clay) in enumerate(columns):
        x=i*240
        title(canvas, (x+8, 42), label)
        for row, name in enumerate([f'wood-{wood}.png', f'clay-{clay:02d}.png']):
            card(canvas, read(name), (x, 74+row*238, 236, 236))
    canvas.save(OUT/'orbit-proof.png')
    frames=[black(read(f'clay-{i:02d}.png')).resize((400,400),RES) for i in range(16)]
    frames[0].save(OUT/'clay-turn.webp', save_all=True, append_images=frames[1:], duration=180, loop=0, quality=85)


def main():
    metrics=compare_fixed()
    profiles()
    orbit()
    moving('near');moving('far')
    common_fixed()
    files=['parent.blend','knight.blend','parent-pigment.png','pigment.png','wood.png','wood-side.png',
           'fixed-and-board.png','comparison.png','comparison.json','two-flanks.png','moving-near.png','moving-far.png','orbit-proof.png',
           'clay-turn.webp','bilateral-eyes.png','common-fixed.png','verified.json','native-check-knight.json','eyes-B.json',
           'carve.py','lamps.py','pigment.py','eye_uv.py','bilateral_eye.py','orbital.py','lens.py','study.py','socket_sections.py',
           'evidence.py','diagnostics.py','eye_study.py','reference_images.py','eye_portraits.py',
           'moving.py','common_fixed.py','verify.py','mesh_check.py','report.py','reproduce.ps1','parameters.json','REPORT.md',
           'socket-sections.json','socket-sections.png','eye-pigment.json','clay-side.png','clay-fixed.png','uv_check.py','uv-check.json',
           'common-fixed.json','moving-light.json','portraits-B/source.json','portraits-parent/source.json',
           'review-copy/assets/knight/mesh.json','review-copy/assets/knight/mesh.bin',
           'review-copy/assets/knight/varnish.bin','review-copy/assets/knight/camera.json']
    files += [f'clay-{i:02d}.png' for i in range(16)]
    files += [f'wood-{name}.png' for name in ['near','opposite','rear-quarter','rear','front']]
    files += ['parent-wood.png','parent-side.png','field-parent.npz','lower-parent.json','brow-parent.json',
              'brow-trace.json','lower-trace.json','inner-source.json','plot_bilateral_eye.py',
              'review-copy/assets/knight/validation.json']
    evidence={}
    for index in ['moving-light.json','common-fixed.json']:
        evidence.update(json.loads((OUT/index).read_text()))
    for subfolder in ['portraits-B','portraits-parent']:
        evidence.update({str(Path(subfolder)/f):value for f,value in json.loads((OUT/subfolder/'source.json').read_text())['views'].items()})
    params=json.loads((OUT/'parameters.json').read_text())
    evidence.update({'knight.blend':params['model_sha256'],'parent.blend':params['parent_sha256'],
        'pigment.png':params['pigment_sha256'],'wood.png':params['fixed_sha256'],'wood-side.png':params['side_sha256']})
    files.extend(evidence)
    metrics['sha256']={f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in sorted(set(files))}
    assert all(metrics['sha256'][f]==digest for f,digest in evidence.items())
    (OUT/'proof.json').write_text(json.dumps(metrics,indent=2)+'\n')


if __name__=='__main__':
    main()

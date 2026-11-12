"""Predict bounded warm-light fits from actual collar response passes.

Predictions guide trials only. A saved, reopened full render is required.
"""
import argparse, json, hashlib, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from image_math import blur
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--folder', default='build/bishop-mission/109-collar-basis')
p.add_argument('--out', help='Separate output folder for another spectral hypothesis.')
p.add_argument('--allow-cool', action='store_true')
a = p.parse_args()
folder = ROOT / a.folder
out = ROOT / a.out if a.out else folder
out.mkdir(parents=True, exist_ok=True)
manifest = json.loads((folder / 'manifest.json').read_text())
box = manifest['border']
x0, y0, x1, y1 = box
ref = np.array(Image.open(ROOT / 'assets/bishop/reference.png').convert('RGBA'), dtype=np.float32) / 255
base = np.load(folder / 'off.npy')[y0:y1, x0:x1]
target = ref[y0:y1, x0:x1, :3]
mask = (ref[y0:y1, x0:x1, 3] > .5) & (target.max(2) > 12/255) & (base[:, :, 3] > .999)
mask = blur(mask.astype(np.float32), 3) > .999
core = mask & (target[:, :, 0] > 210/255) & (target[:, :, 1] > 150/255) & (target[:, :, 2] > 70/255)
weight = np.where(core, 2, 1)[mask].astype(np.float32)
t = target[mask]
b = base[:, :, :3][mask]
def srgb(x):
    return np.clip(np.where(x <= .0031308, x*12.92, 1.055*np.maximum(x, 0)**(1/2.4)-.055), 0, 1)
def metrics(pred):
    error = np.abs(pred - target)
    return dict(rgb_mae_8bit=float(error[mask].mean()*255),
                core_mae_8bit=float(error[core].mean()*255),
                weighted_mae_8bit=float((error[mask].mean(1)*weight).sum()/weight.sum()*255))
colors = {'neutral': [1, 1, 1], 'warm-white': [1, .95, .85],
          'cream': [1, .9, .65], 'accepted-gold': [1, .87, .25]}
if a.allow_cool:
    colors.update({'cool-white': [.65, .85, 1], 'blue-fill': [.35, .65, 1]})
panels = [('Selected white 3', target),
          ('Accepted 013 (actual pass)', srgb(np.load(folder / 'accepted.npy')[y0:y1, x0:x1, :3]))]
records = {}
for label, spec in manifest['cases'].items():
    response = np.load(folder / (label + '.npy'))[y0:y1, x0:x1, :3] - base[:, :, :3]
    response = np.maximum(response, 0)
    d = response[mask]
    best = None
    for color_name, color in colors.items():
        c = np.array(color)
        for energy in range(0, 401, 4):
            prediction = srgb(b + d*c*(energy/manifest['basis_energy']))
            loss = float((np.abs(prediction-t).mean(1)*weight).sum()/weight.sum())
            if best is None or loss < best[0]:
                best = (loss, energy, color_name, color)
    _, energy, color_name, color = best
    predicted = srgb(base[:, :, :3] + response*np.array(color)*(energy/manifest['basis_energy']))
    records[label] = dict(energy=energy, color_name=color_name, color=color, **metrics(predicted))
    prefix = '113-collar-' if a.allow_cool else '110-collar-'
    config = dict(source=manifest['source'], variant=prefix+label, samples=128,
                  adaptive_sampling=False, lights=[dict(spec, energy=energy, color=color)],
                  fitting_evidence=out.relative_to(ROOT).as_posix()+'/fit.json')
    (out / ('config-'+label+'.json')).write_text(json.dumps(config, indent=2)+'\n', newline='\n')
    panels.append((f'PREDICTION {label}: {energy} W, {color_name}', predicted))
records['accepted'] = metrics(panels[1][1])
records['off'] = metrics(srgb(base[:, :, :3]))
result = dict(note='Predictions from 96-sample linear response passes, not final renders or mission scores. Fixed crop, original pixel coordinates, same reference. Core weight 2. Light power 0..400 W; fixed spectral tints listed below.',
              spectral_tints=colors, response_folder=a.folder,
              source=manifest['source'], source_sha256=manifest['source_sha256'], border=box,
              shared_pixels=int(mask.sum()), core_pixels=int(core.sum()), cases=records,
              reference_sha256=hashlib.sha256((ROOT/'assets/bishop/reference.png').read_bytes()).hexdigest())
(out/'fit.json').write_text(json.dumps(result, indent=2)+'\n', newline='\n')
cw, ch = 600, 375
canvas = Image.new('RGB', (3*cw, ((len(panels)+2)//3)*ch), '#171b21')
draw = ImageDraw.Draw(canvas)
for i, (label, pixels) in enumerate(panels):
    x, y = i%3*cw, i//3*ch
    im = Image.fromarray(np.uint8(np.clip(pixels, 0, 1)*255+.5)).resize((600, 338), Image.Resampling.LANCZOS)
    canvas.paste(im, (x, y+32))
    draw.text((x+10, y+10), label, fill='white')
canvas.save(out/'predictions.png')
print(json.dumps(records, indent=2))

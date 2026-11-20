"""Compare the broad wood face and its carved inner edge at the fixed board angle."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def luminance(image, radius=2):
    return np.asarray(image.filter(ImageFilter.GaussianBlur(radius)), dtype=float) @ [.2126, .7152, .0722]


def relative_valley(field, rows, x):
    shoulder = (field[rows, x-8] + field[rows, x+8]) / 2
    return (shoulder - field[rows, x]) / np.maximum(shoulder, 12)


def curved_valley(field, rows, outer, hollow):
    """Find each image's own smooth trough within the wood, excluding the carved edge."""
    width = field.shape[1]
    costs = np.full(width, np.inf)
    previous = np.zeros((len(rows), width), dtype=int)
    for i, y in enumerate(rows):
        span = hollow[i]-outer[i]
        x = np.arange(round(outer[i]+.24*span), round(outer[i]+.72*span)+1)
        expense = -relative_valley(field, np.full_like(x, y), x)
        if i:
            step = np.arange(-3,4)
            neighbors = x[:,None]+step
            alternatives = costs[neighbors]+.024*np.abs(step)
            choice = alternatives.argmin(axis=1)
            expense += alternatives[np.arange(len(x)), choice]
            previous[i,x] = neighbors[np.arange(len(x)), choice]
        costs = np.full(width, np.inf)
        costs[x] = expense
    path = [int(costs.argmin())]
    for i in range(len(rows)-1, 0, -1):
        path.append(int(previous[i,path[-1]]))
    return np.array(path[::-1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('round', type=int)
    parser.add_argument('candidates', nargs='*')
    args = parser.parse_args()
    root = args.root.resolve()
    build = root/'build/knight-mission'
    output = build/f'round-{args.round:03}-judge'
    output.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(root/'scripts/knight'))
    from audit_mission import black, registered, silhouette
    references = registered()
    shape = silhouette(references['selected'], True)
    parent_path = build/'round-013-judge/mane-pigment-origin.json'
    source_path = build/'round-011-judge/mane-hollow.json'
    rows, old_arc = np.array(json.loads(parent_path.read_bytes())['path_y_x']).T
    trace = json.loads(source_path.read_bytes())['Black 2']['samples']
    ty, tx = np.array([row[:2] for row in trace]).T
    hollow = np.rint(np.interp(rows, ty, tx)).astype(int)
    outer = np.array([np.flatnonzero(shape[y])[0] for y in rows])
    pictures = {'Original black': references['original'], 'Black 2': references['selected']}
    pictures['Parent'] = Image.open(root/'assets/knight/render.png')
    for code in args.candidates:
        pictures[code] = Image.open(build/f'improvement-{args.round:03}-{code}/wood.png')
    for code in ['parent', *args.candidates]:
        folder = output/f'mane-passes-{code}'
        if (folder/'pigment.png').exists():
            pictures[code.title()+' pigment'] = Image.open(folder/'pigment.png')
    width, height = 165, 214
    sheet = Image.new('RGB', (width*len(pictures), height*2+60), '#232723')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=13)
    box = (178,443,312,616)
    results = {}
    for index,(name,pic) in enumerate(pictures.items()):
        im = black(pic.convert('RGBA'))
        field = luminance(im)
        search = curved_valley(field, rows, outer, hollow)
        valley = relative_valley(field, rows, old_arc)
        strongest = relative_valley(field, rows, search)
        # The same edge samples in every photograph preserve the registration.
        offsets = np.arange(-7,8)
        minimum = offsets[field[rows[:,None],hollow[:,None]+offsets].argmin(axis=1)]
        deepest = hollow+minimum
        results[name] = {
            'darkness_on_parent_mark_percent':round(100*float(np.median(valley)),2),
            'strongest_smooth_mark_percent':round(100*float(np.median(strongest)),2),
            'share_parent_line_darker_by_at_least_ten_percent':round(float((valley>.1).mean()),3),
            'distance_from_source_hollow_px':round(float(np.median(np.abs(minimum))),2),
            'real_hollow_median_luminance':round(float(np.median(field[rows, deepest])),2),
            'neck_18px_beyond_hollow':round(float(np.median(field[rows,hollow+18])),2),
        }
        crop = im.crop(box).resize((width-2,height), Image.Resampling.LANCZOS)
        x = index*width
        draw.text((x+5,4),name,font=font,fill='#f0f1e7')
        sheet.paste(crop,(x,25))
        sheet.paste(crop,(x,32+height))
        for line,color in [(old_arc,'#daa771'),(hollow,'#77c9b9')]:
            points = [(x+(col+.5-box[0])*(width-2)/(box[2]-box[0]),
                       height+32+(y+.5-box[1])*height/(box[3]-box[1])) for y,col in zip(rows,line)]
            draw.line(points,fill=color,width=1)
    draw.text((5,2*height+40),'Copper follows the extra pigment mark. Green follows the carved inner edge in the reference.', font=font, fill='#e7e7dc')
    sheet.save(output/'mane-surface-comparison.png')
    report = {'method':'Use the same fixed-camera track for the parent pigment mark and the source hollow on every image. Also search independently for any coherent dark trough inside the broad wood face, allowing lateral shifts of three pixels per two-pixel row. Small wood pores differ between references. The whole color and moving-light views guide judgment.',
              'parent_mark_trace_sha256':digest(parent_path),'source_hollow_trace_sha256':digest(source_path),'results':results}
    (output/'mane-surface-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(results))

if __name__=='__main__':
    main()

"""Compare the king's cross seat at fixed registration and at level elevation."""
from argparse import ArgumentParser
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]


def font(size):
    for location in ('C:/Windows/Fonts/segoeui.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if Path(location).is_file():
            return ImageFont.truetype(location,size)
    return ImageFont.load_default(size=size)


def image(path):
    with Image.open(path) as source:
        return source.convert('RGBA')


def photo(source):
    backdrop = Image.new('RGBA',source.size,'#171819')
    backdrop.alpha_composite(source)
    return backdrop.convert('RGB')


def front_edge_rows(source):
    # Across the central front arc, these are the dark lines below each bead.
    blurred = source.convert('L').filter(ImageFilter.GaussianBlur(1.6))
    scan = np.mean(np.asarray(blurred)[:,497:514],axis=1)
    rows = {}
    for name, (lo,hi) in {'upper':(218,241), 'lower':(248,275)}.items():
        i = int(np.argmin(scan[lo:hi])) + lo
        rows[name] = {'y':i,'luma':round(float(scan[i]),2),'interior_to_window':lo<i<hi-1}
    return rows


def front_luma(source):
    luma = np.asarray(source.convert('L').filter(ImageFilter.GaussianBlur(1.6)),dtype=float)
    scan = luma[:,497:514].mean(axis=1)
    crests = {}
    for name, (lo,hi) in {'upper':(214,230),'lower':(240,257)}.items():
        i = int(np.argmax(scan[lo:hi])) + lo
        crests[name] = {'y':i,'luma':round(float(scan[i]),2),'interior_to_window':lo<i<hi-1}
    return crests,luma[183:271,420:591]


def make(config, out):
    out.mkdir(parents=True, exist_ok=True)
    assets = ROOT/'assets/king'
    stage = ROOT/'build/king-mission'/config['variant']
    old = (ROOT/config['king_source']).parent
    ref = image(assets/'reference.png')
    registration = json.loads((assets/'original-alignment.json').read_text())
    scale, x, y = (registration[k] for k in ('scale','x','y'))
    original = image(assets/'original.png').transform(ref.size,Image.Transform.AFFINE,
        (scale*300/ref.width,0,x*3,0,scale*300/ref.width,y*3),Image.Resampling.BILINEAR)
    prior, current = (image(path) for path in (old/'render.png',stage/'wood-reopened.png'))
    guide = image(assets/'concepts/side-01-cutout.png')
    before_side, side = (image(path) for path in (old/'profile.png',stage/'profile.png'))
    plate = Image.new('RGB',(858,434),'#202325')
    draw = ImageDraw.Draw(plate)
    width, height = 272,160
    fixed_box = (367,131,639,291)
    # The level model crops share their camera and coordinates. The imagined
    # guide is registered by the foot-width scale and centered on its cap.
    side_box = (208,161,392,269)
    side_scale = json.loads((assets/'side-registration.json').read_text())['scale']
    guide_box = tuple(round(t) for t in (
        623+(side_box[0]-300)*side_scale,270+(side_box[1]-243)*side_scale,
        623+(side_box[2]-300)*side_scale,270+(side_box[3]-243)*side_scale))
    cards = [('Lichess original',original,fixed_box),('Black candidate 1',ref,fixed_box),
             ('Revised king · 54°',current,fixed_box),('Imagined side guide',guide,guide_box),
             ('Previous king · side',before_side,side_box),('Revised king · side',side,side_box)]
    for i,(label,im,rectangle) in enumerate(cards):
        left, top = 8+285*(i%3), 7+212*(i//3)
        draw.text((left+1,top),label,font=font(18),fill='#f3ece3')
        crop = photo(im).crop(rectangle).resize((width,height),Image.Resampling.LANCZOS)
        plate.paste(crop,(left,top+30))
    plate.save(out/'crown-seat-comparison.png', optimize=True)
    views = [('original',original),('selected',ref),('previous',prior),('revised',current)]
    readings = {name:front_edge_rows(im) for name,im in views}
    crests, patches = {}, {}
    for name,im in views:
        crests[name],patches[name] = front_luma(im)
    errors = {}
    for ref_name in ('original','selected'):
        errors[ref_name] = {}
        for model in ('previous','revised'):
            a,b = patches[ref_name],patches[model]
            errors[ref_name][model] = dict(absolute_luma_error=float(abs(a-b).mean()),
                correlation=float(np.corrcoef(a.ravel(),b.ravel())[0,1]))
    report = {'description':'Darkest mean luma below each front bead, x=497..513 on the registered 1254px fixed image after 1.6px Gaussian blur. A minimum on a window boundary is not a resolved trough.',
              'measurements':readings, 'highlight_rows':crests, 'front_patch_xyxy':[420,183,591,271],
              'front_patch_comparison':errors}
    (out/'front-arc-measurements.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(readings))


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path)
    parser.add_argument('output',type=Path)
    args = parser.parse_args()
    make(json.loads(args.config.read_text(encoding='utf-8-sig')),args.output)

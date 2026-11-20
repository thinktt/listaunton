"""Compare king and queen base renders at the same native side-camera scale."""
from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
PATCHES = {
    'flare': (.20, .70, .32, .53),
    'left bevel': (-1.035, -.91, .17, .29),
    'right bevel': (.92, 1.035, .16, .26),
    'socket edge': (.36, .53, .89, 1.09),
}


def font(size, bold=False):
    paths = [('C:/Windows/Fonts/seguisb.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf'),
             ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    return next((ImageFont.truetype(p,size) for p in paths if Path(p).is_file()),ImageFont.load_default(size=size))


def samples(image, ppm, center_z):
    image = np.asarray(image)
    y = np.uint8(image[:,:,:3] @ np.array([.2126,.7152,.0722]))
    y = np.asarray(Image.fromarray(y).filter(ImageFilter.GaussianBlur(1)))
    height,width = y.shape
    x,z = np.meshgrid((np.arange(width)+.5-width/2)/ppm,center_z+(height/2-np.arange(height)-.5)/ppm)
    readings = {}
    for name,(x0,x1,z0,z1) in PATCHES.items():
        values = y[(x>x0)&(x<x1)&(z>z0)&(z<z1)&(image[:,:,3]>240)]
        readings[name] = dict(median=float(np.median(values)),p99=float(np.quantile(values,.99)),
                              area_above_100=float(np.count_nonzero(values>100)/ppm**2))
    return readings


def build(spec, queen_profile, out):
    stage = ROOT / 'build/king-mission' / spec['variant']
    out.mkdir(parents=True,exist_ok=True)
    prior = (ROOT / spec['king_source']).with_name('profile.png')
    plate = Image.new('RGB',(1020,304),'#1b1e20')
    pen = ImageDraw.Draw(plate)
    reading = {}
    for i,(label,path,scale,center) in enumerate([
            ('Queen',queen_profile,6.6,2.55), ('Previous king',prior,6,2.65),
            ('Revised king',stage/'profile.png',6,2.65)]):
        image = Image.open(path).convert('RGBA')
        ppm = image.height/scale
        factor = ppm/145
        transform = (factor,0,image.width/2-170*factor,0,factor,image.height/2+center*ppm-225*factor)
        crop = image.transform((340,232),Image.Transform.AFFINE,transform,Image.Resampling.BICUBIC)
        background = Image.new('RGBA',crop.size,'#25292b')
        background.alpha_composite(crop)
        plate.paste(background.convert('RGB'),(340*i,44))
        pen.text((340*i+170,10),label,font=font(20,True),anchor='mt',fill='#f1e9de')
        reading[label] = dict(source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                              pixels_per_unit=ppm,measurements=samples(image,ppm,center))
    pen.text((510,282),'Level Blender renders at the same physical scale and floor height',
             font=font(15),fill='#c1c4c0',anchor='mt')
    plate.save(out/'base-comparison.png',optimize=True)
    report = dict(window_xz_model_units=PATCHES, method='8-bit Rec. 709 luma, one-pixel Gaussian blur, alpha >240. Each region is evaluated in model coordinates.',views=reading)
    (out/'base-light-comparison.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

    reference = Image.open(ROOT/'assets/king/reference.png').convert('RGBA')
    reg = json.loads((ROOT/'assets/king/original-alignment.json').read_text())
    s,x,y = (reg[k] for k in ('scale','x','y'))
    original = Image.open(ROOT/'assets/king/original.png').convert('RGBA').transform(
        reference.size,Image.Transform.AFFINE,(s*300/reference.width,0,x*3,0,s*300/reference.width,y*3),Image.Resampling.BILINEAR)
    fixed = Image.new('RGB',(791,491),'#1b1e20')
    pen = ImageDraw.Draw(fixed)
    for i,(label,image) in enumerate([('Lichess original',original),('Black candidate 1',reference),
                                      ('Revised king · 54°',Image.open(stage/'wood-reopened.png').convert('RGBA'))]):
        bg = Image.new('RGBA',image.size,'black')
        bg.alpha_composite(image)
        view = bg.convert('RGB').crop((185,0,815,1110)).resize((253,446),Image.Resampling.LANCZOS)
        left = 8+261*i
        fixed.paste(view,(left,36))
        pen.text((left+126,9),label,font=font(15),anchor='mt',fill='#f1e9de')
    fixed.save(out/'fixed-comparison.png',optimize=True)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--queen-profile',type=Path,default=ROOT/'assets/queen/queen-wood-profile.png')
    args=parser.parse_args()
    build(json.loads(args.config.read_text(encoding='utf-8-sig')),args.queen_profile,args.output)

"""Compare the king crown in its saved cameras. The imagined guide uses a local rim registration."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from audit_mission import mask, iou
from compare_crown_seat import ROOT, font, front_luma, image, photo, registered_original


def guide_in_profile(assets, size):
    info = json.loads((assets/'side-registration.json').read_text())
    scale = info['scale']
    # Equal foot-width scale; translate the guide to the crown's broad shoulder.
    return image(assets/'concepts/side-01-cutout.png').transform(
        size, Image.Transform.AFFINE, (scale,0,623-300*scale,0,scale,270-243*scale),
        Image.Resampling.BICUBIC)


def guide_errors(guide, model):
    guide_alpha = np.asarray(guide)[:,:,3] > 150
    model_alpha = np.asarray(model)[:,:,3] > 150

    def edge_height(alpha, x):
        yy = np.flatnonzero(alpha[:262,x])
        return int(yy[0])

    # Outside the footprint of either bead, the first opaque pixel from the
    # top traces the turned shoulder on both halves of the silhouette.
    errors = []
    for dx in range(56,86):
        for x in (300+dx,299-dx):
            errors.append(abs(edge_height(guide_alpha,x)-edge_height(model_alpha,x)))
    both = np.s_[63:246,198:402]
    return dict(shoulder_mean_vertical_error_px=float(np.mean(errors)),
                side_crown_iou=iou(guide_alpha[both],model_alpha[both]))


def fixed_comparison(reference, render):
    a, b = mask(reference,True), mask(render)
    metrics = {}
    for feature, crop in {'head': np.s_[:350,:], 'exposed_cross': np.s_[:90,:]}.items():
        metrics[feature+'_iou'] = iou(a[crop],b[crop])
    ref_patch = front_luma(reference)[1]
    render_patch = front_luma(render)[1]
    metrics['seat_mean_luma_error_255'] = float(abs(ref_patch-render_patch).mean())
    def relief(im):
        gray = photo(im).convert('L').filter(ImageFilter.GaussianBlur(2))
        return np.asarray(gray, dtype=float)[38:175,408:604]
    a, b = relief(reference), relief(render)
    metrics['cross_face_mean_luma_error_255'] = float(abs(a-b).mean())
    metrics['cross_face_luma_correlation'] = float(np.corrcoef(a.ravel(),b.ravel())[0,1])
    return metrics


def compare(config, output):
    assets = ROOT/'assets/king'
    stage = ROOT/'build/king-mission'/config['variant']
    prior = (ROOT/config['king_source']).parent
    target = image(assets/'reference.png')
    original = registered_original(assets,target)
    prev_side = image(prior/'profile.png')
    side = image(stage/'profile.png')
    old = image(prior/'render.png')
    current = image(stage/'wood-reopened.png')
    guide = guide_in_profile(assets,side.size)
    side_box = (194,65,406,287)
    front_box = (319,0,689,337)

    sheet = Image.new('RGB',(948,684),'#202326')
    draw = ImageDraw.Draw(sheet)
    def row(y, panels, box, h):
        for i,(title,source) in enumerate(panels):
            x = 10+i*313
            draw.text((x+2,y),title,fill='#f5f0e8',font=font(18))
            panel = photo(source).crop(box)
            panel.thumbnail((302,h),Image.Resampling.LANCZOS)
            if panel.height<h and panel.width<302:
                scale = min(302/panel.width,h/panel.height)
                panel = panel.resize((round(panel.width*scale),round(panel.height*scale)),Image.Resampling.LANCZOS)
            slab = Image.new('RGB',(302,h),'#171819')
            slab.paste(panel,((302-panel.width)//2,(h-panel.height)//2))
            sheet.paste(slab,(x,y+30))

    row(8,[('Imagined side guide',guide),('Previous king · side',prev_side),('Revised king · side',side)],side_box,284)
    row(342,[('Lichess original · 54° fit',original),('Previous king · 54°',old),('Revised king · 54°',current)],front_box,276)
    draw.text((12,657),'Side profiles share a scale and shoulder alignment. The lower row uses the saved camera and original registration.',font=font(15),fill='#c3c4c5')
    output.mkdir(exist_ok=True,parents=True)
    sheet.save(output/'crown-comparison.png')
    result = dict(guide_registration='Scale fixed by foot width. Guide (623,270) maps to profile (300,243).',
                  side_camera_px_per_blender_unit=150,
                  side={name:guide_errors(guide,im) for name,im in [('previous',prev_side),('current',side)]},
                  fixed={source:{key:fixed_comparison(ref,im) for key,im in [('previous',old),('current',current)]}
                         for source,ref in [('original',original),('selected',target)]})
    (output/'crown-fit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    print(json.dumps(compare(json.loads(args.config.read_text(encoding='utf-8-sig')),args.output)))

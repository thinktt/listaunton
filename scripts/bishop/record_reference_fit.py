"""Compare the restored and shortened bishops on their shared physical and image rulers."""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from compare_shared_turning import sprite
from compare_side_refit import panel

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/bishop-mission/iteration-029'
RESTORED = ROOT/'history/bishop-mission-024'
BUILD = ROOT/'build/bishop-mission'
FINAL = BUILD/'185-reference-checkpoint'
GEOMETRY = BUILD/'185-geometry'
read = lambda path: json.loads(path.read_text())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_cut(folder, landmarks, model):
    report = read(folder/'slit-boundary.json')
    assert report['source_sha256'] == digest(model)
    assert abs(report['camera_degrees_measured']-54) < .0001
    labels = np.load(folder/'surface-labels.npy')
    y,x = np.where(labels == 3)
    rows = {r['y']:r for r in report['slit_rows']}
    samples = []
    for u,v in landmarks['slit_dark_center_samples']:
        if 280 <= v <= 410:
            row = rows[v]
            samples.append([v,u,(row['left']+row['right'])/2])
    last = rows[max(rows)]
    return {'button_bounds_ltrb':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],
            'slit_tip_xy':[(last['left']+last['right'])/2,last['y']],
            'slit_centerline_mae_px':float(np.mean([abs(u-measured) for v,u,measured in samples])),
            'source_and_measured_slit_x_by_row':samples}


def color_error(reference, image, selected):
    # The original has about 4.3 native render pixels per sprite pixel.
    # Low-pass the model before comparing to the already interpolated sprite.
    # The selected enlargement is compared at the full native resolution.
    im=image.convert('RGB')
    if not selected:
        scale=read(ROOT/'assets/bishop/original-alignment.json')['scale']*300/reference.width
        im=im.filter(ImageFilter.GaussianBlur(.5/scale))
    ref=np.asarray(reference.convert('RGB'),dtype=float)
    rgb=np.asarray(im,dtype=float)
    regions={'button':(431,164,552,267),'mitre':(352,269,632,479),'body':(200,491,790,1107)}
    r=np.asarray(reference.convert('RGBA'))
    mask=(r[:,:,3]>220)&(r[:,:,:3].max(2)>26)&(np.asarray(image)[:,:,3]>245)
    # Real face-ID distinguishes the cap from the head when the boxes overlap.
    labels=np.load(BUILD/'185-labels-reference-checkpoint/surface-labels.npy')
    result={}
    for name,(x0,y0,x1,y1) in regions.items():
        valid=mask[y0:y1,x0:x1].copy()
        if name=='button':valid&=labels[y0:y1,x0:x1]==3
        error=np.abs(rgb[y0:y1,x0:x1]-ref[y0:y1,x0:x1])[valid]
        result[name]=round(float(error.mean()),3)
    return result


def main():
    original=sprite()
    selected=Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA')
    photo=read(ROOT/'docs/bishop-mission/iteration-027/fit-proposals.json')['original_white_features']
    ruler=read(ROOT/'docs/bishop-mission/iteration-026/side-target.json')
    board=ruler['baseline_board_records']
    per_unit=board['bishop']['height_in_board_pixels']/ruler['old_height']
    king=board['king']['height_in_board_pixels']
    before=Image.open(RESTORED/'render.png').convert('RGBA')
    after=Image.open(FINAL/'wood.png').convert('RGBA')
    sources=[('restored','024',RESTORED/'bishop-rebuilt.blend',ROOT/'docs/bishop-mission/iteration-024/comparison/metrics.json',before),
             ('accepted','reference-checkpoint',FINAL/'bishop.blend',DOC/'comparison/metrics.json',after)]
    result={'source_camera_degrees':54,'original_optical_landmarks':photo,'prior_short_goal_percent':ruler['target_bishop_percent_on_fixed_king_ruler'],
            'ruler':'Original saved orthographic camera and original sprite registration. Physical units for height and diameter. Source image rows use the 1254-pixel render. The 025 board ruler fixes physical height relative to the king.',
            'bounds_for_centered_button':read(DOC/'button-proposals.json')['full_target_bound']}
    for key,case,model,metric,image in sources:
        row=read(GEOMETRY/case/'measures.json')
        assert row['source_sha256']==digest(model)
        q=read(metric)
        assert q['render_sha256']==digest(RESTORED/'render.png' if key=='restored' else FINAL/'wood.png')
        row['registered']={k:v['silhouette_iou'] for k,v in q['images'].items()}
        row['relative_to_floor']=row['floor']
        row['percent_of_king']=100*row['height']*per_unit/king
        row.update(inspect_cut(BUILD/('185-labels-'+case),photo,model))
        row['front_collar_mean_abs_error_px']=float(np.mean(np.abs(np.array(list(row['front_collar_rim_rows'].values()))-photo['collar_trough_rows'])))
        row['wood_rgb_mae_0_to_255']={'original':color_error(original,image,False),'selected':color_error(selected,image,True)}
        result[key]=row
    a,b=result['restored'],result['accepted']
    assert b['height']<a['height'] and abs(b['foot_diameter']-a['foot_diameter'])<1e-6 and a['floor']==b['floor']==0
    assert all(b['registered'][k]>v for k,v in a['registered'].items())
    assert b['front_collar_mean_abs_error_px']<a['front_collar_mean_abs_error_px']
    assert b['slit_centerline_mae_px']<a['slit_centerline_mae_px']
    assert abs(b['front_groove_row']-photo['groove_trough_row'])<1
    spec=read(DOC/'profile-fit.json')['reference_first_height']
    if spec.get('stockier_stem'):
        baseline_stem,stem=a['stem'],b['stem']
        result['minimum_stem_diameter_increase_percent']=100*(stem['minimum_evaluated_diameter']/baseline_stem['minimum_evaluated_diameter']-1)
        result['exposed_stem_span_decrease_percent']=100*(1-stem['socket_to_collar_control_span']/baseline_stem['socket_to_collar_control_span'])
        assert stem['minimum_evaluated_diameter']>baseline_stem['minimum_evaluated_diameter']
        assert stem['socket_to_collar_control_span']<baseline_stem['socket_to_collar_control_span']
        planned=spec['stockier_stem']
        assert abs(stem['socket_to_collar_control_span']-planned['socket_to_collar_control_span'])<1e-5
        assert abs(stem['minimum_evaluated_diameter']-planned['predicted_subdivision_waist_diameter'])<.003
    result['shorter_percent']=100*(1-b['height']/a['height'])
    box=(181,132,804,1135)
    rejected=Image.open(ROOT/'docs/bishop-mission/iteration-027/views/render.png').convert('RGBA')
    ordered=[original,selected,rejected,before,after]
    labels=['Lichess original white','Selected white 3','Rejected shorter bishop','Restored bishop 024','New shorter bishop']
    panel([im.crop(box) for im in ordered],labels,DOC/'fixed-comparison.png',(218,351))
    panel([im.crop((401,141,590,285)) for im in ordered],labels,DOC/'button-comparison.png',(208,158))
    side_images=[Image.open(GEOMETRY/k/'level.png').convert('RGBA') for k in ('024','reference-checkpoint')]
    assert a['side']==b['side']
    crop=(72,19,530,977)
    rims=[]
    for im in side_images:
        mask=im.getchannel('A').point(lambda v:255 if v>127 else 0)
        rims.append(np.asarray(mask.filter(ImageFilter.MaxFilter(5)))!=np.asarray(mask.filter(ImageFilter.MinFilter(5))))
    bg=Image.new('RGBA',side_images[1].size,'#20231f')
    bg.alpha_composite(side_images[1])
    overlay=np.asarray(bg.convert('RGB')).copy()//2
    overlay[rims[0]]=[97,202,224]
    overlay[rims[1]]=[255,183,91]
    overlay[rims[0]&rims[1]]=[229,228,210]
    panel([im.crop(crop) for im in [*side_images,Image.fromarray(overlay)]],
          [f"Restored · {a['height']:.3f} units",f"Stockier · {b['height']:.3f} units",
           'Restored in blue · stockier in gold'],DOC/'side-comparison.png',(240,502))
    (DOC/'measurements.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Fixed camera and level comparisons passed.',result['shorter_percent'],b['registered'],b['slit_centerline_mae_px'])


if __name__=='__main__':
    main()

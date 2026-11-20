"""Compare checkpoint 027 trials in the saved camera and on the owner's fixed side ruler."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw

from compare_shared_turning import sprite
from compare_side_refit import (ASSETS,BUILD,ROOT,DOC as PREVIOUS,read,spans,envelope,
                               screenshot_mask,level,compare_edges,plot_edges,panel,frozen_lineup)
from fit_locked_height import XY_BANDS

DOC=ROOT/'docs/bishop-mission/iteration-027'
ARCHIVE=ROOT/'history/bishop-mission-026'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def trace_score(key,target):
    path=BUILD/('184-slit-'+key)/'slit-boundary.json'
    if not path.exists():return None
    data=read(path)
    cut={row['y']:row for row in data['slit_rows']}
    points=[]
    for x,y in target:
        if y<280 or y>410 or y not in cut:continue
        row=cut[y]
        points.append([y,x,(row['left']+row['right'])/2])
    last=data['slit_rows'][-1]
    cap=np.load(path.parent/'surface-labels.npy')==3
    return {'original_and_real_wall_midpoints':points,
            'centerline_mae_px':float(np.mean([abs(o-m) for _,o,m in points])),
            'visible_tip_xy':[(last['left']+last['right'])/2,last['y']],
            'first_visible_button_row':int(np.where(cap)[0].min()),
            'source_sha256':data['source_sha256']}


def regional(target,model):
    t,l,r=spans(target)
    m,a,b=spans(model)
    ww=np.where(t,r-l+1,0)
    vv=np.where(m,b-a+1,0)
    out={}
    for name,(lo,hi) in XY_BANDS.items():
        ok=t[lo:hi]|m[lo:hi]
        delta=(vv-ww)[lo:hi][ok]
        out[name]={'rows':[lo,hi-1],'mean_signed_full_width_px':float(delta.mean()),
                   'mean_abs_half_width_px_including_missing_rows':float(np.mean(abs(delta))/2),
                   'whole_reference_rows_missing':int((t[lo:hi]&~m[lo:hi]).sum())}
    return out


def evaluate(accepted):
    spec=read(DOC/'side-refit.json')
    keys=['026',*spec['cases']]
    owner=Image.open(PREVIOUS/'owner-side-crop.png').convert('RGBA')
    frame=read(PREVIOUS/'side-target.json')
    assert sha(PREVIOUS/'owner-side-crop.png')==frame['crop_sha256']
    side_target=screenshot_mask(owner,11)
    source=sprite()
    original=np.asarray(source)
    mask=envelope((original[:,:,3]>127)&(original[:,:,:3].max(2)>12))
    selected=Image.open(ASSETS/'reference.png').convert('RGBA')
    optical=read(DOC/'fit-proposals.json')['original_white_features']
    data={'side_calibration':frame,'original_white_optical_landmarks':optical,
          'row_measurement':'Native 1254-pixel frame. Width includes entire absent rows. Optical troughs are cues for physical crests, subject to illumination.'}
    side_images={}
    pictures={}
    walls={}
    for key in keys:
        base=key=='026'
        out=BUILD/('side-refit-compromise' if base else 'fixed-height-'+key)
        saved=ARCHIVE if base else out
        model=saved/('bishop-rebuilt.blend' if base else 'bishop.blend')
        wood=saved/('render.png' if base else 'wood.png')
        clay=saved/('render-clay.png' if base else 'neutral.png')
        metrics=read((PREVIOUS/'comparison' if base else out/'registered')/'metrics.json')
        assert metrics['render_sha256']==sha(wood)
        row=read(out/'measures.json')
        assert row['source_sha256']==sha(model) and abs(row['height']-spec['locked_height'])<5e-7 and abs(row['floor'])<1e-7
        row['registered']={k:v['silhouette_iou'] for k,v in metrics['images'].items()}
        side=level(out,owner,frame)
        row['side_fit']=compare_edges(side_target,envelope(np.asarray(side)[:,:,3]>127))
        row['regional_geometry']=regional(mask,envelope(np.asarray(Image.open(clay).convert('RGBA'))[:,:,3]>127))
        row['front_collar_mean_abs_error_px']=float(np.mean(abs(np.array(list(row['front_collar_rim_rows'].values()))-optical['collar_trough_rows'])))
        slit=trace_score(key,optical['slit_dark_center_samples'])
        if slit:
            assert slit['source_sha256']==row['source_sha256']
            row['slit']=slit
            walls[key]=np.load(BUILD/('184-slit-'+key)/'surface-labels.npy')==2
        data[key]=row
        bg=Image.new('RGBA',side.size,'#20231f');bg.alpha_composite(side)
        side_images[key]=plot_edges(bg,side_target,[255,183,88])
        pictures[key]=(wood,clay)
    (DOC/'measurements.json').write_text(json.dumps(data,indent=2)+'\n')
    if accepted:
        assert accepted in keys
        box=(180,135,806,1145)
        im=lambda p:Image.open(p).convert('RGBA')
        panel([x.crop(box) for x in (source,selected,im(pictures['026'][0]),im(pictures[accepted][0]),im(pictures[accepted][1]))],
              ['Lichess original','White candidate 3','Bishop 026','Bishop 027','Bishop 027 · clay'],DOC/'fixed-comparison.png',(202,326))
        panel([owner,side_images['026'],side_images[accepted]],['Your lineup','Bishop 026','Bishop 027'],DOC/'side-comparison.png',(187,363))
        side_keys=[k for k in keys if k not in ('front-cut','turned-cut')]+[accepted]
        panel([owner]+[side_images[k] for k in dict.fromkeys(side_keys)],['Your lineup']+list(dict.fromkeys(side_keys)),DOC/'side-trials.png',(142,275))
        box=(372,145,634,500)
        annotated=im(pictures[accepted][0]).convert('RGB')
        annotated=plot_edges(annotated,walls[accepted],(85,207,255))
        d=ImageDraw.Draw(annotated)
        d.line([tuple(xy) for xy in optical['slit_dark_center_samples']],fill='#ffcb6a',width=2)
        panel([x.crop(box) for x in (source,im(pictures['026'][1]),im(pictures[accepted][1]),im(pictures[accepted][0]),annotated)],
              ['Original white','026 · clay','027 · clay','027 · wood','Gold trace / blue wall'],DOC/'slit-comparison.png',(194,263))
    for key in keys:
        row=data[key]
        print(key,round(row['registered']['original_white']*100,3),round(row['side_fit']['outline_iou']*100,2),
              round(row['front_collar_mean_abs_error_px'],2),row.get('slit',{}).get('visible_tip_xy'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accepted')
    parser.add_argument('--lineup',action='store_true')
    args=parser.parse_args()
    evaluate(args.accepted)
    if args.lineup:frozen_lineup(DOC,ARCHIVE,('Bishop 026','Bishop 027'))

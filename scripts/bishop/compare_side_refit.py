"""Compare the saved level renders on one physical ruler, and the fixed camera without re-registration."""
import argparse
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from compare_shared_turning import sprite

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/bishop-mission/iteration-026'
BUILD=ROOT/'build/bishop-mission'
ARCHIVE=ROOT/'history/bishop-mission-025'
ASSETS=ROOT/'assets/bishop'
BG='#20231f'
FONT=ImageFont.load_default(size=15)


def read(p):
    return json.loads(p.read_text())


def spans(mask):
    return mask.any(1),mask.argmax(1),mask.shape[1]-1-mask[:,::-1].argmax(1)


def envelope(mask):
    present,left,right=spans(mask)
    x=np.arange(mask.shape[1])[None,:]
    return (x>=left[:,None])&(x<=right[:,None])&present[:,None]


def screenshot_mask(target, threshold):
    v=np.asarray(target.convert('RGB'),dtype=np.int16)
    return envelope(np.abs(v-v[0,0]).max(2)>threshold)


def level(out, target, frame):
    image=Image.open(out/'level.png').convert('RGBA')
    camera=read(out/'measures.json')['side']
    step=camera['pixels_per_unit']/frame['pixels_per_unit']
    return image.transform(target.size,Image.Transform.AFFINE,
        (step,0,image.width/2-frame['x_center']*step,0,step,camera['floor_row']-frame['floor_y']*step),
        Image.Resampling.BICUBIC)


def compare_edges(target, candidate):
    t,l,r=spans(target)
    m,a,b=spans(candidate)
    common=t&m
    err=(np.abs(l-a)+np.abs(r-b))/2
    bands={'button_and_mitre':(28,94),'collars':(94,116),'stem':(116,192),'socket_and_base':(192,249)}
    return {'outline_iou':float((target&candidate).sum()/(target|candidate).sum()),
            'edge_mae_screenshot_px':float(err[common].mean()),
            'top_and_bottom':list(map(int,np.flatnonzero(m)[[0,-1]])),
            'mean_edge_error_by_region':{name:float(err[lo:hi][common[lo:hi]].mean()) for name,(lo,hi) in bands.items()}}


def plot_edges(im, mask, color):
    rim=Image.fromarray((mask*255).astype('uint8'))
    rim=np.asarray(rim)>np.asarray(rim.filter(ImageFilter.MinFilter(3)))
    out=np.array(im.convert('RGB'))
    out[rim]=color
    return Image.fromarray(out)


def panel(images,labels,path,size):
    w,h=size
    result=Image.new('RGB',(len(images)*w,h+33),BG)
    d=ImageDraw.Draw(result)
    for i,(image,label) in enumerate(zip(images,labels)):
        im=image.convert('RGBA').resize((w,h),Image.Resampling.LANCZOS)
        result.paste(im,(i*w,31),im)
        d.text((i*w+7,8),label,font=FONT,fill='white')
    result.save(path,optimize=True)


def frozen_lineup():
    frame=read(DOC/'side-target.json')
    board=frame['baseline_board_records']
    reference_height=board['king']['height_in_board_pixels']
    display_scale=328/reference_height
    canvas=Image.new('RGB',(824,399),BG)
    draw=ImageDraw.Draw(canvas)
    floor=347
    draw.line((8,floor,816,floor),fill='#52604e')
    for i,(name,key) in enumerate([('King','king'),('Queen','queen'),('Bishop 025','bishop'),('Bishop 026','bishop')]):
        row=board[key]
        if key!='bishop':
            p=row['archived_side_profile']
            cached=BUILD/'183-ruler'/(key+'.png')
            raw=cached.read_bytes() if cached.exists() else subprocess.check_output(
                ['git','-C',str(ROOT),'show',frame['board_page_at_screenshot']+':'+p['file']])
            assert hashlib.sha256(raw).hexdigest()[:16]==p['version']
            source=Image.open(io.BytesIO(raw)).convert('RGBA')
            step=display_scale*row['height_in_board_pixels']/(p['bottom']-p['top']+1)
            center=p['center']+.5
            bottom=p['bottom']+1
            percent=row['height_in_board_pixels']/reference_height*100
        else:
            which=ARCHIVE if i==2 else ASSETS
            source=Image.open(which/'side-profile.png').convert('RGBA')
            # Both bishops are drawn from the same zero-degree camera,
            # 1000/4.98 pixels per model unit, at z=2.32 with zero shift.
            camera=read(ASSETS/'diagnostic-cameras.json')['side-profile']
            ppunit=camera['height']/camera['orthoScale']
            assert camera['elevationDegrees']==0 and camera['orthoScale']==4.98
            step=display_scale*row['frozen_board_pixels_per_native_unit']/ppunit
            center=source.width/2
            bottom=source.height/2+ppunit*2.32
            height=read(which/'mesh.json')['bounds']['size'][2]
            percent=height*row['frozen_board_pixels_per_native_unit']/reference_height*100
        x=i*206+103
        piece=source.transform((206,350),Image.Transform.AFFINE,
            (1/step,0,center-103/step,0,1/step,bottom-floor/step),Image.Resampling.BICUBIC)
        canvas.paste(piece,(i*206,0),piece)
        draw.text((x,359),name,anchor='mt',font=FONT,fill='white')
        draw.text((x,380),f'{percent:.1f}% of king',anchor='mt',font=FONT,fill='#e3c295')
    canvas.save(DOC/'frozen-lineup.png',optimize=True)


def evaluate(keys,selected=None):
    assert keys[0]=='025'
    ref=Image.open(DOC/'owner-side-crop.png')
    frame=read(DOC/'side-target.json')
    assert hashlib.sha256((DOC/'owner-side-crop.png').read_bytes()).hexdigest()==frame['crop_sha256']
    target=screenshot_mask(ref,11)
    source=sprite()
    detail=Image.open(ASSETS/'reference.png').convert('RGBA')
    measures={}
    side=[]
    fixed=[]
    neutral=[]
    labels=[]
    for key in keys:
        out=BUILD/('side-refit-'+key)
        prior=key=='025'
        saved=ARCHIVE if prior else out
        model_file=saved/('bishop-rebuilt.blend' if prior else 'bishop.blend')
        wood=saved/('render.png' if prior else 'wood.png')
        clay=saved/('render-clay.png' if prior else 'neutral.png')
        if prior:
            original=read(ROOT/'docs/bishop-mission/iteration-025/comparison/metrics.json')
        else:
            path=out/'registered/metrics.json'
            if not path.exists() or read(path)['render_sha256']!=hashlib.sha256(wood.read_bytes()).hexdigest():
                subprocess.run([sys.executable,str(ROOT/'scripts/bishop/mission_compare.py'),'--render',str(wood.relative_to(ROOT)),
                                '--out',str(path.parent.relative_to(ROOT))],check=True,stdout=subprocess.DEVNULL)
            original=read(path)
        item=read(out/'measures.json')
        assert item['source_sha256']==hashlib.sha256(model_file.read_bytes()).hexdigest()
        side_im=level(out,ref,frame)
        mask=envelope(np.array(side_im)[:,:,3]>127)
        side_fit=compare_edges(target,mask)
        side_fit['threshold_iou_range']=[compare_edges(screenshot_mask(ref,n),mask)['outline_iou'] for n in [5,25]]
        item.update(side_fit=side_fit,registered={name:score['silhouette_iou'] for name,score in original['images'].items()})
        pixels=np.array(Image.open(clay).convert('RGBA'))[:,:,3]
        ys,xs=np.where(pixels>127)
        item['render_xyxy']=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]
        measures[key]=item
        back=Image.new('RGBA',ref.size,BG)
        back.alpha_composite(side_im)
        side.append(plot_edges(back,target,[255,183,88]))
        fixed.append(Image.open(wood).convert('RGBA'))
        neutral.append(Image.open(clay).convert('RGBA'))
        labels.append('Bishop 025' if prior else key.capitalize())
    actual=selected or keys[-1]
    y,x=np.where((np.asarray(source)[:,:,3]>127)&(np.max(np.asarray(source)[:,:,:3],2)>12))
    measures['original_registered_box']=[int(x.min()),int(y.min()),int(x.max()),int(y.max())]
    measures['side_calibration']=frame
    (DOC/'measurements.json').write_text(json.dumps(measures,indent=2)+'\n')
    panel([ref]+side,['Your lineup']+labels,DOC/'side-trials.png',(160,310))
    if selected:
        idx=keys.index(selected)
        panel([ref,side[0],side[idx]],['Your lineup','Bishop 025','Bishop 026'],DOC/'side-comparison.png',(187,363))
        box=(174,125,811,1142)
        im=[v.crop(box) for v in [source,detail,fixed[0],fixed[idx],neutral[idx]]]
        panel(im,['Lichess original','White candidate 3','Bishop 025','Bishop 026','Bishop 026 · clay'],DOC/'fixed-comparison.png',(190,303))
        for key in keys:
            print(key,measures[key]['side_fit'],measures[key]['registered'])
    else:
        for key in keys:
            x=measures[key];print(key,'side',round(x['side_fit']['outline_iou']*100,2), 'mae',round(x['side_fit']['edge_mae_screenshot_px'],2),'original',round(x['registered']['original_white']*100,2),x['front_collar_rim_rows'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('keys',nargs='+')
    p.add_argument('--accepted')
    p.add_argument('--lineup',action='store_true')
    args=p.parse_args()
    evaluate(args.keys,args.accepted)
    if args.lineup:
        frozen_lineup()

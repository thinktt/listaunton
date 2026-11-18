"""Compare saved candidate renders on a single floor, scale and registration."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'build/bishop-mission'
HISTORY=ROOT/'history/bishop-mission-024'
DOC=ROOT/'docs/bishop-mission/iteration-025'
ASSET=ROOT/'assets/bishop'
NAMES={'bishop':'Bishop 024','king':'King 017','queen':'Queen 033','wide':'Wider base',
       'short':'Wider + shorter','moderate':'Moderate shortening','refit':'Upper refit','registered':'Bishop 025'}
CASES=['bishop','wide','short','moderate','refit','registered']
INK='#ece8df'
FIELD='#1b1f23'
try:
    FONT=ImageFont.truetype('DejaVuSans.ttf',17)
except OSError:
    FONT=ImageFont.load_default(size=17)


def load(path):
    return Image.open(path).convert('RGBA')


def sprite():
    a=json.loads((ASSET/'original-alignment.json').read_text())
    s=a['scale']*300/1254
    return load(ASSET/'original.png').transform((1254,1254),Image.Transform.AFFINE,
            (s,0,3*a['x'],0,s,3*a['y']),Image.Resampling.BILINEAR)


def native(label,neutral=False):
    return load((HISTORY/('render-clay.png' if neutral else 'render.png')) if label=='bishop'
                else BUILD/('turning-'+label)/('neutral.png' if neutral else 'wood.png'))


def panel(items,size,labels,path):
    w,h=size
    im=Image.new('RGB',(w*len(items),h+42),FIELD)
    d=ImageDraw.Draw(im)
    for j,(label,art) in enumerate(zip(labels,items)):
        im.paste(art,(j*w,42),art)
        d.text((j*w+8,11),label,font=FONT,fill=INK)
    im.save(path)


def fixed_sheet(out,accepted):
    source=sprite()
    selected=load(ASSET/'reference.png')
    keys=['bishop','wide','short',accepted]
    images=[source,selected]+[native(k) for k in keys]
    labels=['Lichess original','White candidate 3']+[NAMES[k] for k in keys]
    rect=(190,127,793,1138)
    thumb=lambda im: im.crop(rect).resize((208,349),Image.Resampling.LANCZOS)
    panel([thumb(im) for im in images],(208,349),labels,out/'fixed-comparison.png')
    panel([thumb(im) for im in [source]+[native(k,True) for k in keys]],(208,349),
        [labels[0]]+[NAMES[k] for k in keys],out/'neutral-comparison.png')
    for fname,box in [('button-comparison.png',(318,141,668,455)),('head-comparison.png',(306,141,676,579))]:
        size=(430,round(430*(box[3]-box[1])/(box[2]-box[0])))
        parts=[im.crop(box).resize(size,Image.Resampling.LANCZOS) for im in
               [source,selected,native('bishop',True),native(accepted,True)]]
        panel(parts,size,['Lichess original','White candidate 3','Bishop 024 · neutral','Bishop 025 · neutral'],out/fname)
    source_mask=mask(source,True)
    target=load(ASSET/'reference.png')
    detail=[]
    for k in keys:
        neutral=native(k,True)
        m=mask(neutral)
        margin=Image.fromarray((m*255).astype('uint8'))
        rim=np.array(margin)!=np.array(margin.filter(ImageFilter.MinFilter(5)))
        ss=Image.fromarray((source_mask*255).astype('uint8'))
        source_rim=np.array(ss)!=np.array(ss.filter(ImageFilter.MinFilter(5)))
        img=np.array(target)
        img[:,:,:3]=(img[:,:,:3]*.60).astype(np.uint8)
        img[source_rim]=[255,199,78,255]
        img[rim]=[113,212,245,255]
        detail.append(Image.fromarray(img).crop((185,608,800,1130)).resize((283,240),Image.Resampling.LANCZOS))
    panel(detail,(283,240),[NAMES[k] for k in keys],out/'base-contours.png')


def mask(image,source=False):
    ar=np.array(image)
    return (ar[:,:,3]>127)&((ar[:,:,:3].max(2)>12) if source else True)


def side_image(key,width,height,zoom,center_z):
    folder=BUILD/'turning-sections'/key
    info=json.loads((folder/'measures.json').read_text())
    img=load(folder/'level.png')
    side=info['side']
    # zoom is desired displayed px per native unit. x=0 centers every piece.
    native_scale=side['pixels_per_unit']
    ratio=native_scale/zoom
    crop_x=img.width/2-width*ratio/2
    crop_y=side['floor_row']-center_z*native_scale-height*ratio/2
    return img.transform((width,height),Image.Transform.AFFINE,(ratio,0,crop_x,0,ratio,crop_y),Image.Resampling.BICUBIC)


def compare_section(a,b,diameter):
    def sample(key):
        folder=BUILD/'turning-sections'/key
        size=json.loads((folder/'measures.json').read_text())['foot_diameter']/diameter
        points=np.load(folder/'meridian.npy') / size
        # Fixed scaled range through the top of the socket; separate from the
        # bishop stem, which has a different radius and height.
        return points[(points[:,1]>=.006)&(points[:,1]<=1.225)]
    def directed(x,y):
        seg=np.diff(y,axis=0)
        squared=(seg*seg).sum(axis=1)
        assert squared.min()>0
        worst=0.
        for batch in np.array_split(x,48):
            delta=batch[:,None,:]-y[None,:-1,:]
            t=np.clip(np.einsum('ijk,jk->ij',delta,seg)/squared,0,1)
            distances=((delta-t[:,:,None]*seg)**2).sum(axis=2)
            worst=max(worst,float(np.sqrt(distances.min(axis=1)).max()))
        return worst
    x,y=sample(a),sample(b)
    return max(directed(x,y),directed(y,x))


def complete(out,accepted):
    far=BUILD/'turning-sections'
    measured={k:json.loads((far/k/'measures.json').read_text()) for k in ['queen','king']+CASES}
    source=sprite()
    white=mask(source,True)
    fy=measured['bishop']['side']
    assert fy['elevation_degrees']==0
    shared=['queen','king','bishop',accepted]
    feet=[]
    for k in shared:
        zoom=220/measured[k]['foot_diameter']
        feet.append(side_image(k,250,180,zoom,80/zoom))
    panel(feet,(250,180),[NAMES[k] for k in shared],out/'equal-foot-bases.png')
    panel([side_image(k,210,440,90,2.25) for k in CASES],(210,440),[NAMES[k] for k in CASES],out/'level-trials.png')
    ybands={'button':(162,213),'mitre':(215,400),'collars':(402,592),'exposed_stem':(594,616),
            'rear_flare':(630,790),'foot':(810,1060)}
    for k in CASES:
        m=mask(native(k))
        mm=measured[k]
        mm['width_change_pct']=(mm['foot_diameter']/measured['bishop']['foot_diameter']-1)*100
        mm['height_change_pct']=(mm['height']/measured['bishop']['height']-1)*100
        mm['reference_errors_fixed_px']={}
        for band,(lo,hi) in ybands.items():
            dif=[]
            for row in range(lo,hi):
                a,b=np.where(m[row])[0],np.where(white[row])[0]
                if len(a) and len(b):
                    dif.extend([abs(int(a[0])-int(b[0])),abs(int(a[-1])-int(b[-1]))])
            mm['reference_errors_fixed_px'][band]=round(float(np.mean(dif)),3)
        metrics=(ROOT/'docs/bishop-mission/iteration-024/comparison/metrics.json' if k=='bishop' else
                 BUILD/('turning-'+k)/'registered/metrics.json')
        mm['iou']={name:v['silhouette_iou'] for name,v in json.loads(metrics.read_text())['images'].items()}
        mm['equal_foot_meridian_distance_to_queen']=compare_section('queen',k,measured['queen']['foot_diameter'])
    measured['king']['equal_foot_meridian_distance_to_queen']=compare_section('queen','king',measured['queen']['foot_diameter'])
    # The center groove is a visible trough in both white references. It is
    # a comparison landmark, not a direct measurement of the tool-cut radius.
    for label,img in [('white',source),('white3',load(ASSET/'reference.png'))]:
        intensity=np.array(img.convert('L').filter(ImageFilter.GaussianBlur(2)))[:,488:497].mean(axis=1)
        measured[label+'_front_dark_groove_row']=int(1020+intensity[1020:1080].argmin())
    measured['equal_foot_scale']='Each model uniformly enlarged to 220 displayed pixels across its evaluated foot. Common sole; neutral level render.'
    measured['normalized_meridian_distance']='Symmetric maximum point-to-polyline distance over queen-equivalent heights .006 through 1.225, using samples every .0005 native units.'
    (out/'measurements.json').write_text(json.dumps(measured,indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixed-only',action='store_true')
    parser.add_argument('--out',type=Path,default=DOC)
    a=parser.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    accepted=json.loads((DOC/'turning.json').read_text())['accepted']
    fixed_sheet(a.out,accepted)
    if not a.fixed_only:
        complete(a.out,accepted)

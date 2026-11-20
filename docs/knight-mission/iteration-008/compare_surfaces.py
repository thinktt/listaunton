"""Compare registered renders with the unchanged source images at their common scale."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REGIONS = {'whole':(175,265,805,1080), 'mane and eyes':(215,289,566,500),
    'neck':(290,540,710,775), 'seat and platform':(265,780,710,875),
    'turned base':(275,893,713,998)}
LUMA = np.array([.2126,.7152,.0722])
def sha(file): return hashlib.sha256(file.read_bytes()).hexdigest()
def cropdiff(ref, image, mask, box, high=True):
    x,y,r,b=box
    keep=mask[y:b,x:r]
    rgb=np.asarray(image.convert('RGB'), dtype=float)[y:b,x:r]
    target=np.asarray(ref.convert('RGB'), dtype=float)[y:b,x:r]
    a,b=rgb[keep],target[keep]
    result={'pixels':int(len(a)), 'rgb_mae':round(float(np.abs(a-b).mean()),3),
            'mean_rgb_error':(a-b).mean(0).round(2).tolist(),
            'luma_percentiles':np.percentile(a@LUMA,[10,50,90,98]).round(2).tolist(),
            'target_luma_percentiles':np.percentile(b@LUMA,[10,50,90,98]).round(2).tolist()}
    if high:
        residual=[]
        for source in [image,ref]:
            detail=np.asarray(source.convert('L'),dtype=float)-np.asarray(source.convert('L').filter(ImageFilter.GaussianBlur(2)),dtype=float)
            residual.append(float(np.median(np.abs(detail[y:y+keep.shape[0],x:r][keep]))))
        result['median_2px_detail_render_target']=np.round(residual,2).tolist()
    return result

def sheet(out,images,box,width):
    x,y,r,b=box;h=round(width*(b-y)/(r-x))
    sheet=Image.new('RGB',(width*len(images),h+29),'#222522');draw=ImageDraw.Draw(sheet)
    font=ImageFont.load_default(size=14)
    for n,(name,im) in enumerate(images.items()):
        draw.text((n*width+7,6),name,font=font,fill='#e7e5dc')
        crop=im.crop(box).resize((width-2,h),Image.Resampling.LANCZOS)
        sheet.paste(crop,(n*width,28))
    sheet.save(out)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('out',type=Path)
    p.add_argument('trials',nargs='*',type=Path)
    args=p.parse_args();root=args.root.resolve();assets=root/'assets/knight'
    out=args.out;out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(root/'scripts/knight'))
    from audit_mission import registered, black, silhouette, iou
    refs=registered()
    fixed={'Parent':assets/'render.png'};side={'Parent':assets/'guide-render.png'}
    for folder in args.trials:
        fixed[folder.name]=folder/'wood.png';side[folder.name]=folder/'wood-side.png'
    size=refs['selected'].size
    def load(f):
        im=Image.open(f).convert('RGBA')
        if im.size!=size:im=im.resize(size,Image.Resampling.LANCZOS)
        return im
    raw={name:load(file) for name,file in fixed.items()}
    original,selected=black(refs['original']),black(refs['selected'])
    colors={'Lichess original':original,'Black candidate 2':selected,**{k:black(im) for k,im in raw.items()}}
    others={k:black(load(file)) for k,file in side.items()}
    masks={name:silhouette(im,True) for name,im in refs.items()}
    common=masks['selected'] & np.logical_and.reduce([silhouette(im) for im in raw.values()])
    common=np.asarray(Image.fromarray((common*255).astype('uint8')).filter(ImageFilter.MinFilter(5)))>0
    result={'registration':'Fixed 54-degree camera; source transformations from audit_mission.registered.',
            'reference_sha256':{n:sha(assets/n) for n in ['original.png','white-original.png','ref.png']},'models':{}}
    for name,path in fixed.items():
        mask=silhouette(raw[name])
        result['models'][name]={'image_sha256':sha(path),'image_size':Image.open(path).size,
            'iou':{key:round(iou(mask,src),7) for key,src in masks.items()},
            'regions':{k:cropdiff(selected,colors[name],common,box) for k,box in REGIONS.items()}}
    sheet(out/'fixed.png',colors,(165,270,800,1080),225)
    sheet(out/'platform.png',colors,(216,711,747,910),270)
    sheet(out/'neck.png',colors,(214,430,742,847),270)
    sheet(out/'mane.png',colors,(190,280,545,481),270)
    sheet(out/'side.png',others,(228,94,1010,1138),235)
    sheet(out/'side-platform.png',others,(295,680,973,966),290)
    (out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({n:{'iou':v['iou'],'region_mae':{k:t['rgb_mae'] for k,t in v['regions'].items()}} for n,v in result['models'].items()}))
if __name__=='__main__':main()

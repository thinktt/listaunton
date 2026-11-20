from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent
def go():
    tiles=np.load(D/'atlas-parts.npz');src=Image.open(D/'pigment.png').convert('RGB');W,H=src.size
    box=(int(.568*W),int((1-.282)*H),int(.639*W),int((1-.228)*H))
    px=np.array(src.crop(box));masks={};h,w=px.shape[:2]
    for k in tiles.files:
        if not k.endswith('_UV'):continue
        xy=tiles[k]*[W,-H]+[-box[0],H-box[1]]
        hit=(xy[:,:,0].max(1)>=0)&(xy[:,:,0].min(1)<=w)&(xy[:,:,1].max(1)>=0)&(xy[:,:,1].min(1)<=h)
        mask=Image.new('1',(w,h));pen=ImageDraw.Draw(mask)
        for t in xy[hit]:pen.polygon(list(map(tuple,t)),fill=1)
        masks[k]=np.asarray(mask)
    eye=masks['near_eye_UV']|masks['far_eye_UV'];others=np.logical_or.reduce([m for k,m in masks.items() if 'eye_UV' not in k])
    for k,m in masks.items():print(k,int(m.sum()),'shared',int((eye&m).sum()))
    overlay=px.copy();overlay[eye]=.5*overlay[eye]+[30,77,90];overlay[eye&others]=[216,56,89]
    out=Image.new('RGB',(w*2,h));out.paste(Image.fromarray(px),(0,0));out.paste(Image.fromarray(overlay),(w,0))
    out.resize((w*3,round(h*1.5)),Image.Resampling.NEAREST).save(D/'eye-atlas.png')
    (D/'eye-atlas.json').write_text(json.dumps({'crop':box,'eye_pixels':int(eye.sum()),'used_by_other_geometries':int((eye&others).sum()),
        'color_median':np.median(px[eye],axis=0).tolist(),'color_std':px[eye].std(0).tolist()}))
if __name__=='__main__':go()

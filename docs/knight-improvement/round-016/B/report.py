"""Assemble matched source, game, orbit, common-light and native verification plates."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from reference_images import registered,black
from study import metrics,BOX
F=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16);TITLE=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
BG='#252927';INK='#eeeae3';R=Image.Resampling.LANCZOS
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def im(n):return black(Image.open(D/n).convert('RGBA'))
def txt(c,xy,s,large=False):ImageDraw.Draw(c).text(xy,s,fill=INK,font=TITLE if large else F)
def paste(c,im,x,y,w,h):
    s=ImageOps.contain(im,(w,h),R);c.paste(s,(x+(w-s.width)//2,y+(h-s.height)//2))
def view_plate():
    refs=registered();objs={'Original':black(refs['original']),'Black 2':black(refs['selected']),'15A parent':im('parent-wood.png'),'16B':im('wood.png')}
    c=Image.new('RGB',(1120,715),BG);txt(c,(8,6),'The carved mane in the 54° gallery view',True)
    for i,(key,image) in enumerate(objs.items()):
        x=i*280;txt(c,(x+7,42),key);paste(c,image.crop((150,270,790,1070)),x,70,280,350)
        paste(c,image.crop(BOX),x,437,280,149);paste(c,image.crop((143,268,943,1068)),x+100,600,80,80)
    txt(c,(8,685),'80 px board crop below the full piece and the registered crest detail.');c.save(D/'fixed-and-board.png')
def orbit_plate():
    c=Image.new('RGB',(1160,701),BG);txt(c,(9,7),'Walnut and neutral clay from the frozen scene',True)
    for i,t in enumerate([('Near','near',0),('Front','front',4),('Far','opposite',8),('Rear quarter','rear-quarter',10),('Back','rear',12)]):
        title,key,j=t;x=232*i;txt(c,(x+7,49),title)
        for row,file in enumerate([f'wood-{key}.png',f'clay-{j:02d}.png']):paste(c,im(file),x,79+row*230,225,225)
    txt(c,(10,569),'Registered 7° profile, parent and 16B at game scale')
    for j,file in enumerate(['parent-side.png','wood-side.png']):
        a=Image.open(D/file).convert('RGBA');box=a.getbbox();paste(c,black(a.crop(box)),20+126*j,596,92,92)
    c.save(D/'orbit-proof.png')
    frames=[im(f'clay-{i:02d}.png').resize((384,384),R) for i in range(16)]
    frames[0].save(D/'clay-turn.webp',save_all=True,append_images=frames[1:],duration=170,loop=0,quality=86)
def light_plate(side):
    c=Image.new('RGB',(1180,870),BG);txt(c,(7,5),'One moving softbox across the '+side+' flank',True)
    for i,s in enumerate(['Behind','Overhead','Noseward']):txt(c,(82+i*365,46),s)
    for j,(key,finish) in enumerate([('parent','walnut'),('knight','walnut'),('parent','clay'),('knight','clay')]):
        y=71+j*198;txt(c,(4,y+38),'15A' if key=='parent' else '16B');txt(c,(4,y+61),finish)
        for i in range(3):paste(c,im(f'turn-{key}-{side}-{finish}-{i}.png'),74+i*367,y,359,193)
    c.save(D/f'moving-{side}.png')
def extent():
    results={}
    for mode,files,rect in [('fixed',['parent-wood.png','wood.png'],BOX),('side',['parent-side.png','wood-side.png'],None)]:
        a,b=(np.asarray(Image.open(D/name).convert('RGBA')) for name in files);am=a[:,:,3]>127;bm=b[:,:,3]>127
        diff=abs(a[:,:,:3].astype(float)-b[:,:,:3].astype(float));lum=diff@[.2126,.7152,.0722]
        row={'silhouette_iou':float((am&bm).sum()/(am|bm).sum()),'changed_silhouette_pixels':int(np.sum(am!=bm))}
        if rect:
            keep=(am&bm).copy();x,y,r,s=rect;keep[y:s,x:r]=False
            for reg,mask in [('piece_outside_crest_crop',keep),('head_eye',np.s_[450:530,452:577])]:
                v=lum[mask];row[reg]={'absolute_luma_change_mean':float(v.mean()),'absolute_luma_change_p95':float(np.percentile(v,95))}
        results[mode]=row
    return results
def control_plate():
    base=im('wood.png').crop(BOX);pairs={'Saved studio':base}
    for name in ['oval','forward','upper']:pairs['Without '+name]=im(f'without-{name}-knight.png')
    c=Image.new('RGB',(4*274,180),BG);data={}
    for i,(name,a) in enumerate(pairs.items()):
        x=274*i;txt(c,(x+5,4),name);paste(c,a,x,31,270,142);data[name]=metrics(a)
    c.save(D/'controlled-light.png');return data
def main():
    view_plate()
    if '--early' in sys.argv:
        (D/'extent.json').write_text(json.dumps(extent(),indent=2)+'\n');return
    orbit_plate();light_plate('near');light_plate('far')
    ext=extent();c=control_plate();(D/'extent.json').write_text(json.dumps(ext,indent=2)+'\n')
    hashes={};names=['knight.blend','wood.png','wood-side.png','parent.blend','parent-wood.png','parent-side.png','pigment.png','parent-pigment.png',
        'crest-comparison.json','crest-comparison.png','verified.json','replay.json','extent.json','pigment-proof.json','parameters.json','geometry-parent.json','top-sections.png',
        'fixed-and-board.png','orbit-proof.png','moving-near.png','moving-far.png','controlled-light.png','clay-turn.webp','clay-side.png','clay-fixed.png',
        'webgl/native-qa.json','review-copy/assets/knight/validation.json','review-copy/assets/knight/mesh.json','review-copy/assets/knight/mesh.bin',
        'review-copy/assets/knight/varnish.bin','review-copy/assets/knight/camera.json','crest-parent.json','crest-B.json','support.json','package-proof.json','REPORT.md']
    for index in ['turn-parent.json','turn-knight.json','controls-knight.json']:
        recorded=json.loads((D/index).read_text());names.append(index)
        for key,digest in recorded.items():
            f=f'without-{key}-knight.png' if index=='controls-knight.json' else key
            assert sha(D/f)==digest;names.append(f)
    names+=['wood-'+k+'.png' for k in ['near','front','opposite','rear-quarter','rear']]+[f'clay-{i:02d}.png' for i in range(16)]
    hashes={n:sha(D/n) for n in sorted(set(names))}
    (D/'proof.json').write_text(json.dumps({'model_sha256':hashes['knight.blend'],'masks':ext,'physical_lamp_control':c,'sha256':hashes},indent=2)+'\n')
if __name__=='__main__':main()

"""Build the comparison plates and check the signed delivery in this folder."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from reference_images import registered,black
R=Image.Resampling.LANCZOS;B='#222825';T='#ebece6'
F=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16);H=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
def read(f):return Image.open(D/f).convert('RGBA')
def panel(c,p,rect):
    x,y,w,h=rect;q=ImageOps.contain(black(p),(w,h),R);c.paste(q,(x+(w-q.width)//2,y+(h-q.height)//2))
def title(c,x,y,t,f=F):ImageDraw.Draw(c).text((x,y),t,font=f,fill=T)
def fixed():
    refs=registered();images=[('Original',refs['original']),('Black 2',refs['selected']),('13A parent',read('parent-wood.png')),('14B',read('wood.png'))]
    im=Image.new('RGB',(1040,790),B);title(im,9,5,'The registered 54° view',H)
    for j,(label,p) in enumerate(images):
        x=j*260;title(im,x+6,40,label)
        panel(im,p.crop((153,269,793,1069)),(x,66,258,321))
        panel(im,p.crop((178,431,326,651)),(x,402,258,239))
        panel(im,p.crop((143,268,943,1068)),(x+89,663,80,80))
    title(im,10,754,'The lower row uses the same 80 px board crop for all four images.');im.save(D/'fixed-and-board.png')
def rear():
    im=Image.new('RGB',(975,1170),B);title(im,10,5,'Walnut under matched light and as unlit pigment',H)
    for col,(view,label) in enumerate([('near-quarter','Near rear quarter'),('back','Rear'),('far-quarter','Far rear quarter')]):title(im,96+col*292,44,label)
    for row,(model,finish) in enumerate([('parent','walnut'),('knight','walnut'),('parent','pigment'),('knight','pigment')]):
        y=72+row*267;title(im,8,y+89,'13A' if model=='parent' else '14B');title(im,8,y+113,finish)
        folder=f'back-{model}'+('-pigment' if finish=='pigment' else '')
        manifest=json.loads((D/folder/'source.json').read_text())
        assert manifest['source_sha256']==sha(model+'.blend')
        for col,view in enumerate(['near-quarter','back','far-quarter']):
            file=f'{finish}-{view}.png';rel=folder+'/'+file
            assert manifest['views'][file]==sha(rel)
            panel(im,read(rel),(74+col*297,y,294,260))
    im.save(D/'rear-comparison.png')
def orbit():
    im=Image.new('RGB',(1165,548),B);title(im,9,5,'The restored billet from five sides',H)
    for j,(view,label,clay) in enumerate([('near','Near side',0),('front','Front',4),('opposite','Far side',8),('rear-quarter','Rear quarter',10),('rear','Rear',12)]):
        x=j*233;title(im,x+6,41,label);panel(im,read('wood-'+view+'.png'),(x,68,231,227));panel(im,read(f'clay-{clay:02d}.png'),(x,306,231,227))
    im.save(D/'orbit-proof.png')
    frames=[black(read(f'clay-{i:02d}.png')).resize((400,400),R) for i in range(16)]
    frames[0].save(D/'clay-turn.webp',save_all=True,append_images=frames[1:],duration=180,loop=0,quality=88)
def controls():
    im=Image.new('RGB',(994,496),B);title(im,8,5,'The same carving under the same studio lights',H)
    rows=[('13A','parent'),('14B','knight')]
    for j,label in enumerate(['Walnut','Pigment only','Neutral finish']):title(im,101+j*301,41,label)
    for i,(label,key) in enumerate(rows):
        y=70+200*i;title(im,8,y+81,label)
        files=['parent-wood.png' if i==0 else 'wood.png',f'trial-{key}-pigment.png',f'neutral-{key}.png']
        for j,f in enumerate(files):
            p=read(f);p=p.crop((175,374,436,716)) if p.width==1254 else p
            panel(im,p.crop((0,58,190,278)),(74+j*300,y,288,194))
    im.save(D/'material-controls.png')
    a=np.asarray(read('neutral-parent.png'),int);b=np.asarray(read('neutral-knight.png'),int)
    return {'neutral_mean_absolute_rgba_delta':float(abs(a-b).mean()),'neutral_max_rgba_delta':int(abs(a-b).max())}
def sha(f):return hashlib.sha256((D/f).read_bytes()).hexdigest()
def main():
    fixed();rear();orbit();m=controls()
    for mode,a,b in [('fixed','parent-wood.png','wood.png'),('side','parent-side.png','wood-side.png')]:
        x=np.asarray(read(a))[:,:,3]>127;y=np.asarray(read(b))[:,:,3]>127
        m[mode+'_silhouette_iou']=float((x&y).sum()/(x|y).sum());m[mode+'_changed_mask_pixels']=int((x^y).sum())
    files=['parent.blend','knight.blend','pigment.png','parent-pigment.png','parent-wood.png','parent-side.png','wood.png','wood-side.png',
        'registered-study.json','registered-study.png','fixed-and-board.png','orbit-proof.png','rear-comparison.png','material-controls.png','clay-turn.webp',
        'parameters.json','verified.json','restoration-9.json','arc-samples.json','hollow-samples.json','neutral-parent.png','neutral-knight.png',
        'map.py','surface.py','donor.py','donor_field.py','restore.py','candidate.py','study.py','verify.py','viewer.py','qa_geometry.py','rear.py',
        'report.py','support.py','support.json','evidence.py','diagnostics.py','reference_images.py','reproduce.ps1','REPORT.md','webgl/native-qa.json',
        'review-copy/assets/knight/viewer-validation.json','review-copy/assets/knight/validation.json','review-copy/assets/knight/mesh.bin',
        'review-copy/assets/knight/mesh.json','review-copy/assets/knight/varnish.bin','review-copy/assets/knight/camera.json',
        'review-copy/assets/knight/wood-atlas-improvement-014-B.png','webgl/fixed-orbit.png','webgl/side-orbit.png','webgl/side-clay.png','webgl/drag-orbit.png']
    for mode in ['wood','pigment']:
        files.extend(f'turn-knight-{mode}-{v}.png' for v in ['near','rear-near','rear','rear-far','far'])
    for folder in ['back-parent','back-knight','back-parent-pigment','back-knight-pigment']:
        files.extend(f.relative_to(D).as_posix() for f in (D/folder).glob('*') if f.is_file())
    files.extend(f'clay-{q:02d}.png' for q in range(16))
    files.extend(f'wood-{q}.png' for q in ['near','opposite','front','rear-quarter','rear'])
    result={f:sha(f) for f in sorted(set(files))}
    params=json.loads((D/'parameters.json').read_text())
    assert [result[n] for n in ['knight.blend','pigment.png','wood.png','wood-side.png']]==[params[k] for k in ['model_sha256','pigment_sha256','fixed_sha256','side_sha256']]
    m['sha256']=result;(D/'proof.json').write_text(json.dumps(m,indent=2)+'\n')
    print('Verified',len(result),'signed outputs and inputs',flush=True)
if __name__=='__main__':main()

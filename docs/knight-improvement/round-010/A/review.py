"""Register the silhouette, photograph the seam and compare the real crown sections."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageOps
D=Path(__file__).resolve().parent;ROOT=D.parents[2];A=ROOT/'assets/knight'
sys.dont_write_bytecode=True;sys.path.insert(0,str(ROOT/'scripts/knight'))
from audit_mission import iou,silhouette
def read(f):return Image.open(f).convert('RGBA')
def black(im):
    b=Image.new('RGBA',im.size,'black');b.alpha_composite(im);return b.convert('RGB')
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def info(n):return json.loads((D/n).read_text())
def panel(canvas,img,box,rect,label):
    if isinstance(img,Path):img=read(img)
    if box:img=img.crop(box)
    x,y,w,h=rect;im=black(img);im.thumbnail((w-5,h-21),Image.Resampling.LANCZOS)
    # For feature inspection the native frame and all four comparison crops
    # are enlarged by the same factor, regardless of their own image size.
    if box:
        scale=min((w-5)/img.width,(h-21)/img.height)
        im=black(img).resize((max(1,int(img.width*scale)),max(1,int(img.height*scale))),Image.Resampling.BICUBIC)
    canvas.paste(im,(x+(w-im.width)//2,y+19+(h-20-im.height)//2))
    ImageDraw.Draw(canvas).text((x+4,y+1),label,fill='#edeae2')
def sections():
    frame=Image.new('RGB',(1140,430),'#252829');d=ImageDraw.Draw(frame)
    for idx,k in enumerate(['-0.8','-0.6','-0.4','-0.2','0','0.14']):
        row,col=divmod(idx,3);xc=col*380+187;yt=row*202+38
        parts={t:info('crest-'+t+'.json')['profiles'][k] for t in ['parent','A']}
        zmax=max(v['surfaces']['mane'] for v in parts['A'] if 'mane' in v['surfaces'])
        for label,colour in [('parent','#daab74'),('A','#64cfcc')]:
            p=parts[label];coords=[(xc+v['y']*568,yt+(zmax-v['surfaces']['mane'])*599) for v in p if 'mane' in v['surfaces']]
            d.line(coords,fill=colour,width=2 if label=='parent' else 1)
        d.text((col*380+7,row*202+2),'Longitudinal station '+k,fill='white')
    d.text((9,408),'Tan = 9A parent     Teal = 10A     Both axes use scene units.',fill='white')
    frame.save(D/'sections.png')
def main():
    cfg=info('parameters.json');sha=cfg['model_sha256'];assert h(D/'knight.blend')==sha
    for k,v in [('parent',cfg['parent_sha256']),('A',sha)]:
        assert info('clay-'+k+'/scene.json')['model']==v==info('wood-'+k+'/source.json')['source_sha256']
    ref=read(A/'ref.png');old=read(D/'parent-wood.png');new=read(D/'wood.png')
    orig=read(A/'original.png');ac=info('../../../assets/knight/original-alignment.json')
    sc=ac['scale']*300/1254
    original=orig.transform(ref.size,Image.Transform.AFFINE,(sc,0,ac['x']*3,0,sc,ac['y']*3),Image.Resampling.BILINEAR)
    views={'Original black':original,'Black 2':ref,'9A parent':old,'10A':new}
    cmp=Image.new('RGB',(1320,769),'#252728')
    for i,(name,im) in enumerate(views.items()):
        panel(cmp,im,(226,274,539,425),(i*330,0,330,185),name+' / upper carving')
        panel(cmp,im,(385,343,492,404),(i*330,188,330,185),'Forehead and ear root')
        panel(cmp,im,(157,252,793,1081),(i*330,377,330,274),'Full silhouette')
        small=black(im).resize((100,100),Image.Resampling.LANCZOS);cmp.paste(small,(i*330+113,665))
    cmp.save(D/'crown-comparison.png')
    features=Image.new('RGB',(1200,853),'#242627')
    for i,(tag,cap) in enumerate([('parent','9A parent'),('A','10A')]):
        off=i*600;c=D/('clay-'+tag);wood=old if i==0 else new;side=D/('parent-wood-side.png' if i==0 else 'wood-side.png')
        for j,(file,box,title) in enumerate([(wood,(240,273,522,421),'54 degree walnut'),(side,(330,97,733,349),'Side walnut'),
            (c/'fixed.png',(184,212,401,327),'54 degree clay'),(c/'side.png',(254,74,563,266),'Side clay'),
            (c/'front-poll.png',None,'Front clay'),(c/'back-poll.png',None,'Rear clay')]):
            rr,cc=divmod(j,2);panel(features,file,box,(off+cc*300,rr*282,300,280),cap+' / '+title)
    features.save(D/'matched-features.png')
    diag=Image.new('RGB',(1220,740),'#242627')
    for i,(f,b,label) in enumerate([(D/'wood.png',(160,260,797,1079),'54 degree walnut'),(D/'wood-side.png',(265,69,986,1145),'Registered side'),
        (D/'wood-front.png',(35,8,453,463),'Front'),(D/'wood-rear.png',(38,10,450,463),'Rear'),
        (D/'wood-A/near.png',(93,58,573,565),'Evenly lit near flank'),(D/'wood-A/far.png',(66,58,547,565),'Evenly lit far flank'),
        (D/'clay-A/rear-quarter.png',(166,12,816,866),'Rear quarter clay'),(D/'clay-A/far-side.png',(137,20,835,876),'Opposite clay')]):
        rr,cc=divmod(i,4);panel(diag,f,b,(cc*305,rr*370,305,367),label)
    diag.save(D/'diagnostics.png')
    turns=[black(read(p)) for p in sorted((D/'clay-turn').glob('*.png'))]
    turns[0].save(D/'clay-turn.webp',save_all=True,append_images=turns[1:],duration=240,loop=0,quality=87,method=2)
    sections()
    regions={'upper_ear_flash':(333,302,355,310),'eye':(475,463,542,496),'cheek':(455,500,525,535),'chest':(317,570,387,605)}
    metrics={}
    for key,im in views.items():
        l=np.asarray(black(im),dtype=float);metrics[key]={}
        for name,(x,y,u,v) in regions.items():
            rgb=l[y:v,x:u];luma=rgb@[.2126,.7152,.0722];metrics[key][name]={'median_rgb':np.median(rgb,axis=(0,1)).tolist(),'p90_luma':round(float(np.percentile(luma,90)),3),'p98_luma':round(float(np.percentile(luma,98)),3)}
    masks={name:silhouette(im,name in ['Original black','Black 2']) for name,im in views.items()}
    outlines={name:{label:iou(masks[name],masks[label]) for label in ['9A parent','10A']} for name in ['Original black','Black 2']}
    outlines['parent_overlap']={'fixed':iou(masks['9A parent'],masks['10A']),'side':iou(silhouette(read(D/'parent-wood-side.png')),silhouette(read(D/'wood-side.png')))}
    source=cfg['parent_sha256']
    details=info('validation.json');assert details['candidate']==sha
    audit=info('self-intersections.json');assert audit['candidate']['sha256']==sha
    out={'model_sha256':sha,'parent_sha256':source,'render_sha256':{n:h(D/n) for n in ['wood.png','wood-side.png']},
         'fixed_regions':regions,'regions_by_image':metrics,'outline':outlines,
         'crest_geometry':details['crown'],'ear_tip':{k:info('ear-'+k+'.json')['visible_ear_columns'][0] for k in ['parent','A']},
         'nonadjacent_self_intersections':{k:v['intersection_count'] for k,v in audit['candidate'].items() if k!='sha256'}}
    (D/'assessment-metrics.json').write_text(json.dumps(out,indent=2)+'\n');print('CHECKED',outlines)
if __name__=='__main__':main()

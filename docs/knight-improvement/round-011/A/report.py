"""Compare the frozen eye at source registration, in physical section and in native views."""
from pathlib import Path
import hashlib,json,sys
from PIL import Image,ImageDraw,ImageFilter,ImageOps
import numpy as np
D=Path(__file__).resolve().parent;R=D.parents[2];A=R/'assets/knight'
sys.dont_write_bytecode=True;sys.path.insert(0,str(R/'scripts/knight'))
from audit_mission import iou,silhouette
def read(p):return Image.open(p).convert('RGBA')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def data(n):return json.loads((D/n).read_bytes())
def black(im):
    dest=Image.new('RGBA',im.size,'black');dest.alpha_composite(im);return dest.convert('RGB')
def panel(sheet,im,box,loc,size,name):
    if isinstance(im,Path):im=read(im)
    if box is not None:im=im.crop(box)
    w,h=size;f=min((w-5)/im.width,(h-22)/im.height);thumb=black(im).resize((int(im.width*f),int(im.height*f)),Image.Resampling.LANCZOS)
    x,y=loc;sheet.paste(thumb,(x+(w-thumb.width)//2,y+20+(h-22-thumb.height)//2))
    ImageDraw.Draw(sheet).text((x+4,y+2),name,fill='#eeece7')
def side_geometry(label):
    a=np.load(D/('eyes-'+label+'.npz'));u=a['u'][a['near_insert']];v=a['v'][a['near_insert']]
    axis=np.array([1.,-.76])/np.hypot(1,.76);across=np.array([-axis[1],axis[0]])
    xz=u[:,None]*axis+v[:,None]*across
    _,_,m=np.linalg.svd(xz-xz.mean(0),full_matrices=False);main=m[0];main*=np.sign(main[0])
    return {'samples':len(xz),'inclination_down_from_head_horizontal_deg':float(np.degrees(np.arctan2(-main[1],main[0]))),
            'extent_along_and_across_principal_axes':np.ptp(xz@m.T,axis=0).tolist()}
def main():
    p=data('parameters.json');parent=p['parent_sha256'];model=p['model_sha256']
    assert sha(D/'knight.blend')==model==data('validation.json')['model']==data('eyes-A.json')['source_sha256']
    assert [sha(D/n) for n in ['wood.png','wood-side.png']]==[p['reopened_renders'][k+'_sha256'] for k in ['fixed','side']]
    for k,h in [('parent',parent),('A',model)]:
        for lab,field in [('portraits','model'),('turn-eye','model'),('clay','model'),('wood','source_sha256')]:
            doc='scene.json' if lab=='clay' else 'source.json';assert data(f'{lab}-{k}/'+doc)[field]==h
    ref=read(A/'ref.png');orig=read(A/'original.png');old=read(D/'parent-wood.png');new=read(D/'wood.png')
    al=json.loads((A/'original-alignment.json').read_text());scale=al['scale']*300/1254
    original=orig.transform(ref.size,Image.Transform.AFFINE,(scale,0,al['x']*3,0,scale,al['y']*3),Image.Resampling.BILINEAR)
    fixed={'Original black':original,'Black 2':ref,'10B parent':old,'11A in parent studio':read(D/'matched-parent-fixed.png'),'11A gallery':new}
    sheet=Image.new('RGB',(1500,730),'#262829')
    for i,(label,im) in enumerate(fixed.items()):
        x=i*300
        panel(sheet,im,(447,444,558,515),(x,0),(300,209),label+' / 54 degrees')
        panel(sheet,im,(314,378,633,575),(x,213),(300,193),'Head and cheek')
        # Source kept at true pixel size. The other four frames are registered
        # to its exact crop and then reduced to that same native size.
        nt=orig if i==0 else im.transform(orig.size,Image.Transform.AFFINE,(1/scale,0,-al['x']*3/scale,0,1/scale,-al['y']*3/scale),Image.Resampling.BICUBIC)
        ImageDraw.Draw(sheet).text((x+4,405),'Native 300 px frame',fill='white')
        sheet.paste(black(nt),(x,424))
    sheet.save(D/'source-comparison.png')
    sheet=Image.new('RGB',(1320,726),'#262828')
    for j,tag in enumerate(['parent','A']):
        ws=D/('parent-wood-side.png' if tag=='parent' else 'wood-side.png')
        camera=D/('clay-'+tag);pts=D/('portraits-'+tag)
        for i,(file,box,title) in enumerate([(camera/'fixed.png',(329,329,441,405),'54 degree clay'),
                (ws,(543,254,745,410),'Registered walnut side'),(pts/'clay-near.png',None,'Near clay'),
                (pts/'clay-far.png',None,'Far clay'),(pts/'walnut-near.png',None,'Near walnut'),(pts/'walnut-far.png',None,'Far walnut')]):
            x=(i%3)*220+j*660;y=(i//3)*213
            panel(sheet,file,box,(x,y),(220,208),('10B' if tag=='parent' else '11A')+' / '+title)
        for i,name in enumerate(['-30','0','30']):
            panel(sheet,D/('turn-eye-'+tag)/('clay-'+name+'.png'),None,(j*660+i*220,442),(220,239),'Clay / '+name+' degrees')
    sheet.save(D/'matched-carving.png')
    sheet=Image.new('RGB',(1200,695),'#242627')
    for i,(img,box,title) in enumerate([(new,(160,256,794,1066),'54 degree walnut'),(D/'wood-side.png',(257,69,998,1145),'Registered side'),
        (D/'wood-front.png',(43,2,445,473),'Front'),(D/'wood-rear.png',(37,3,455,474),'Rear'),
        (D/'wood-A/near.png',(122,82,535,451),'Equal-light near flank'),(D/'wood-A/far.png',(102,82,515,451),'Equal-light far flank'),
        (D/'clay-A/rear-quarter.png',(155,21,819,882),'Rear quarter clay'),(D/'clay-A/far-side.png',(128,22,833,884),'Far-side clay')]):
        panel(sheet,img,box,((i%4)*300,(i//4)*346),(300,343),title)
    sheet.save(D/'diagnostics.png')
    rois={'eye':(466,461,553,489),'lower_lid':(463,488,548,512),'cheek':(455,500,525,535),'chest':(317,570,387,605)}
    images={k:np.asarray(black(im),dtype=float) for k,im in fixed.items()}
    luma={k:np.asarray(black(im).filter(ImageFilter.GaussianBlur(1.2)),float)@[.2126,.7152,.0722] for k,im in fixed.items()}
    metrics={};trace={}
    for name,img in images.items():
        metrics[name]={}
        for key,(x,y,r,b) in rois.items():
            w=luma[name][y:b,x:r];tar=luma['Black 2'][y:b,x:r]
            metrics[name][key]={'median_rgb':np.median(img[y:b,x:r],axis=(0,1)).tolist(),'luminance_mae':float(abs(w-tar).mean()),
                'pattern_correlation':float(np.corrcoef(w.ravel(),tar.ravel())[0,1])}
        a=np.median(luma[name][454:511,496:505],axis=1)
        peaks=np.flatnonzero((a[1:-1]>a[:-2])&(a[1:-1]>=a[2:]))+1
        trace[name]={'central_peaks_y_luma':[[int(k+454),round(float(a[k]),2)] for k in peaks if 461<=k+454<=505],
            'brightest_lower_y':int(np.argmax(a[38:53])+492)}
    masks={k:silhouette(im,k in ['Original black','Black 2']) for k,im in fixed.items() if 'studio' not in k}
    overlaps={k:{n:iou(masks[k],masks[n]) for n in ['10B parent','11A gallery']} for k in ['Original black','Black 2']}
    overlaps['parent']={'fixed':iou(masks['10B parent'],masks['11A gallery']),'side':iou(silhouette(read(D/'parent-wood-side.png')),silhouette(read(D/'wood-side.png')))}
    r={'model':model,'parent':parent,'renders':{n:sha(D/n) for n in ['wood.png','wood-side.png']},'studio_control':data('matched-studio.json'),
       'fixed_source_comparison':metrics,'trace_x496_504':trace,'outline':overlaps,'bilateral_apertures':{k:side_geometry(k) for k in ['parent','A']},
       'fixed_visible_insert':{k:data('fixed-eye-'+k+'.json')['visible_pixels'] for k in ['parent','A']},
       'bilateral_iou':data('eyes-A.json')['exposed_insert_mirrored_iou'],
       'per_part_self_intersections':{k:v['intersection_count'] for k,v in data('self-intersections.json')['candidate'].items() if k!='sha256'},
       'skull_self_intersections':data('skull-intersections.json')['candidate']['continuous horse head and neck']['intersection_count']}
    (D/'assessment-metrics.json').write_text(json.dumps(r,indent=2)+'\n');print(r['outline'])
if __name__=='__main__':main()

"""Assemble comparisons and metrics from reopened native geometry and final 144-sample images."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D=Path(__file__).resolve().parent;R=D.parents[2];J=D.parent/'round-012-judge'
sys.path.insert(0,str(R/'scripts/knight'))
from audit_mission import registered,black,silhouette,iou
def read(p):return json.loads(Path(p).read_bytes())
def rgba(p):return Image.open(p).convert('RGBA')
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
def sheet(path,rows,cell,label=30):
    w,h=cell;im=Image.new('RGB',(len(rows[0])*w,len(rows)*(h+label)),'#171a19');pen=ImageDraw.Draw(im)
    for y,row in enumerate(rows):
        for x,(text,pic) in enumerate(row):
            xx=x*w;yy=y*(h+label);pen.text((xx+8,yy+4),text,fill='#eeece4',font=font)
            pic.thumbnail((w,h),Image.Resampling.LANCZOS)
            im.paste(pic,(xx+(w-pic.width)//2,yy+label+(h-pic.height)//2),pic if pic.mode=='RGBA' else None)
    im.save(path)
def main():
    par=read(D/'parameters.json');m=par['reopened_renders']
    for n,k in [('wood.png','fixed_sha256'),('wood-side.png','side_sha256')]:
        assert hashlib.sha256((D/n).read_bytes()).hexdigest()==m[k]
    refs=registered()
    ims={'Original':refs['original'],'Black 2':refs['selected'],'11B':rgba(D/'parent-wood.png'),'12A':rgba(D/'wood.png')}
    sheet(D/'comparison.png',[[(n,im.crop((145,245,803,1094))) for n,im in ims.items()]],(245,340))
    sheet(D/'board.png',[[(n,im.resize((100,100),Image.Resampling.LANCZOS)) for n,im in ims.items()]],(100,100))
    sheet(D/'source-study.png',[[(n,im.crop((173,416,375,675))) for n,im in ims.items()]],(224,285))
    rows=np.array([(y,x) for y,x,*_ in read(D/'mane-hollow.json')['Black 2']['samples'] if 470<=y<=625]);offset=np.arange(-25,64)
    scores={}
    for n,im in ims.items():
        a=np.asarray(black(im).filter(ImageFilter.GaussianBlur(2.5)),float)@[.2126,.7152,.0722]
        prof=np.median(a[rows[:,0,None],rows[:,1,None]+offset],axis=0)
        scores[n]=dict(zip(['mane','valley','neck','minimum','minimum_offset'],[round(float(j),2) for j in (np.median(prof[(offset>=-25)&(offset<=-14)]),np.median(prof[np.abs(offset)<=3]),np.median(prof[(offset>=20)&(offset<=39)]),prof.min(),offset[prof.argmin()])]))
    masks={n:silhouette(im,n in ['Black 2','Original']) for n,im in ims.items()}
    left={n:np.argmax(m[445:660],axis=1) for n,m in masks.items()}
    outline={'candidate_parent_iou':iou(masks['11B'],masks['12A']),
             'rows_445_659_mean_displacement':float(np.mean(left['12A']-left['11B'])),
             'rows_445_659_mean_absolute_displacement':float(np.mean(abs(left['12A']-left['11B']))),
             'rows_445_659_maximum_displacement':int(np.max(abs(left['12A']-left['11B']))),
             'source_iou':{k:{n:iou(masks[k],masks[n]) for n in ['11B','12A']} for k in ['Black 2','Original']}}
    geom={};pars={}
    for name,file in [('11B','parent-depth.json'),('12A','candidate-depth.json')]:
        depth=read(D/file)
        assert depth['source_sha256']==(par['model_sha256'] if name=='12A' else par['parent_sha256'])
        obs=[]
        for yy,s in depth['rows'].items():
            rays=s['rays'];cx=s['reference_shadow_x'];look={r[0]:r for r in rays}
            join=next(r[0] for r in rays[16:] if r[-1]=='continuous horse head and neck')
            deepest=max(look[x][1] for x in range(cx-16,cx+18))
            relief=deepest-(look[cx-20][1]+look[cx+20][1])/2
            obs.append({'y':int(yy),'source_x':cx,'first_neck_x':join,'error_px':join-cx,'relief':round(relief,4)})
        geom[name]={'rows':obs,'mean_absolute_contact_error_px':float(np.mean([abs(r['error_px']) for r in obs])),'median_native_depth_versus_40px_chord':float(np.median([r['relief'] for r in obs]))}
    checks=read(D/'protected.json')
    for key,where in [('parent',D/'mane-neck-depth.json'),('candidate',D/'candidate-seat/mane-neck-depth.json')]:
        dat=read(where)
        pars[key]={c['y']:sorted(c['samples']['source_shadow']['hits']) for c in dat['sections']}
    roi=np.array([(y,np.flatnonzero(masks['Black 2'][y])[0],x) for y,x in rows if 488<=y<=581])
    percent=np.arange(3,165,2);xx=np.rint(roi[:,1,None]+(roi[:,2]-roi[:,1])[:,None]*percent/100).astype(int)
    broad={}
    for n,im in ims.items():
        a=np.asarray(black(im).filter(ImageFilter.GaussianBlur(3)),float)@[.2126,.7152,.0722]
        prof=np.median(a[roi[:,0,None],xx],axis=0)
        broad[n]=[round(float(np.median(prof[(percent>=lo)&(percent<=hi)])),2) for lo,hi in [(21,39),(65,83)]]
    compact={'fixed_144_luminance':scores,'broad_rear_inner_face_luminance':broad,'registered_silhouette':outline,'octet_contact_profiles':geom,'source_column_hits':pars}
    (D/'assessment.json').write_text(json.dumps(compact,indent=2)+'\n')
    labels=['Near','Rear quarter','Rear','Opposite quarter','Far']
    paths=['near','near-quarter','back','far-quarter','far']
    sheet(D/'turns.png',[[(lab,rgba(D/f'turn-{path}.png')) for lab,path in zip(labels,paths)],[(lab,rgba(D/'clay-turn'/f'{k:02d}.png')) for lab,k in zip(labels,[0,10,12,14,8])]],(204,204))
    pp=read(D/'controls/wood/source.json');pc=read(D/'controls/clay/scene.json')
    assert pp['source_sha256']==par['parent_sha256'] and pc['model']==par['parent_sha256']
    if not (D/'paired/source.json').is_file():return
    assert read(D/'paired/source.json')['source_sha256']==par['model_sha256']
    assert read(D/'neutral/scene.json')['model']==par['model_sha256']
    sets=[]
    for title,wdir,cdir in [('11B',D/'controls/wood',D/'controls/clay'),('12A',D/'paired',D/'neutral')]:
        from PIL import ImageOps
        def frame(image):return image.crop((90,20,560,630))
        sets.append([(title+' walnut, near',frame(rgba(wdir/'near.png'))),(title+' walnut, mirrored far',frame(ImageOps.mirror(rgba(wdir/'far.png')))),
           (title+' clay, 54°',rgba(cdir/'fixed.png').crop((125,190,620,854))),
           (title+' clay, side',rgba(cdir/'side.png').crop((120,0,875,940))),
           (title+' clay, rear quarter',rgba(cdir/'rear-quarter.png').crop((100,10,870,945)))])
    sheet(D/'diagnostics.png',sets,(225,285))
if __name__=='__main__':main()

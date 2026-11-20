"""Compare the registered sources and renders without fitting the material to projected samples."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
D=Path(__file__).resolve().parent;R=D.parents[2];B=D.parent;AS=R/'assets/knight'
BLACK=(0,0,0)
def open_rgb(file):
    im=Image.open(file).convert('RGBA');bg=Image.new('RGBA',im.size,(0,0,0,255));return Image.alpha_composite(bg,im).convert('RGB')
def source_pair():
    high=open_rgb(AS/'ref.png');orig=Image.open(AS/'original.png').convert('RGBA');align=json.loads((AS/'original-alignment.json').read_bytes());fac=align['scale']*300/high.width
    low=orig.transform(high.size,Image.Transform.AFFINE,(fac,0,align['x']*3,0,fac,align['y']*3),Image.Resampling.BILINEAR)
    return Image.alpha_composite(Image.new('RGBA',low.size,(0,0,0,255)),low).convert('RGB'),high
def Y(im,sigma=0):return np.asarray(im if sigma==0 else im.filter(ImageFilter.GaussianBlur(sigma)),dtype=float)@[.2126,.7152,.0722]
def inspect():
    orig,ref=source_pair();l=Image.open(AS/'ref.png').convert('RGBA');refmask=np.max(np.asarray(ref),axis=2)>6
    # Match the lead silhouette implementation.
    sys.path.insert(0,str(R/'scripts/knight'))
    from audit_mission import silhouette
    refmask=silhouette(l,True)
    trace=json.loads((B/'round-011-judge/mane-hollow.json').read_bytes())['Black 2']['samples'];yy,xx=np.array([row[:2] for row in trace]).T
    arc=np.array(json.loads((B/'round-013-judge/mane-pigment-origin.json').read_bytes())['path_y_x'])
    path=D/'wood.png';finished=path.exists()
    wood=open_rgb(path if finished else D/'preview-studio.png');albedo=open_rgb(D/'albedo-fixed.png' if (D/'albedo-fixed.png').exists() else D/'preview-albedo.png')
    pics={'Original at board scale':orig,'Black 2':ref,'Parent 13A':open_rgb(D/'parent-wood.png'),'14A walnut':wood,'Parent pigment':open_rgb(B/'round-013-judge/mane-passes-parent/pigment.png'),'14A pigment':albedo}
    masks=np.zeros(refmask.shape,bool);section=[];rows=np.arange(488,582);frac=np.arange(3,164,2)
    for y in range(463,622):
        a=np.flatnonzero(refmask[y])[0];bb=np.interp(y,yy,xx);w=bb-a;masks[y,round(a+.2*w):round(a+.71*w)]=True
        if y in rows:section.append(np.rint(a+frac/100*w).astype(int))
    xs=np.array(section);result={};sheet=Image.new('RGB',(6*164,301),'#222826');pen=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=13)
    for i,(label,im) in enumerate(pics.items()):
        lum=Y(im);lo=Y(im,2);hi=Y(im,8);res=Y(im,1.5)-hi
        dy,dx=np.gradient(res);u,v=dx[masks],dy[masks]
        val,axes=np.linalg.eigh([[np.mean(u*u),np.mean(u*v)],[np.mean(u*v),np.mean(v*v)]])
        direction=(np.degrees(np.arctan2(axes[1,0],axes[0,0]))+90)%180-90
        ys,px=arc.T;ctr=lo[ys,px];shoulders=(lo[ys,px-8]+lo[ys,px+8])/2
        profile=np.median(Y(im,3)[rows[:,None],xs],axis=0)
        result[label]={'median_luminance':round(float(np.median(lum[masks])),2),
          'old_arc_relative_recess':round(float(np.median((shoulders-ctr)/np.maximum(12,shoulders))),3),
          'grain_degrees':round(float(direction),1),'grain_coherence':round(float((val[1]-val[0])/val.sum()),3),
          'fine_contrast':round(float(np.sqrt(np.mean(((lum-lo)/np.maximum(lo,12))[masks]**2))),3),
          'mid_contrast':round(float(np.sqrt(np.mean(((lo-hi)/np.maximum(hi,12))[masks]**2))),3),
          'face_rear':round(float(np.median(profile[(frac>=19)&(frac<=41)])),1),'face_inside':round(float(np.median(profile[(frac>=59)&(frac<=81)])),1),
          'registered_hollow':round(float(np.min(profile[(frac>=93)&(frac<=105)])),1)}
        sheet.paste(im.crop((175,405,325,658)).resize((161,263),Image.Resampling.LANCZOS),(164*i,25));pen.text((i*164+4,5),label,font=font,fill='#e4e4db')
    (D/'appearance.json').write_text(json.dumps(result,indent=2)+'\n');sheet.save(D/'mane-study.png')
    print(json.dumps({k:v for k,v in result.items() if '14A' in k},indent=1))
    if not finished:return
    board=Image.new('RGB',(480,148),'#222826');p=ImageDraw.Draw(board)
    align=json.loads((AS/'original-alignment.json').read_bytes())
    native=open_rgb(AS/'original.png');fac=align['scale']*native.width/ref.width
    extent=(-align['x']*3/fac,-align['y']*3/fac,(native.width-align['x']*3)/fac,(native.height-align['y']*3)/fac)
    for i,(label,im) in enumerate(list(pics.items())[:4]):
        small=native.resize((100,100),Image.Resampling.LANCZOS) if i==0 else im.resize((100,100),Image.Resampling.LANCZOS,box=extent)
        board.paste(small,(10+120*i,30));p.text((8+120*i,8),'Original sprite' if i==0 else label,font=font,fill='white')
    board.save(D/'board.png')
    if (D/'uniform-far.png').exists():
        sheet=Image.new('RGB',(5*183,4*217),'#242825');p=ImageDraw.Draw(sheet)
        for j,kind in enumerate(['wood','albedo','neutral','uniform']):
            for i,name in enumerate(['near','rear-quarter','back','far-quarter','far']):
                im=open_rgb(D/(kind+'-'+name+'.png'));im=im.resize((183,183),Image.Resampling.LANCZOS)
                sheet.paste(im,(i*183,j*217+25));p.text((i*183+5,j*217+6),kind+' / '+name,font=font,fill='white')
        sheet.save(D/'all-around.png')
if __name__=='__main__':inspect()

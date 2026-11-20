"""Compare the two approved references, true studio renders and unlit pigment."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from reference_images import registered,black
BOX=(175,374,436,716);DETAIL=(0,58,152,275)
F=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',13)
def lum(im,s=0):
    if s:im=im.filter(ImageFilter.GaussianBlur(s))
    return np.asarray(im,float)@[.2126,.7152,.0722]
def main(keys):
    refs=registered();src=black(refs['selected']);orig=black(refs['original'])
    tracks=np.array(json.loads((D/'arc-samples.json').read_text())['path_y_x'])
    hh=np.array([r[:2] for r in json.loads((D/'hollow-samples.json').read_text())['Black 2']['samples']])
    y,x=tracks.T;y=y-BOX[1];x=x-BOX[0];hollow=np.rint(np.interp(y+BOX[1],hh[:,0],hh[:,1])).astype(int)-BOX[0]
    mask=(np.asarray(refs['selected'])[:,:,3]>127)&(np.asarray(refs['selected'])[:,:,:3].max(2)>12)
    outer=np.array([np.flatnonzero(row)[0] if row.any() else -1 for row in mask])-BOX[0]
    yy=np.arange(488,582)-BOX[1];edge=np.interp(yy+BOX[1],hh[:,0],hh[:,1])-BOX[0]
    low=outer[yy+BOX[1]]
    pct=np.arange(3,165,2);where=np.rint(low[:,None]+(edge-low)[:,None]*pct[None,:]/100).astype(int)
    local=np.zeros((BOX[3]-BOX[1],BOX[2]-BOX[0]),bool)
    for s in range(463,622):
        l=outer[s];r=np.interp(s,hh[:,0],hh[:,1])-BOX[0]
        local[s-BOX[1],round(l+(r-l)*.2):round(l+(r-l)*.71)]=True
    def metrics(im):
        a=lum(im,2)
        recess=((a[y,x+8]+a[y,x-8])*.5-a[y,x])/np.maximum(12.,(a[y,x+8]+a[y,x-8])*.5)
        candidates=[];prev={};hist=[]
        for row,left,end in zip(y,outer[y+BOX[1]],hollow):
            cols=np.arange(round(left+.24*(end-left)),round(left+.72*(end-left))+1)
            shoulder=(a[row,cols-8]+a[row,cols+8])*.5
            rel=(shoulder-a[row,cols])/np.maximum(12.,shoulder)
            cur={};jumps={}
            for c,vv in zip(cols,rel):
                if prev:
                    best=min((prev.get(c+j,np.inf)+.024*abs(j),c+j) for j in range(-3,4))
                    cur[c]=-vv+best[0];jumps[c]=best[1]
                else:cur[c]=-vv
            candidates.append(dict(zip(cols,rel)));hist.append(jumps);prev=cur
        point=min(prev,key=prev.get);strong=[]
        for n in reversed(range(len(hist))):
            strong.append(candidates[n][point])
            if n:point=hist[n][point]
        q=np.median(lum(im,3)[yy[:,None],where],axis=0)
        inner=np.arange(-7,8);off=a[y[:,None],hollow[:,None]+inner].argmin(1)-7
        short=lum(im,1.5)-lum(im,8);dy,dx=np.gradient(short);vx,vy=dx[local],dy[local]
        e,v=np.linalg.eigh([[np.mean(vx*vx),np.mean(vx*vy)],[np.mean(vx*vy),np.mean(vy*vy)]])
        angle=(np.degrees(np.arctan2(v[1,0],v[0,0]))+90)%180-90
        return {'old_arc_percent':round(100*float(np.median(recess)),2),'independent_arc_percent':round(100*float(np.median(strong)),2),
                'real_hollow_center':round(float(np.median(a[y,hollow+off])),2),'hollow_offset_pixels':round(float(np.median(abs(off))),2),
                'rear_third':round(float(np.median(q[(pct>=21)&(pct<=39)])),2),'inner_third':round(float(np.median(q[(pct>=65)&(pct<=83)])),2),
                'figure_angle_deg':round(float(angle),2),'figure_coherence':round(float((e[1]-e[0])/e.sum()),3),
                'crosswise_2to8px_rms':round(float(np.sqrt(np.mean(((lum(im,2)-lum(im,8))[local]/np.maximum(12.,lum(im,8)[local]))**2))),3),
                'pore_0to2px_rms':round(float(np.sqrt(np.mean(((lum(im)-lum(im,2))[local]/np.maximum(12.,lum(im,2)[local]))**2))),3)}
    sets=[('Original',orig.crop(BOX),None),('Black 2',src.crop(BOX),None)]
    for key in keys:
        name='13A' if key=='parent' else '14B' if key=='knight' else key
        f=D/('wood.png' if key=='knight' else 'parent-wood.png' if key=='parent' else f'trial-{key}-wood.png')
        if not f.exists():continue
        rgb=black(Image.open(f).convert('RGBA'));rgb=rgb.crop(BOX) if rgb.size!=sets[0][1].size else rgb
        albedo=D/f'trial-{key}-pigment.png'
        sets.append((name,rgb,black(Image.open(albedo).convert('RGBA')) if albedo.exists() else None))
    sheet=Image.new('RGB',(185*len(sets),613),'#242927');draw=ImageDraw.Draw(sheet);out={}
    for i,(name,rgb,pig) in enumerate(sets):
        info=metrics(rgb);out[name]={'wood':info}
        x0=185*i;draw.text((x0+4,4),name,font=F,fill='white')
        sheet.paste(rgb.crop(DETAIL).resize((183,262),Image.Resampling.LANCZOS),(x0,23))
        draw.text((x0+3,288),f"arc {info['old_arc_percent']}% / grain {info['figure_angle_deg']}°",font=F,fill='#f1dfc9')
        if pig:
            out[name]['pigment']=metrics(pig)
            sheet.paste(pig.crop(DETAIL).resize((183,262),Image.Resampling.LANCZOS),(x0,322))
            draw.text((x0+3,587),f"pigment arc {out[name]['pigment']['old_arc_percent']}%",font=F,fill='#efe2cb')
        print(name,out[name],flush=True)
    stem='registered-study' if 'knight' in keys else 'study';sheet.save(D/(stem+'.png'));(D/(stem+'.json')).write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main(sys.argv[1:])

"""Build the final comparison sheets directly from signed references and native renders."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from reference_images import black,registered
from light import OFF
BG='#252a29';TXT='#efeee8';RES=Image.Resampling.LANCZOS
F=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15);H=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
def read(name):return Image.open(D/name).convert('RGBA')
def title(c,x,y,t,font=F):ImageDraw.Draw(c).text((x,y),t,font=font,fill=TXT)
def draw_image(c,im,r):
    x,y,w,h=r;image=ImageOps.contain(black(im),(w,h),RES)
    c.paste(image,(x+(w-image.width)//2,y+(h-image.height)//2))
def fixed():
    refs=registered();items=[('Original',refs['original']),('Black 2',refs['selected']),('11B parent',read('parent-wood.png')),('12B',read('wood.png'))]
    im=Image.new('RGB',(1024,912),BG);title(im,10,5,'The sweep below the ear',H)
    for i,(name,img) in enumerate(items):
        x=i*256;title(im,x+7,40,name)
        draw_image(im,img.crop((152,269,792,1069)),(x,69,256,320))
        draw_image(im,img.crop((175,395,401,690)),(x,407,256,334))
        draw_image(im,img.crop((143,268,943,1068)),(x+88,774,80,80))
    title(im,12,873,'The same registered crop at 80 px appears below the detail.')
    im.save(D/'registered-and-board.png')
def orbit():
    c=Image.new('RGB',(1150,550),BG);title(c,8,5,'The new mane and neck in the round',H)
    for i,(s,cl,label) in enumerate([('near',0,'Near'),('front',4,'Front'),('opposite',8,'Far'),('rear-quarter',10,'Rear quarter'),('rear',12,'Rear')]):
        x=i*230;title(c,x+6,44,label)
        draw_image(c,read('wood-'+s+'.png'),(x,74,228,228));draw_image(c,read(f'clay-{cl:02d}.png'),(x,308,228,228))
    c.save(D/'orbit-proof.png')
    frames=[black(read(f'clay-{i:02d}.png')).resize((400,400),RES) for i in range(16)]
    frames[0].save(D/'clay-turn.webp',save_all=True,append_images=frames[1:],duration=180,loop=0,quality=88)
def moving():
    c=Image.new('RGB',(900,956),BG);title(c,12,5,'A moving light on the two physical flanks',H)
    for j,n in enumerate(['From the back','From the side','From the nose']):
        title(c,104+j*260,44,n)
    for i,(m,f) in enumerate([('parent','near'),('knight','near'),('parent','far'),('knight','far')]):
        y=72+218*i;title(c,6,y+68,'11B' if m=='parent' else '12B');title(c,6,y+93,f+' side')
        for j in range(3):draw_image(c,read(f'moving-{m}-{f}-{j}.png'),(84+j*260,y,252,216))
    c.save(D/'moving-light.png')
def curve(c,rect,x,y,xmin,xmax,ymin,ymax,color):
    x0,y0,w,h=rect;x=np.asarray(x);y=np.asarray(y);good=np.isfinite(y)&(x>=xmin)&(x<=xmax)
    pts=[(x0+(v-xmin)/(xmax-xmin)*w,y0+h-(u-ymin)/(ymax-ymin)*h) for v,u in zip(x[good],y[good])]
    if len(pts)>1:ImageDraw.Draw(c).line(pts,fill=color,width=3)
def sections():
    c=Image.new('RGB',(980,728),BG);title(c,10,5,'Transverse geometry and the light across the cut',H)
    pairs={l:np.load(D/f'{l}-sections.npz') for l in ['parent','knight']}
    colors={'parent':'#a7b8bc','knight':'#e9ad6c'}
    title(c,12,47,'11B parent',F);ImageDraw.Draw(c).line([(106,59),(145,59)],fill=colors['parent'],width=3)
    title(c,170,47,'12B',F);ImageDraw.Draw(c).line([(221,59),(260,59)],fill=colors['knight'],width=3)
    for i,height in enumerate([2.83,3.15,3.55,3.97]):
        x0=42+(i%2)*474;y0=124+(i//2)*180
        title(c,x0,y0-28,f'Native near-side section · z {height:.2f}')
        rect=(x0,y0,413,113);ImageDraw.Draw(c).rectangle([x0,y0,x0+413,y0+113],outline='#434c49')
        for k,t in enumerate(['−1.43','−0.77','−0.10']):
            title(c,x0+k*192,y0+115,t)
        for l,d in pairs.items():
            row=abs(d['z']-height).argmin();depth=np.fmax.reduce(d['sides'][:,0,row],axis=0)
            curve(c,rect,d['x'],depth,-1.43,-.1,0,.76,colors[l])
    title(c,35,460,'Registered walnut brightness, relative to the dark line in Black 2')
    light=json.loads((D/'light-final.json').read_text())
    rect=(42,506,864,132);dr=ImageDraw.Draw(c);dr.rectangle((42,506,906,638),outline='#434c49')
    for lab,col in [('Original','#c9c4a8'),('Black 2','#dc965a'),('Parent','#a7b8bc'),('12B','#66c8ac')]:
        curve(c,rect,OFF,light[lab]['profile'],-25,63,0,76,col)
    for i,(lab,col) in enumerate([('Original','#c9c4a8'),('Black 2','#dc965a'),('Parent','#a7b8bc'),('12B','#66c8ac')]):
        dr.line((42+i*145,665,62+i*145,665),fill=col,width=3);title(c,70+i*145,653,lab)
    title(c,42,686,'Section axes give rear-to-front x and lateral distance from the midplane (0 to 0.76 units).')
    title(c,42,706,'Brightness is Rec. 709 luma. The horizontal range is −25 to +63 pixels from the photographed hollow.')
    c.save(D/'geometry-and-light.png')
def side_pair():
    out=Image.new('RGB',(920,554),BG);title(out,12,6,'The registered side camera',H)
    for i,(lab,file) in enumerate([('11B parent','parent-side.png'),('12B','wood-side.png')]):
        x=i*460;title(out,x+12,46,lab);draw_image(out,read(file).crop((250,120,975,1150)),(x,76,450,462))
    out.save(D/'paired-side.png')
def materials():
    c=Image.new('RGB',(990,595),BG);title(c,10,4,'Pigment and the cut under the studio lights',H)
    for i,(key,name) in enumerate([('parent','11B'),('knight','12B')]):
        for j,(mode,lab) in enumerate([('albedo','Pigment only'),('uniform','Uniform brown'),('native','Native walnut')]):
            x=j*330;y=i*259+67
            if i==0:title(c,x+6,36,lab)
            img=read(f'finish-{key}-{mode}.png') if mode!='native' else read('parent-wood.png' if i==0 else 'wood.png').crop((175,374,436,716))
            title(c,x+4,y+5,name);draw_image(c,img.crop((10,42,217,329)),(x+37,y,286,248))
    c.save(D/'material-control.png')
def sha(name):return hashlib.sha256((D/name).read_bytes()).hexdigest()
def main():
    fixed();orbit();moving();sections();side_pair();materials()
    files=['parent.blend','knight.blend','parent-pigment.png','pigment.png','wood.png','wood-side.png',
           'registered-and-board.png','orbit-proof.png','moving-light.png','geometry-and-light.png','clay-turn.webp','paired-side.png','material-control.png',
           'parameters.json','verified.json','light-final.json','sections-knight.json','qa-knight.json','moving.json',
           'carve.py','section_grid.py','verify.py','grain.py','atlas_input.py','pigment.py','moving.py','report.py',
           'evidence.py','diagnostics.py','qa_geometry.py','measure.py','finish_probe.py','light.py','reference_images.py','reproduce.ps1','REPORT.md',
           'review-copy/assets/knight/mesh.bin','review-copy/assets/knight/mesh.json','review-copy/assets/knight/varnish.bin']
    files+=[f'clay-{i:02d}.png' for i in range(16)]
    files+=[f'wood-{s}.png' for s in ['near','opposite','front','rear-quarter','rear']]
    data={name:sha(name) for name in files}
    masks={}
    for name,l,r in [('fixed','parent-wood.png','wood.png'),('side','parent-side.png','wood-side.png')]:
        a=np.asarray(read(l))[:,:,3]>127;b=np.asarray(read(r))[:,:,3]>127
        masks[name]={'iou_parent':float((a&b).sum()/(a|b).sum()),'changed_pixels':int((a^b).sum())}
    (D/'proof.json').write_text(json.dumps({'sha256':data,'parent_silhouettes':masks},indent=2)+'\n')
if __name__=='__main__':main()

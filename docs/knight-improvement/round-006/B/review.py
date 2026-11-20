from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/"scripts/knight"))
from audit_mission import registered,silhouette,iou
BG=(44,46,47);FONT=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf",17)
def panel(canvas,im,rect,box,title):
    x,y,w,h=box
    im=im.convert("RGBA")
    scale=im.width/1254
    im=im.crop(tuple(round(n*scale) for n in rect))
    f=min(w/im.width,(h-23)/im.height);im=im.resize((round(im.width*f),round(im.height*f)),Image.Resampling.LANCZOS)
    canvas.paste(im,(x+(w-im.width)//2,y),im)
    ImageDraw.Draw(canvas).text((x+w/2,y+h-20),title,font=FONT,anchor="mt")
def main():
    fixed=(158,262,752,722);side=(264,112,884,785)
    eye=(444,444,566,514);side_eye=(590,283,735,371)
    refs=registered()
    names=["Parent","B"]
    flat=Image.new("RGB",(1016,654),BG)
    for i,name in enumerate(names):
        pre="parent-" if i==0 else ""
        for j,(view,rect) in enumerate([("fixed",fixed),("side",side)]):
            img=Image.open(OUT/f"{pre}clay-{view}.png")
            panel(flat,img,rect,(j*508,i*327,508,327),name+" · "+view+" clay")
    flat.save(OUT/"flat-comparison.png")
    sheet=Image.new("RGB",(1120,654),BG)
    pics=[refs["original"],refs["selected"],Image.open(OUT/"parent-wood.png"),Image.open(OUT/"wood.png")]
    for i,(name,img) in enumerate(zip(["Original","Black candidate 2","Parent","B"],pics)):
        panel(sheet,img,fixed,(280*i,0,280,245),name+" · fixed")
        panel(sheet,img,eye,(280*i,255,280,173),name+" · eye")
    for i,name in enumerate(names):
        img=Image.open(OUT/("parent-side.png" if i==0 else "wood-side.png"))
        panel(sheet,img,side_eye,(280*i+280,453,280,187),name+" · side eye")
    sheet.save(OUT/"carving-study.png")
    contact=Image.new("RGB",(1056,698),BG)
    for i,(name,im) in enumerate(list(zip(["Original","Black candidate 2","Parent fixed","B fixed"],pics))+
                    [("Parent side",Image.open(OUT/"parent-side.png")),("B side",Image.open(OUT/"wood-side.png"))]):
        crop=(137,240,802,1085) if i<4 else (250,103,939,1154)
        panel(contact,im,crop,(i*176,0,176,220),name)
        mini=im.convert("RGBA").resize((90,90),Image.Resampling.LANCZOS)
        contact.paste(mini,(i*176+43,220),mini)
    for i,(suffix,idx) in enumerate([("near",0),("front",4),("opposite",8),("rear-quarter",10),("rear",12)]):
        for j,(f,name) in enumerate([(OUT/f"wood-{suffix}.png",suffix),(OUT/f"clay-{idx:02d}.png","Clay · "+suffix)]):
            if f.exists():
                im=Image.open(f);panel(contact,im,(260,75,1020,1208),(i*211,311+191*j,211,186),name)
    contact.save(OUT/"contact.png")
    if (OUT/"clay-15.png").is_file():
        frames=[]
        for i in range(16):
            im=Image.open(OUT/f"clay-{i:02d}.png").convert("RGBA").crop((110,24,539,625))
            f=Image.new("RGB",im.size,BG);f.paste(im,(0,0),im);f.thumbnail((330,400),Image.Resampling.LANCZOS);frames.append(f)
        frames[0].save(OUT/"clay-turn.webp",save_all=True,append_images=frames[1:],duration=350,loop=0,quality=88)
    compare={}
    masks=[silhouette(im,i<2) for i,im in enumerate(pics)]
    xx=np.arange(476,531,2);yy=np.rint(np.interp(xx,[476,488,504,518,530],[488,495,499,500,499])).astype(int)
    for i,im in enumerate(pics):
        rgb=np.asarray(im.convert("RGB").filter(ImageFilter.GaussianBlur(1.8)))@[.2126,.7152,.0722]
        l=rgb[yy,xx].mean();b=np.mean([rgb[yy+k,xx] for k in range(8,15)])
        compare[["Original","Black candidate 2","Parent","B"][i]]={"whole_IoU_with_original":round(iou(masks[i],masks[0]),6),
            "whole_IoU_with_black2":round(iou(masks[i],masks[1]),6),"lower_lid_trace":round(l,2),"cheek_below":round(b,2)}
    (OUT/"feature-metrics.json").write_text(json.dumps(compare,indent=2)+"\n")
    depths={}
    lines={}
    for i,name in enumerate(["Original","Black 2","Parent","B"]):
        rgba=np.asarray(pics[i].convert("RGBA"))
        mask=rgba[:,:,3]>127
        if i<2:mask&=rgba[:,:,:3].max(axis=2)>12
        lines[name]={}
        for y in range(535,656):
            row=mask[y,500:800]
            xs=np.flatnonzero(row[:-4]&row[1:-3]&row[2:-2]&row[3:-1]&row[4:])
            if len(xs):lines[name][y]=int(xs[-1]+504)
    for name in ["Parent","B"]:
        depths[name]={}
        for ref in ["Original","Black 2"]:
            depths[name][ref]={}
            for low,high in [(540,580),(581,655)]:
                depths[name][ref][f"{low}-{high}"]=round(np.mean([abs(lines[name][y]-lines[ref][y]) for y in range(low,high+1)]),2)
    (OUT/"chest-edges.json").write_text(json.dumps({"rows":lines,"mean_absolute_error_px":depths},indent=2)+"\n")
    throat=Image.new("RGB",(1108,282),"#1a1c1c")
    d=ImageDraw.Draw(throat)
    for i,label in enumerate(["Original","Black 2","Parent","B"]):
        from audit_mission import black
        d.text((277*i+4,4),label,fill="white")
        throat.paste(black(pics[i].convert("RGBA")).crop((493,434,770,694)),(277*i,22))
    throat.save(OUT/"throat-and-chest.png")
if __name__=="__main__":main()

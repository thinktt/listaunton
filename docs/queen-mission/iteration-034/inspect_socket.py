from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont

P=Path(__file__).resolve().parent
S=P.parents[2]
controls=np.load(P/'controls-033.npy')
r=np.linalg.norm(controls[:,:,:2],axis=2).mean(1);z=controls[:,:,2].mean(1)
reg=json.loads((S/'assets/queen/original-reference-alignment.json').read_text());scale=reg['scale']
def original(color):
    return Image.open(S/f'references/lichess-staunton-3d/{color}-Queen.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,(1/scale,0,-reg['offset_x']/scale,0,1/scale,-reg['offset_y']/scale),Image.Resampling.BILINEAR)
def bg(im):
    out=Image.new('RGBA',im.size,(16,21,28,255));out.alpha_composite(im.convert('RGBA'));return out.convert('RGB')
images=[original('Black'),original('White'),Image.open(S/'assets/queen/reference.png'),Image.open(P/'current-snapshot/queen-brown.png'),Image.open(P/'current-snapshot/queen-matched.png')]
names=['Original black','Original white','Selected high-res','Current wood','Current neutral']
box=(315,610,650,890);factor=1.5;width=503;height=420
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
arcs=[]
for ring in [29,33,35,37,38,39]:
    rad=(r[ring-1]+4*r[ring]+r[ring+1])/6
    zz=(z[ring-1]+4*z[ring]+z[ring+1])/6
    phi=np.linspace(-np.pi/2,np.pi/2,181)
    points=np.c_[483.625+264.61125*rad*np.sin(phi),860.223491056495-264.61125*np.cos(np.deg2rad(54))*zz+264.61125*np.sin(np.deg2rad(54))*rad*np.cos(phi)]
    arcs.append({'ring':ring,'radius':float(rad),'height':float(zz),'front_y':float(points[90,1]),'points':points.tolist()})
for overlay in [False,True]:
    sheet=Image.new('RGB',(width*5,height+75),(16,21,28));d=ImageDraw.Draw(sheet)
    for j,(name,im) in enumerate(zip(names,images)):
        crop=bg(im).crop(box).resize((width,height));pen=ImageDraw.Draw(crop)
        if overlay:
            for arc,col in zip(arcs,['#c385d5','#fe735a','#fad47c','#62d4f4','#6ee6a0','#b0cefa']):
                xy=[((x-box[0])*factor,(y-box[1])*factor) for x,y in arc['points']]
                pen.line(xy,fill=col,width=1)
                pen.text((xy[10][0],xy[10][1]),str(arc['ring']),fill=col)
        sheet.paste(crop,(j*width,45));d.text((j*width+10,10),name,fill='white',font=font)
    d.text((10,height+50),'All sources keep the accepted registration. Lines are cubic-limit ring estimates, not detected image edges.',fill='white')
    sheet.save(P/('socket-ring-overlay.png' if overlay else 'socket-sources.png'))
(P/'projected-socket-rings.json').write_text(json.dumps(arcs,indent=2)+'\n')
print(json.dumps([{k:v for k,v in row.items() if k!='points'} for row in arcs],indent=2))

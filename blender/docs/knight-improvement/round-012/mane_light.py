"""Compare the light crossing the source mane hollow on one registered grid."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);extra=sys.argv[3:]
asset=root/'assets/knight';build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'));from audit_mission import registered,black
trace=json.loads((build/'round-011-judge/mane-hollow.json').read_bytes())
rows=np.array([(y,x) for y,x,*_ in trace['Black 2']['samples'] if 470<=y<=625])
off=np.arange(-25,64)
refs=registered()
imgs={'Original black':refs['original'],'Black 2':refs['selected'],'Parent':Image.open(asset/'render.png')}
for name in extra:
    imgs[name]=Image.open(build/f'improvement-{n:03}-{name}/wood.png')
colors={'Original black':'#bcc4b2','Black 2':'#ffbd77','Parent':'#acc5ce','A':'#b39de1','B':'#5ad3a2'}
report={};profiles={}
w,h=196,263;box=(176,422,370,680)
sheet=Image.new('RGB',(w*len(imgs),h+214),'#242724');d=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=14)
for i,(name,pic) in enumerate(imgs.items()):
    rgb=black(pic.convert('RGBA'))
    smooth=np.asarray(rgb.filter(ImageFilter.GaussianBlur(2.5)),float)@[.2126,.7152,.0722]
    strips=smooth[rows[:,0,None],rows[:,1,None]+off]
    profiles[name]=strips
    x=w*i;d.text((x+4,5),name,font=font,fill='#efeee8');sheet.paste(rgb.crop(box),(x+1,28))
    prof=np.median(strips,axis=0)
    center=float(np.median(prof[np.abs(off)<=3]))
    mane=float(np.median(prof[(off>=-25)&(off<=-14)]))
    neck=float(np.median(prof[(off>=20)&(off<=39)]))
    nearest=int(off[np.argmin(prof)])
    report[name]={'luminance_mane':round(mane,2),'luminance_at_source_hollow':round(center,2),'luminance_neck':round(neck,2),
                  'neck_minus_hollow':round(neck-center,2),'mane_minus_hollow':round(mane-center,2),'darkest_offset_in_median_strip':nearest,
                  'median_profile':np.round(prof,2).tolist()}
    for ref in ['Original black','Black 2']:
        if ref not in profiles:continue
        target=profiles[ref]
        report[name]['against '+ref]={'luma_mae':round(float(np.abs(strips-target).mean()),2),
                                      'pattern_correlation':round(float(np.corrcoef(strips.ravel(),target.ravel())[0,1]),4)}
x0=45;y0=310;pw=sheet.width-72;ph=119
maximum=max(65.,max(max(row['median_profile']) for row in report.values())*1.06)
for val in np.linspace(0,maximum,4):
    y=y0+ph-ph*val/maximum;d.line((x0,y,x0+pw,y),fill='#3c443d');d.text((x0-28,y-7),str(round(val)),font=font,fill='#dce0d7')
for val in [-20,0,20,40,60]:
    x=x0+(val-off[0])*pw/(off[-1]-off[0]);d.line((x,y0,x,y0+ph),fill='#8b8270' if val==0 else '#3c443d')
    d.text((x-8,y0+ph+3),str(val),font=font,fill='#dce0d7')
for name,item in report.items():
    points=[(x0+i*pw/(len(off)-1),y0+ph-v*ph/maximum) for i,v in enumerate(item['median_profile'])]
    d.line(points,fill=colors[name],width=2)
    x=list(report).index(name)*w+5;d.line((x,299,x+20,299),fill=colors[name],width=3)
    d.text((x+24,290),name,font=font,fill='#dedfd4')
d.text((x0,453),'Distance from source hollow (px). Lines give median brightness.',font=font,fill='#e6e7de')
sheet.save(out/'mane-light.png')
(out/'mane-light.json').write_text(json.dumps({'method':'Median Rec.709 sRGB luminance across registered horizontal profiles, blurred 2.5 px. Measurements cover image rows 470 to 625, sampled every 3 px on the recorded Black 2 shadow center. The brightest and darkest anchors use the same locations on every model.','offsets':off.tolist(),'profiles':report},indent=2)+'\n')
for k,row in report.items():print(k,{key:value for key,value in row.items() if key!='median_profile'})

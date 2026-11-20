"""Separate the effect of a new carving from changes to the studio lights."""
from pathlib import Path
import sys,json
from PIL import Image,ImageDraw,ImageFont
import numpy as np
root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);labels=sys.argv[3:]
build=root/'build/knight-mission';out=build/f'round-{n:03}-judge'
sys.path.insert(0,str(root/'scripts/knight'));from audit_mission import black,registered
box=(452,445,567,516);w,h=240,150
sheet=Image.new('RGB',(3*w,len(labels)*(h+24)),'#242625');d=ImageDraw.Draw(sheet);f=ImageFont.load_default(size=13)
ref=black(registered()['selected']);report={}
def crop(im):
    return black(im.convert('RGBA')).crop(box)
def dist(left,right):
    return round(float(abs(np.array(left,float)-np.array(right,float)).mean()),3)
control=out/'studio-control/fixed.png'
baseline=out/'studio-parent/fixed.png'
if control.is_file():
    report['reloaded_identical_scene_mae']=dist(crop(Image.open(control)),crop(Image.open(baseline)))
for row,label in enumerate(labels):
    path=root/'assets/knight/render.png' if label=='parent' else build/f'improvement-{n:03}-{label}/wood.png'
    actual=crop(Image.open(path));common=crop(Image.open(out/f'studio-{label}/fixed.png'));target=ref.crop(box)
    for col,(name,img) in enumerate([('Black 2',target),(label+' / common studio',common),(label+' / saved studio',actual)]):
        x=col*w;y=row*(h+24);d.text((x+4,y+3),name,font=f,fill='#eeeeea')
        sheet.paste(img.resize((w-3,h),Image.Resampling.LANCZOS),(x,y+22))
    report[label]={'rgb_mae_common_vs_target':dist(common,target),'rgb_mae_saved_vs_target':dist(actual,target),'rgb_mae_common_vs_saved':dist(actual,common)}
sheet.save(out/'eye-studio-comparison.png')
(out/'eye-studio-comparison.json').write_text(json.dumps({'eye_crop':box,'results':report,'method':'Three identical crops. The common-light pass uses the complete released parent studio and the actual candidate mesh and material. The full reference render uses that candidate’s saved studio.'},indent=2)+'\n')
print(report)

"""Register the pawn's side render to its imagined guide using only base width and foot."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'assets/pawn';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def foot(path):
    a=np.array(Image.open(path).convert('RGBA'));mask=a[:,:,3]>127;y,x=np.nonzero(mask);floor=int(y.max()+1);top=int(y.min());rows=[]
    for row in range(int(floor-(floor-top)*.25),floor):
        xs=np.flatnonzero(mask[row])
        if len(xs):rows.append((int(xs[-1]-xs[0]+1),int(xs[0]),int(xs[-1]),row))
    width,left,right,row=max(rows);return {'width':width,'center':(left+right+1)/2,'floor':floor,'row':row}
guide=ROOT/'assets/pawn/concepts/side-01-cutout.png';profile=out/'profile.png';g=foot(guide);m=foot(profile);scale=g['width']/m['width'];padding=160
record={'guide':'assets/pawn/concepts/side-01-cutout.png','profile':'assets/pawn/profile.png','guide_sha256':sha(guide),'profile_sha256':sha(profile),'source_blend_sha256':sha(ROOT/'models/pawn/pawn-rebuilt.blend'),'canvas':[1254,1414],'guide_top':padding,'scale':scale,'offset_x':g['center']-scale*m['center'],'offset_y':g['floor']+padding-scale*m['floor'],'guide_foot':g,'model_foot':m,'method':'Uniform scale and translation only: equal base width and common floor. Guide is imagined, not geometric ground truth.'}
record['profile_dimensions']=list(Image.open(profile).size)
record['guide_dimensions']=list(Image.open(guide).size)
(out/'side-registration.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2))

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
presentation=out/'side-presentation.json'
if presentation.exists():
    lighting=json.loads(presentation.read_text(encoding='utf8'))
    assert lighting['model_sha256']==record['source_blend_sha256'] and lighting['profile_sha256']==record['profile_sha256']
    assert lighting['same_editable_object_and_material']
    record['presentation_scene']=lighting['scene']
    record['lighting_preset']=lighting['lighting_preset']
    if 'portrait' in lighting:
        camera = lighting['portrait']
        path = ROOT / camera['file']
        assert sha(path) == camera['sha256']
        measured = foot(path)
        portrait_scale = g['width'] / measured['width']
        with Image.open(path) as image:
            dimensions = list(image.size)
        record['portrait'] = {
            'profile': camera['file'], 'profile_sha256': camera['sha256'],
            'profile_dimensions': dimensions, 'elevation': camera['elevation'],
            'model_foot': measured, 'scale': portrait_scale,
            'offset_x': g['center'] - portrait_scale * measured['center'],
            'offset_y': g['floor'] + padding - portrait_scale * measured['floor'],
        }
(out/'side-registration.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2))

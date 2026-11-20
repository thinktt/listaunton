"""Record evidence for checkpoint 31 from actual saved outputs."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[2]
out=root/'docs/queen-mission/iteration-031'
trial=root/'build/queen-mission/254-rounded-collar-join'
assets=root/'assets/queen'
source=root/'history/queen-mission-029'
out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
data=np.load(trial/'control-comparison.npz')
before,after=data['before'],data['after']
changed=np.flatnonzero(np.any(before!=after,axis=(1,2))).tolist()
assert changed==[48,49]
assert np.array_equal(before[:,:,:2],after[:,:,:2])
measure={'changed_rings_from_checkpoint_29':changed,
    'all_radii_exact':True,'all_other_controls_exact':True,
    'ring_z_before_after':{str(i):[float(before[i,0,2]),float(after[i,0,2])] for i in [48,49,50]},
    'stem_join_vertical_gap_before_after':[float(a[50,0,2]-a[49,0,2]) for a in [before,after]],
    'source_blend_sha256':sha(source/'queen-rebuilt.blend'),
    'accepted_blend_sha256':sha(root/'models/queen/queen-rebuilt.blend')}
(out/'geometry-delta.json').write_text(json.dumps(measure,indent=2)+'\n')
fit=json.loads((assets/'finish-comparison.json').read_text())['silhouette_iou']['revised_54_degree']
scores={'original_black_iou_percent':100*fit['original_black'],
    'selected_highres_iou_percent':100*fit['selected_highres'],
    'subjective':{'interior_and_side_shape':88,'wood_color':85,'grain_texture':79,'lighting':76},
    'working_mean_percent':(100*fit['original_black']+88+85+79+76)/5,
    'holistic_range_percent':[80,85],
    'reason':'Flatter stem join under the rounded lower collar; outside outline unchanged. Base compression is rejected.',
    'complete':False}
(out/'scores.json').write_text(json.dumps(scores,indent=2)+'\n')
references=[root/'references/lichess-staunton-3d/Black-Queen.png',
    root/'references/lichess-staunton-3d/White-Queen.png',assets/'reference.png',
    assets/'concepts/side-01.png',root/'assets/side-views/defaults.json']
(out/'source-hashes.json').write_text(json.dumps({p.relative_to(root).as_posix():sha(p) for p in references},indent=2)+'\n')
font_path=Path('C:/Windows/Fonts/segoeui.ttf')
font=ImageFont.truetype(str(font_path),21) if font_path.exists() else ImageFont.load_default(size=21)
box=(140,175,460,810)
w,h=box[2]-box[0],box[3]-box[1]
canvas=Image.new('RGB',(2*w+30,h+60),(15,20,26))
draw=ImageDraw.Draw(canvas)
for i,(label,path) in enumerate([('Before — checkpoint 29',source/'queen-finished-profile.png'),
                               ('After — checkpoint 31',assets/'queen-finished-profile.png')]):
    x=i*(w+10)+5
    draw.text((x,12),label,font=font,fill='white')
    crop=Image.open(path).convert('RGBA').crop(box)
    canvas.paste(crop,(x,52),crop)
canvas.save(out/'side-before-after.png')
for name in ['finish-comparison.json','finish-validation.json','model-validation.json',
             'profile-landmarks.json','side-registration.json','overlay-metrics.json']:
    (out/name).write_bytes((assets/name).read_bytes())
print(json.dumps({'scores':scores,'geometry':measure},indent=2))

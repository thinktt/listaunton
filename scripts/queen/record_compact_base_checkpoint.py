"""Record checkpoint 32 evidence from the accepted saved renders and controls."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[2]
out=root/'docs/queen-mission/iteration-032'
trial=root/'build/queen-mission/262-compact-shelf-retain-stem'
assets=root/'assets/queen'
source=root/'history/queen-mission-031'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
data=np.load(trial/'control-comparison.npz');before,after=data['before'],data['after']
assert np.array_equal(before[48:],after[48:])
assert np.array_equal(before[38:,:,:2],after[38:,:,:2])
assert np.array_equal(before[0],after[0])
assert np.allclose(after[1:39,:,2],before[1:39,:,2]*.94,rtol=0,atol=2e-7)
radius=lambda a,i:float(np.linalg.norm(a[i,:,:2],axis=1).mean())
assert np.all(np.diff([radius(after,i) for i in range(24,39)])<=1e-6)
measure={'changed_rings_from_checkpoint_31':np.flatnonzero(np.any(before!=after,axis=(1,2))).tolist(),
    'all_controls_48_onward_exact':True,'all_stem_radii_38_onward_exact':True,'foot_ground_control_exact':True,
    'whole_base_vertical_factor':.94,
    'socket_seat_height_before_after':[float(a[38,0,2]) for a in [before,after]],
    'socket_wall_height_before_after':[float(a[33,0,2]-a[29,0,2]) for a in [before,after]],
    'socket_wall_radius_before_after':[radius(a,31) for a in [before,after]],
    'shelf_radial_span_before_after':[radius(a,33)-radius(a,38) for a in [before,after]],
    'inner_flare_radius_before_after':[radius(a,25) for a in [before,after]],
    'source_blend_sha256':sha(source/'queen-rebuilt.blend'),
    'accepted_blend_sha256':sha(root/'models/queen/queen-rebuilt.blend')}
(out/'geometry-delta.json').write_text(json.dumps(measure,indent=2)+'\n')
fit=json.loads((assets/'finish-comparison.json').read_text())['silhouette_iou']['revised_54_degree']
scores={'original_black_iou_percent':100*fit['original_black'],
    'selected_highres_iou_percent':100*fit['selected_highres'],
    'subjective':{'interior_and_side_shape':89,'wood_color':85,'grain_texture':79,'lighting':76},
    'working_mean_percent':(100*fit['original_black']+89+85+79+76)/5,
    'holistic_range_percent':[80,85],
    'reason':'Broader, shallower whole base and narrower compact socket, with its shelf/drop and accepted stem/collar curves preserved. Small original silhouette tradeoff is recorded; socket reflections still need refinement.',
    'complete':False}
(out/'scores.json').write_text(json.dumps(scores,indent=2)+'\n')
references=[root/'references/lichess-staunton-3d/Black-Queen.png',root/'references/lichess-staunton-3d/White-Queen.png',
    assets/'reference.png',assets/'concepts/side-01.png',root/'assets/side-views/defaults.json']
current={p.relative_to(root).as_posix():sha(p) for p in references}
previous=json.loads((root/'docs/queen-mission/iteration-031/source-hashes.json').read_text())
assert current==previous,'Source images or approved gallery defaults changed'
(out/'source-hashes.json').write_text(json.dumps(current,indent=2)+'\n')
font_path=Path('C:/Windows/Fonts/segoeui.ttf')
font=ImageFont.truetype(str(font_path),21) if font_path.exists() else ImageFont.load_default(size=21)
box=(140,175,460,810);width,height=box[2]-box[0],box[3]-box[1]
canvas=Image.new('RGB',(2*width+30,height+60),(15,20,26));draw=ImageDraw.Draw(canvas)
for i,(label,path) in enumerate([('Before — checkpoint 31',source/'queen-finished-profile.png'),('After — checkpoint 32',assets/'queen-finished-profile.png')]):
    x=i*(width+10)+5;draw.text((x,12),label,font=font,fill='white')
    crop=Image.open(path).convert('RGBA').crop(box);canvas.paste(crop,(x,52),crop)
canvas.save(out/'side-before-after.png')
for name in ['finish-comparison.json','finish-validation.json','model-validation.json','profile-landmarks.json','side-registration.json','overlay-metrics.json']:
    (out/name).write_bytes((assets/name).read_bytes())
print(json.dumps({'scores':scores,'geometry':measure},indent=2))

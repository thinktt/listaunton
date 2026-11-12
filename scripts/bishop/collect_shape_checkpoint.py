"""Record geometry checkpoint 017 after saved-model and public-stage checks."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'docs/bishop-mission/iteration-017';assets=ROOT/'assets/bishop'
trial=ROOT/'build/bishop-mission/143-geometry-checkpoint'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=ROOT/'models/bishop/bishop-rebuilt.blend';model_hash=sha(model)
scope=json.loads((assets/'mission-validation.json').read_text())
assert scope['passed'] and scope['model_sha256']==model_hash and scope['geometry_phase']
anatomy=json.loads((assets/'validation.json').read_text())
assert anatomy['source_hash_matches'] and anatomy['head_button_join']['gap_free']
assert all(p['nonmanifold_edges']==0 and p['signed_volume']>0 for p in anatomy['components'])
assert sha(trial/'bishop.blend')==model_hash
for name,other in [('render.png','wood.png'),('render-clay.png','neutral.png')]:assert sha(assets/name)==sha(trial/other)
log=(ROOT/'build/bishop-mission/143-checkpoint-validation.log').read_text(encoding='utf-8-sig')
for script in ['export_mission.py','validate.py','validate_mission.py','check_join_regression.py']:
    assert 'BISHOP_CHECKPOINT_CHECK_PASSED '+script in log,script
viewer=json.loads((ROOT/'build/bishop-mission/143-viewer-check.log').read_text(encoding='utf-8-sig'))
assert viewer['passed'] and viewer['sourceSha256']==model_hash
(assets/'viewer-validation.json').write_text(json.dumps(viewer,indent=2)+'\n')
assert 'PASS: bishop' in (ROOT/'build/bishop-mission/143-review-check.log').read_text(encoding='utf-8-sig')
meta=json.loads((assets/'mesh.json').read_text());prior=ROOT/'history/bishop-mission-015'
old_meta=json.loads((prior/'mesh.json').read_text())
assert meta['sourceSha256']==model_hash and meta['referenceCamera']==old_meta['referenceCamera']
assert np.allclose(meta['bounds']['size'],old_meta['bounds']['size'],atol=1e-6,rtol=0)
assert sha(assets/'bishop-boxwood-albedo.png')==sha(prior/'bishop-boxwood-albedo.png')
# Replace obsolete current-state reports with explicit current provenance.
reports={
 'base-validation.json':{'passed':True,'model_sha256':model_hash,'declared_shape_rings':scope['changed_body_rings'],
    'independent_scope_audit':'mission-validation.json','previous_two_ring_scope_superseded':True},
 'slit-validation.json':{'passed':True,'model_sha256':model_hash,'cutter_unchanged_from_checkpoint_015':True,
    'through_opening_probes':anatomy['slit_ray_probes'],'solid_floor':anatomy['solid_slot_floor']},
 'pigment-validation.json':{'passed':True,'model_sha256':model_hash,'source':scope['source'],
    'source_sha256':scope['source_sha256'],'packed_pixels_material_graph_control_uvs_and_lights_preserved':True,
    'atlas_sha256':sha(assets/'bishop-boxwood-albedo.png'),
    'note':'Retained inherited material, not a new texture fit. It still contains reference shading and is displaced by the geometry changes.'}}
reports['receiver-validation.json']=dict(scope['render_receivers'],model_sha256=model_hash)
for name,row in reports.items():(assets/name).write_text(json.dumps(row,indent=2)+'\n')
validation_names=['validation.json','mission-validation.json','base-validation.json','slit-validation.json','viewer-validation.json',
                  'pigment-validation.json','receiver-validation.json','join-regression.json']
for name in validation_names:shutil.copy2(assets/name,out/'validation'/name)
for name in ['render.png','render-clay.png','side-profile.png','head-side.png','rear-oblique.png','camera.json','diagnostic-cameras.json']:
    (out/'views').mkdir(exist_ok=True);shutil.copy2(assets/name,out/'views'/name)
shutil.copy2(ROOT/'scripts/bishop/profile.json',out/'profile.json')
shutil.copy2(ROOT/'build/bishop-mission/143-viewer-check.log',out/'validation/viewer.json')
shutil.copy2(ROOT/'build/bishop-mission/143-review-check.log',out/'validation/review.txt')
al=json.loads((assets/'original-alignment.json').read_text());scale=al['scale']*300/1254
original=Image.open(assets/'original.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,
    (scale,0,al['x']*3,0,scale,al['y']*3),Image.Resampling.BILINEAR)
ref=np.array(original);mask=(ref[:,:,3]>127)&(ref[:,:,:3].max(2)>12)
regional={}
for name,path in [('before',prior/'render.png'),('after',assets/'render.png')]:
    m=np.array(Image.open(path).convert('RGBA'))[:,:,3]>127
    errors=[]
    for y in range(610,795,2):
        a=np.flatnonzero(mask[y]);b=np.flatnonzero(m[y]);errors.append(abs((a[-1]-a[0])-(b[-1]-b[0]))/2)
    regional[name]={'mean_half_width_error_native_px':float(np.mean(errors)),
                    'max_half_width_error_native_px':float(np.max(errors))}
(out/'regional-geometry.json').write_text(json.dumps({'rows':[610,795,2],'source':'Registered original white, unchanged threshold; half-width diagnostic only, not interior-shape accuracy.','results':regional},indent=2)+'\n')
# Equal framing and crops; these are diagnostic comparisons, not altered refs.
items=[('Original white',original),('Selected white 3',Image.open(assets/'reference.png').convert('RGBA')),
       ('Previous neutral',Image.open(prior/'render-clay.png').convert('RGBA')),
       ('Current neutral',Image.open(assets/'render-clay.png').convert('RGBA'))]
for name,box in [('neutral-collars',(300,365,680,615)),('neutral-body',(180,585,800,1130))]:
    w,h=box[2]-box[0],box[3]-box[1];canvas=Image.new('RGB',(w*4,h+35),'#14181c');draw=ImageDraw.Draw(canvas)
    for i,(label,im) in enumerate(items):
        crop=im.crop(box);canvas.paste(crop,(i*w,35),crop);draw.text((i*w+8,10),label,fill='white')
    canvas.save(out/(name+'.png'))
canvas=Image.new('RGB',(1000,535),'#14181c');draw=ImageDraw.Draw(canvas)
for i,(label,path) in enumerate([('Previous side',prior/'side-profile.png'),('Current side',assets/'side-profile.png')]):
    im=Image.open(path).convert('RGBA').resize((500,500),Image.Resampling.LANCZOS)
    canvas.paste(im,(500*i,35),im);draw.text((500*i+10,10),label,fill='white')
canvas.save(out/'side-comparison.png')
metrics=json.loads((out/'comparison/metrics.json').read_text())
assert metrics['render_sha256']==sha(assets/'render.png')
scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'],'interior':86,'color':83,'texture':77,'lighting':72}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':[75,85],
        'silhouette_measured_other_scores_subjective':True,'phase':'geometry',
        'model_sha256':model_hash,'render_sha256':sha(assets/'render.png'),'neutral_sha256':sha(assets/'render-clay.png'),
        'atlas_sha256':sha(assets/'bishop-boxwood-albedo.png'),'original_and_selected_ious':metrics['images'],
        'shape_complete':False,'full_mission_complete':False,
        'tradeoff':'Shape improves while retained pigment and lighting no longer fit the changed surfaces as well. The full-image mean may fall; this is not claimed as a finished material checkpoint.'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'collected':True,'model_sha256':model_hash,'regional_geometry':regional,'scores':scores},indent=2))

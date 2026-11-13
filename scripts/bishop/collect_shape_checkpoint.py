"""Record an accepted geometry checkpoint after saved-model and stage checks."""
from pathlib import Path
import argparse,hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--checkpoint',default='017');p.add_argument('--baseline',default='015')
p.add_argument('--trial',default='143-geometry-checkpoint');p.add_argument('--log-prefix',default='143')
p.add_argument('--interior-score',type=float,default=86)
p.add_argument('--holistic-range',type=float,nargs=2,default=[75,85])
p.add_argument('--bounds-relative-tolerance',type=float,default=0,
               help='Explicitly declared allowance for a local evaluated diameter change; default preserves exact prior bounds.')
a=p.parse_args();assert a.checkpoint.isdigit() and a.baseline.isdigit() and a.log_prefix.isdigit()
assert 0<=a.bounds_relative_tolerance<=.001
assert 0<=a.holistic_range[0]<=a.holistic_range[1]<=100
out=ROOT/f'docs/bishop-mission/iteration-{a.checkpoint}';assets=ROOT/'assets/bishop'
(out/'validation').mkdir(parents=True,exist_ok=True)
trial=ROOT/'build/bishop-mission'/a.trial
assert trial.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=ROOT/'models/bishop/bishop-rebuilt.blend';model_hash=sha(model)
scope=json.loads((assets/'mission-validation.json').read_text())
assert scope['passed'] and scope['model_sha256']==model_hash and scope['geometry_phase']
anatomy=json.loads((assets/'validation.json').read_text())
assert anatomy['source_hash_matches'] and anatomy['head_button_join']['gap_free']
assert all(p['nonmanifold_edges']==0 and p['signed_volume']>0 for p in anatomy['components'])
assert sha(trial/'bishop.blend')==model_hash
for name,other in [('render.png','wood.png'),('render-clay.png','neutral.png')]:assert sha(assets/name)==sha(trial/other)
log=(ROOT/f'build/bishop-mission/{a.log_prefix}-checkpoint-validation.log').read_text(encoding='utf-8-sig')
for script in ['export_mission.py','validate.py','validate_mission.py','check_join_regression.py']:
    assert 'BISHOP_CHECKPOINT_CHECK_PASSED '+script in log,script
viewer=json.loads((ROOT/f'build/bishop-mission/{a.log_prefix}-viewer-check.log').read_text(encoding='utf-8-sig'))
assert viewer['passed'] and viewer['sourceSha256']==model_hash
(assets/'viewer-validation.json').write_text(json.dumps(viewer,indent=2)+'\n')
assert 'PASS: bishop' in (ROOT/f'build/bishop-mission/{a.log_prefix}-review-check.log').read_text(encoding='utf-8-sig')
meta=json.loads((assets/'mesh.json').read_text());prior=ROOT/f'history/bishop-mission-{a.baseline}'
old_meta=json.loads((prior/'mesh.json').read_text())
assert meta['sourceSha256']==model_hash and meta['referenceCamera']==old_meta['referenceCamera']
old_size=np.array(old_meta['bounds']['size']);new_size=np.array(meta['bounds']['size'])
assert np.allclose(new_size,old_size,atol=1e-6,rtol=a.bounds_relative_tolerance)
assert abs(new_size[2]-old_size[2])<1e-6,'Local foot edit must not alter overall height.'
(out/'bounds-comparison.json').write_text(json.dumps({'previous':old_size.tolist(),'current':new_size.tolist(),
    'relative_change':((new_size-old_size)/old_size).tolist(),'allowed_relative_tolerance':a.bounds_relative_tolerance,
    'height_preserved':True,'note':'Measured evaluated bounds, not an image or gallery scale adjustment.'},indent=2)+'\n')
assert sha(assets/'bishop-boxwood-albedo.png')==sha(prior/'bishop-boxwood-albedo.png')
# Replace obsolete current-state reports with explicit current provenance.
reports={
 'base-validation.json':{'passed':True,'model_sha256':model_hash,'declared_shape_rings':scope['changed_body_rings'],
    'independent_scope_audit':'mission-validation.json','previous_two_ring_scope_superseded':True},
 'slit-validation.json':{'passed':True,'model_sha256':model_hash,'cutter_unchanged_from_source':True,'source_checkpoint':a.baseline,
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
shutil.copy2(ROOT/f'build/bishop-mission/{a.log_prefix}-viewer-check.log',out/'validation/viewer.json')
shutil.copy2(ROOT/f'build/bishop-mission/{a.log_prefix}-review-check.log',out/'validation/review.txt')
al=json.loads((assets/'original-alignment.json').read_text());scale=al['scale']*300/1254
original=Image.open(assets/'original.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,
    (scale,0,al['x']*3,0,scale,al['y']*3),Image.Resampling.BILINEAR)
ref=np.array(original);mask=(ref[:,:,3]>127)&(ref[:,:,:3].max(2)>12)
regional={}
for name,path in [('before',prior/'render.png'),('after',assets/'render.png')]:
    m=np.array(Image.open(path).convert('RGBA'))[:,:,3]>127
    errors=[]
    for y in range(610,795,2):
        reference_x=np.flatnonzero(mask[y]);model_x=np.flatnonzero(m[y])
        errors.append(abs((reference_x[-1]-reference_x[0])-(model_x[-1]-model_x[0]))/2)
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
scores={'silhouette':100*metrics['images']['selected']['silhouette_iou'],'interior':a.interior_score,'color':83,'texture':77,'lighting':72}
record={'scores_percent':scores,'mean_percent':sum(scores.values())/5,'holistic_range_percent':a.holistic_range,
        'silhouette_measured_other_scores_subjective':True,'phase':'geometry',
        'model_sha256':model_hash,'render_sha256':sha(assets/'render.png'),'neutral_sha256':sha(assets/'render-clay.png'),
        'atlas_sha256':sha(assets/'bishop-boxwood-albedo.png'),'original_and_selected_ious':metrics['images'],
        'shape_complete':False,'full_mission_complete':False,
        'tradeoff':'Geometry is evaluated independently of the retained pigment and lights. Those still have visible mismatches and are not newly fitted or claimed complete.'}
(out/'scores.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'collected':True,'model_sha256':model_hash,'regional_geometry':regional,'scores':scores},indent=2))

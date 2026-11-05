from pathlib import Path
import hashlib,json,shutil
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[2];out=root/'docs/bishop-mission/iteration-001';out.mkdir(parents=True,exist_ok=True)
names=['001-boxwood-baseline','002-golden-lighting','003-targeted-reflections','004-fine-relief','005-reflection-balance','006-confined-reflections','007-button-glints']
scores=[[94.8824,78,60,61,42],[94.8785,78,67,62,40],[94.8785,78,70,62,47],[94.8785,78,70,61,52],[94.8785,78,60,61,50],[94.8785,78,65,58,35],[94.8785,78,70,64,54]]
notes=['First actual wood; muted, smooth, misplaced high base reflection.','Golden diffuse color improves; broad reflections obscure grain.','Targeting glints reduces spill, but strong relief scatters highlights.','Finer relief sharpens reflections; finish is still too smooth.','Rejected: reduced saturation washes wood toward pink/tan.','Rejected: narrow area spread normalizes energy upward, blowing out reflections and adding streaks.','Chosen: intermediate relief, warm pigment, two finial glints; still unfinished.']
rows=[]
for name,sc,note in zip(names,scores,notes):
    cfg=json.loads((root/f'scripts/bishop/mission-{name[:3]}.json').read_text());cfg['source']='history/bishop-mission-000/bishop-rebuilt.blend';(out/f'{name[:3]}-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    met=json.loads((root/f'build/bishop-mission/{name}/compare/metrics.json').read_text());rows.append({'trial':name,'scores':dict(zip(['silhouette','interior','color','texture','lighting'],sc)),'mean':sum(sc)/5,'original_white_iou':met['images']['original_white']['silhouette_iou'],'render_sha256':met['render_sha256'],'decision':note})
(out/'trials.json').write_text(json.dumps(rows,indent=2)+'\n')
canvas=Image.new('RGB',(1440,790),'#111418');draw=ImageDraw.Draw(canvas)
for i,(label,path) in enumerate([('Selected white 3',root/'assets/bishop/reference.png')]+[(x,root/f'build/bishop-mission/{x}/wood.png') for x in names]):
    im=Image.open(path).convert('RGBA');im.thumbnail((360,360));x=(i%4)*360;y=(i//4)*395;draw.text((x+12,y+10),label,fill='white');canvas.paste(im,(x,y+35),im)
canvas.save(out/'trials-contact-sheet.png')
for src,name in [('build/bishop-mission/008-baked-checkpoint/bake-validation.json','initial-bake-validation.json'),('build/bishop-mission/009-cut-wood/cut-validation.json','cut-validation.json'),('build/bishop-mission/reflection-landmarks.json','reflection-landmarks.json')]:shutil.copy2(root/src,out/name)
shutil.copy2(root/'build/bishop-mission/011-valid-cap-atlas/bake-validation.json',out/'final-bake-validation.json')
shutil.copy2(root/'build/bishop-mission/010-reproduced/render-comparison.json',out/'reproduced-render-comparison.json')
repro={'source':'history/bishop-mission-000/bishop-rebuilt.blend','source_sha256':hashlib.sha256((root/'history/bishop-mission-000/bishop-rebuilt.blend').read_bytes()).hexdigest(),'material_config':'docs/bishop-mission/iteration-001/007-config.json','commands':['blender --background --python-exit-code 1 --python scripts/bishop/mission_material.py -- docs/bishop-mission/iteration-001/007-config.json','blender --background --python-exit-code 1 --python scripts/bishop/bake_mission.py -- --source build/bishop-mission/007-button-glints/bishop.blend --out build/bishop-mission/reproduced-001'],'accepted_model_sha256':hashlib.sha256((root/'models/bishop/bishop-rebuilt.blend').read_bytes()).hexdigest(),'pigment_sha256':hashlib.sha256((root/'assets/bishop/bishop-boxwood-albedo.png').read_bytes()).hexdigest(),'note':'Texture bake captures pigment only. The corrected bake script also assigns procedural wood to the editable Boolean cut faces.'}
(out/'reproduction.json').write_text(json.dumps(repro,indent=2)+'\n')
metrics=json.loads((out/'metrics.json').read_text());final_scores={'silhouette':metrics['images']['selected']['silhouette_iou']*100,'interior':78,'color':70,'texture':64,'lighting':54}
(out/'scores.json').write_text(json.dumps({'scores_percent':final_scores,'mean_percent':sum(final_scores.values())/5,'holistic_range_percent':[65,75],'original_white_iou':metrics['images']['original_white']['silhouette_iou'],'original_black_iou':metrics['images']['original_black']['silhouette_iou'],'silhouette_is_measured_other_scores_are_visual_estimates':True,'accepted_model_sha256':repro['accepted_model_sha256'],'render_sha256':metrics['render_sha256'],'texture_sha256':repro['pigment_sha256'],'status':'accepted improvement, mission incomplete'},indent=2)+'\n')
for name in ['mission-validation.json','validation.json','viewer-validation.json','join-regression.json','diagnostic-cameras.json']:
    path=root/'assets/bishop'/name
    if path.exists():shutil.copy2(path,out/name)
print('Collected iteration evidence.')

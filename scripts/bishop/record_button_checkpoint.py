"""Record independently projected button boundaries and checkpoint 020 trials."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'docs/bishop-mission/iteration-020';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cp(relative,target):
    dest=out/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/relative,dest)
def rgb(im):
    im=im.convert('RGBA');bg=Image.new('RGB',im.size,'black');bg.paste(im,(0,0),im);return bg
current=ROOT/'models/bishop/bishop-rebuilt.blend'
before=ROOT/'history/bishop-mission-019/bishop-rebuilt.blend'
sources={'before':ROOT/'build/bishop-mission/154-button-audit',
         'after':ROOT/'build/bishop-mission/158-button-surface'}
masks={};boundaries={}
for label,folder in sources.items():
    meta=json.loads((folder/'slit-boundary.json').read_text())
    assert meta['source_sha256']==sha(before if label=='before' else current)
    mask=np.load(folder/'surface-labels.npy')==3;masks[label]=mask
    ys,xs=np.nonzero(mask)
    curves=[{'x':x,'top':int(a[0]),'bottom':int(a[-1])} for x in range(410,580)
            if len(a:=np.flatnonzero(mask[:,x]))]
    boundaries[label]={'source_sha256':meta['source_sha256'],
                      'bounds':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
                      'column_boundaries':curves,'camera_degrees_measured':meta['camera_degrees_measured']}
    (out/'boundaries').mkdir(exist_ok=True)
    np.save(out/f'boundaries/{label}-button-mask.npy',mask[140:305,410:580])
targets=[(440,251),(460,263),(480,270),(491,270),(500,270),(520,265),(540,253)]
landmarks=[]
for x,y in targets:
    row={'x':x,'reference_front_y_estimate':y,'estimated_uncertainty_px':3}
    for label,mask in masks.items():row[label]=int(np.flatnonzero(mask[:,x])[-1])
    landmarks.append(row)
record={'method':'Actual first-hit button surface against the evaluated mesh at the saved camera; independent of pigment, lights and highlights.',
        'boundaries':boundaries,'front_rim_landmarks':landmarks,
        'mean_absolute_error_to_interpreted_front_arc':{label:float(np.mean([abs(r[label]-r['reference_front_y_estimate']) for r in landmarks])) for label in masks},
        'reference_landmark_note':'Manually interpreted selected-white-3 button edge, supported by the blurred original; +/-3 comparison pixels. This is approximate visual evidence, not exact semantic ground truth or a claim of recovered source geometry.'}
(out/'button-surface-evidence.json').write_text(json.dumps(record,indent=2)+'\n')
al=json.loads((ROOT/'assets/bishop/original-alignment.json').read_text());s=al['scale']*300/1254
original=Image.open(ROOT/'assets/bishop/original.png').convert('RGBA').transform((1254,1254),Image.Transform.AFFINE,
          (s,0,al['x']*3,0,s,al['y']*3),Image.Resampling.BILINEAR)
items=[('Original white',original),('White candidate 3',Image.open(ROOT/'assets/bishop/reference.png')),
       ('Current neutral',Image.open(ROOT/'assets/bishop/render-clay.png'))]
sheet=Image.new('RGB',(1200,410),'#15191e');draw=ImageDraw.Draw(sheet)
for i,(label,im) in enumerate(items):
    ar=np.array(rgb(im))
    for name,color in [('before',[255,90,195]),('after',[30,235,235])]:
        m=masks[name];edge=m&~(np.roll(m,1,0)&np.roll(m,-1,0)&np.roll(m,1,1)&np.roll(m,-1,1));ar[edge]=color
    sheet.paste(Image.fromarray(ar).crop((400,135,590,310)).resize((380,350)),(400*i,35))
    draw.text((400*i+10,10),label,fill='white')
draw.text((10,390),'Pink: previous physical boundary. Cyan: current physical boundary.',fill='white')
sheet.save(out/'button-boundaries.png')
cases=[('rim','155-button-rim-1p8','rim-1p8.json','Rejected: cup underside and contact width only 77.45%, below the direct-contact requirement.'),
       ('full-tip','156-button-lens','lens.json','Not chosen: anatomy passes, but the wider tip extension unnecessarily changes the upper-head outline.'),
       ('local-tip','157-button-lens-local','lens-local.json','Chosen: same shallow lens, localized continuous tip adjustment and closer original-head outline.')]
decisions=[]
for label,folder,config,decision in cases:
    base=ROOT/'build/bishop-mission'/folder
    for name in ['wood.png','neutral.png','profile.json','trial-audit.json','scope-validation.json','anatomy-validation.json','geometry-validation.json']:
        if (base/name).exists():cp((base/name).relative_to(ROOT).as_posix(),f'trials/{label}/{name}')
    cp('build/bishop-mission/154-button-audit/'+config,f'trials/{label}/config.json')
    decisions.append({'trial':folder,'decision':decision})
    for name in ['views/head-side.png','studio/head.png','studio/studio.json','geometry/geometry-rows.json']:
        if (base/name).exists():cp((base/name).relative_to(ROOT).as_posix(),f'trials/{label}/{name}')
cp('build/bishop-mission/155-trial-validation.log','trials/rim/failed-anatomy-check.txt')
cp('build/bishop-mission/158-button-checkpoint/trial-audit.json','final-trial-audit.json')
(out/'trials/decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
sheet=Image.new('RGB',(1200,620),'#15191e');draw=ImageDraw.Draw(sheet)
for i,(label,path) in enumerate([('Previous button','history/bishop-mission-019/head-side.png'),('Current button','assets/bishop/head-side.png')]):
    sheet.paste(rgb(Image.open(ROOT/path)).resize((600,600)),(i*600,20));draw.text((i*600+10,4),label,fill='white')
sheet.save(out/'head-side-comparison.png')
print(json.dumps({'recorded':True,'button_bounds':{k:v['bounds'] for k,v in boundaries.items()},
                  'arc_errors':record['mean_absolute_error_to_interpreted_front_arc']},indent=2))

"""Record checkpoint 019's small foot correction and rejected bulk studies."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'docs/bishop-mission/iteration-019'
out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cp(relative,destination):
    target=out/destination;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/relative,target)
def image(relative):
    im=Image.open(ROOT/relative).convert('RGBA')
    bg=Image.new('RGB',im.size,'black');bg.paste(im,(0,0),im);return bg
trials=[('moderate','150-collars-moderate','150-collar-sections/moderate.json',
         'Not accepted. Compressing all collar rolls makes the lip too sharp without resolving the observed swollen interior forms.'),
        ('flatter','150-collars-flatter','150-collar-sections/flatter.json',
         'Rejected. Stronger compression makes a thin knife edge unlike the reference rolled lip.'),
        ('shelf','151-collar-shelf','150-collar-sections/shelf.json',
         'Not accepted. Flatter inner deck changes the level profile but fixed-view improvement is not convincing.'),
        ('foot','152-foot-wall','152-foot-section/trial.json',
         'Accepted after final rebuild and checks. A small, straighter-foot-wall correction only; broader shape mismatch remains.')]
records=[]
for name,folder,config,decision in trials:
    base=ROOT/'build/bishop-mission'/folder
    audit=json.loads((base/'trial-audit.json').read_text())
    assert audit['source_unchanged'] and audit['saved_and_reopened']
    assert audit['model_sha256']==sha(base/'bishop.blend')
    cp('build/bishop-mission/'+config,f'trials/{name}/config.json')
    for f in ['neutral.png','wood.png','trial-audit.json']:
        cp(f'build/bishop-mission/{folder}/{f}',f'trials/{name}/{f}')
    records.append({'name':name,'decision':decision,'trial_model_sha256':audit['model_sha256'],
                    'source_sha256':audit['config']['source_sha256']})
cp('build/bishop-mission/152-foot-section/metrics/metrics.json','trials/foot/metrics.json')
cp('build/bishop-mission/150-collar-sections/moderate-comparison/metrics.json','trials/moderate/metrics.json')
for folder,destination in [('148-internal-audit','studio/before'),('151-collar-shelf/studio','studio/shelf'),
                            ('152-foot-wall/studio','studio/foot')]:
    for file in (ROOT/'build/bishop-mission'/folder).glob('*'):
        if file.suffix in ['.png','.json']:cp(file.relative_to(ROOT).as_posix(),destination+'/'+file.name)
cp('build/bishop-mission/153-foot-wall-checkpoint/trial-audit.json','final-trial-audit.json')
(out/'trials/decisions.json').write_text(json.dumps(records,indent=2)+'\n')
panels=[('Original white','build/bishop-mission/149-owner-recording/registered-original.png'),
        ('Selected white 3','assets/bishop/reference.png'),('Checkpoint 018','history/bishop-mission-018/render-clay.png'),
        ('Checkpoint 019','assets/bishop/render-clay.png')]
for name,box in [('foot-detail',(225,920,755,1120)),('head-collars-detail',(290,135,690,630))]:
    w,h=box[2]-box[0],box[3]-box[1]
    sheet=Image.new('RGB',(w*len(panels),h+35),'#15191e');draw=ImageDraw.Draw(sheet)
    for i,(label,relative) in enumerate(panels):
        sheet.paste(image(relative).crop(box),(w*i,35));draw.text((w*i+10,10),label,fill='white')
    sheet.save(out/(name+'.png'))
# Show only the artwork area from the owner's recording, excluding browser
# chrome, unrelated tabs and bookmarks. The complete recording is not copied.
recording=ROOT/'build/bishop-mission/149-owner-recording'
crop=(680,425,1060,1040);w,h=crop[2]-crop[0],crop[3]-crop[1]
sheet=Image.new('RGB',(w*2,h+35),'#15191e');draw=ImageDraw.Draw(sheet)
for i,(frame,label) in enumerate([(107,'Owner recording: reference'),(131,'Owner recording: current neutral')]):
    sheet.paste(Image.open(recording/f'frame-{frame:05d}.png').crop(crop),(w*i,35))
    draw.text((w*i+8,10),label,fill='white')
sheet.save(out/'owner-recording-detail.png')
metadata=json.loads((recording/'recording.json').read_text())
video=Path(metadata['source'])
(out/'owner-recording.json').write_text(json.dumps({'source_filename':video.name,
    'source_sha256':sha(video),'fps':metadata['fps'],'frame_count':metadata['frame_count'],
    'comparison_frames':[107,131],'artwork_crop':crop,'browser_chrome_excluded':True,
    'finding':'White candidate 3 versus current neutral overlay. The inflated appearance is visible; the overall exterior is not uniformly larger. Prior interior confidence was too high.'},indent=2)+'\n')
# Width measurements keep original registration and do not stand in for a
# surface-curvature or full visual-match assessment.
stats={}
for label,relative in [('original','build/bishop-mission/149-owner-recording/registered-original.png'),
                        ('selected','assets/bishop/reference.png'),('model018','history/bishop-mission-018/render.png')]:
    arr=np.array(Image.open(ROOT/relative).convert('RGBA'));mask=arr[:,:,3]>127
    if label!='model018':mask&=arr[:,:,:3].max(2)>12
    for region,(y0,y1) in {'head_upper':[240,350],'base':[800,1115]}.items():
        widths=[int(x[-1]-x[0]+1) for row in mask[y0:y1] if len(x:=np.flatnonzero(row))]
        stats.setdefault(label,{})[region+'_maximum_width_px']=max(widths)
(out/'extent-audit.json').write_text(json.dumps({'widths':stats,'note':'Image-row exterior extents, not anatomical segmentation. No scale, translation, camera or reference change. These measurements explain why a global shrink is not justified by the recording.'},indent=2)+'\n')
print('Recorded foot checkpoint evidence and rejected collar experiments.')

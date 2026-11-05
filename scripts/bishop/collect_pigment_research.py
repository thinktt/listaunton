"""Preserve concise rejected-trial evidence without publishing failed models."""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
trials=[
 ('058-regularized-pigment',[83,75,72,68],'Broad smoothing loses front contrast; old fine residue retains the rear patch.'),
 ('059-folded-pigment',[83,84,72,73],'Wrapping a front strip also wraps its baked shading into false horizontal bands.'),
 ('060-grain-continuation',[83,84,73,73],'Separating sampled fine grain still leaves the broad dark bands and patch transition.'),
 ('061-generated-grain',[83,84,74,73],'Fresh inferred grain is cleaner on unseen wood, but the front-to-rear color patch remains and an edge stripe appears.'),
 ('062-continuous-generated-grain',[83,80,75,70],'Broad regularization plus new grain smooths the rear transition somewhat, but weakens collar grooves and front tonal structure.'),
]
records=[];front=[('Selected white 3',ROOT/'assets/bishop/reference.png'),('Accepted 007',ROOT/'history/bishop-mission-007/render.png')]
rear=[('Accepted 007',ROOT/'history/bishop-mission-007/rear-oblique.png')]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,subjective,reason in trials:
    source=ROOT/'build/bishop-mission'/name;dest=out/name;dest.mkdir(exist_ok=True)
    metrics=json.loads((source/'comparison/metrics.json').read_text())
    silhouette=metrics['images']['selected']['silhouette_iou']*100
    scores=dict(zip(['silhouette','interior','color','texture','lighting'],[silhouette,*subjective]))
    scores['mean']=sum(scores.values())/5
    for rel in ['regularization.json','continuation.json','trial-validation.json','statistics.json','comparison/metrics.json','atlas-comparison.png','comparison/base.png','comparison/head.png']:
        path=source/rel
        if path.exists():shutil.copy2(path,dest/path.name)
    record={'trial':name,'decision':'rejected','reason':reason,'scores':scores,'holistic_fixed_view_range': '70–80%' if name.startswith(('058','062')) else '75–85%',
      'model_sha256':sha(source/'bishop.blend'),'render_sha256':sha(source/'wood.png'),'atlas_sha256':sha(source/'albedo.png'),
      'metrics':metrics['images'],'samples':96,'fixed_sampling':True,'rear_diagnostic_samples':24}
    (dest/'assessment.json').write_text(json.dumps(record,indent=2)+'\n');records.append(record)
    front.append((name[:3],source/'wood.png'));rear.append((name[:3],source/'rear-oblique.png'))
def montage(entries,path,crop,size):
    width,height=size;im=Image.new('RGB',(width*len(entries),height+36),'#171b21');d=ImageDraw.Draw(im)
    for i,(name,p) in enumerate(entries):
        source=Image.open(p).convert('RGB')
        if crop:source=source.crop(crop)
        source.thumbnail((width,height),Image.Resampling.LANCZOS)
        im.paste(source,(i*width+(width-source.width)//2,36+(height-source.height)//2));d.text((i*width+9,12),name,fill='white')
    im.save(path)
montage(front,out/'front-trials.png',(180,140,795,1140),(230,375))
montage(rear,out/'rear-trials.png',(225,75,535,700),(250,505))
diagnostics=ROOT/'build/bishop-mission/diagnostics-058';diag_out=out/'material-isolation';diag_out.mkdir(exist_ok=True)
for p in diagnostics.iterdir():
    if p.suffix in ['.png','.json']:shutil.copy2(p,diag_out/p.name)
manifest={'status':'Rejected experiments; accepted model and public pages remain unchanged by this collector.',
 'baseline':'history/bishop-mission-007/bishop-rebuilt.blend','baseline_sha256':sha(ROOT/'history/bishop-mission-007/bishop-rebuilt.blend'),
 'source_of_truth':'Original Lichess white bishop; selected ungraded white candidate 3 for detail.',
 'references_unchanged':True,'scores_note':'Silhouette is measured; other scores are subjective. Diagnostic views inform usability. RGB loss is not a fidelity score.',
 'trials':records,
 'conclusion':'The remaining boundary is in pigment rather than bump or geometry. Protecting projected color or retaining its fine residual preserves the artifact; wrapping whole donor strips introduces dark bands. Smoothing those tones weakens important front contrast. Future work must jointly improve physical illumination/shape and pigment, rather than repeating a hidden-only fill.'}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'out':a.out,'trials':len(records),'status':'rejected evidence collected'},indent=2))

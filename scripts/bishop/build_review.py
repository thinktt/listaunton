"""Build the bishop checkpoint workspace without changing other pieces' pages."""
from pathlib import Path
import argparse
import hashlib
import json
root=Path(__file__).resolve().parents[2]
data=json.loads((root/'assets/candidates/alignment.json').read_text(encoding='utf-8'))
parser=argparse.ArgumentParser(description=__doc__)
args=parser.parse_args()
template=(root/'scripts/bishop/review-template.html').read_text(encoding='utf-8')
profile=json.loads((root/'scripts/bishop/profile.json').read_text(encoding='utf-8'))
side_link=''
if profile.get('side_refit'):
    lineup=Path(profile['side_refit']['config']).parent/'frozen-lineup.png'
    if (root/lineup).is_file():
        side_link=f' · <a href="{lineup.as_posix()}" target="_blank" rel="noopener">Side height comparison</a>'
template=template.replace('__SIDE_PROPORTIONS__',side_link)
# Model pages activate automatically when their checked standalone viewer exists.
for piece,images in data['pieces'].items():
    if piece != 'bishop':
        continue
    page=template
    model_page=f'{piece}-model.html'
    model={'page':model_page} if model_page and (root/model_page).is_file() else None
    reconstruction=piece=='bishop' and model is not None
    initial_tab='model' if reconstruction or (piece=='king' and model) else 'candidates'
    if reconstruction:
        # Includes the rendered checkpoint and the viewer code, not just the mesh.
        model['revision']=hashlib.sha256((root/model_page).read_bytes()).hexdigest()[:16]
    tabs=[('model','Reference overlay'),('rotate','Rotate model'),('candidates','Reference candidates')] if reconstruction else [('candidates','Reference candidates'),('model','Reconstruction' if initial_tab=='model' else 'Model')]
    review_tabs='\n'.join(f'<button id="tab-{name}" type="button" role="tab" aria-selected="{str(name==initial_tab).lower()}" aria-controls="panel-{name if name!="rotate" else "model"}" tabindex="{0 if name==initial_tab else -1}">{label}</button>' for name,label in tabs)
    projection_page=f'{piece}-projections.html'
    projections={'page':projection_page} if (root/projection_page).is_file() else None
    extra_tab='<button id="tab-projections" type="button" role="tab" aria-selected="false" aria-controls="panel-projections" tabindex="-1">Projection variants</button>' if projections else ''
    extra_panel=f'<section id="panel-projections" role="tabpanel" aria-labelledby="tab-projections" hidden><iframe id="projections-frame" title="{piece.title()} projection variants" sandbox="allow-scripts allow-downloads"></iframe></section>' if projections else ''
    nav=' '.join(f'<a href="{p}-review.html"'+(' aria-current="page"' if p==piece else '')+f'>{p.title()}</a>' for p in data['pieces'])
    def options(selected):
        groups=[('Originals',[i for i in images if i['id'] in ('black','white')]),('Black enlargements',[i for i in images if i['id'].startswith('candidate-')]),('White enlargements',[i for i in images if i['id'].startswith('white-candidate-')])]
        return ''.join('<optgroup label="'+label+'">'+''.join(f'<option value="{v["id"]}"'+(' selected' if v['id']==selected else '')+f'>{v["label"]}</option>' for v in entries)+'</optgroup>' for label,entries in groups)
    config=dict(piece=piece.title(),images=images,viewPadding=5 if piece=='king' else 0,model=model,projections=projections)
    if initial_tab!='candidates':
        config['initialTab']=initial_tab
    if reconstruction:
        config['reconstructionWorkspace']=True
    for key,value in {'__REVIEW_TABS__':review_tabs,'__CANDIDATES_HIDDEN__':' hidden' if initial_tab=='model' else '', '__MODEL_HIDDEN__':'' if initial_tab=='model' else ' hidden','__EMPTY_HIDDEN__':' hidden' if initial_tab=='model' else '', '__EXTRA_TAB__':extra_tab,'__EXTRA_PANEL__':extra_panel,'__PIECE__':piece.title(),'__LOWER_PIECE__':piece,'__NAV__':nav,'__OPTIONS_A__':options('black'),'__OPTIONS_B__':options(images[2]['id']),'__FIRST_A__':images[0]['file'],'__FIRST_B__':images[2]['file'],'__DATA__':json.dumps(config,separators=(',',':')).replace('<','\\u003c')}.items():page=page.replace(key,value)
    (root/f'{piece}-review.html').write_text(page,encoding='utf-8',newline='\n')
print('Built bishop reconstruction workspace.')

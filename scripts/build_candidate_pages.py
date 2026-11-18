"""Build five reference/model review pages; never writes the queen review."""
from pathlib import Path
import json,argparse,subprocess,sys,hashlib
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'assets/candidates/alignment.json').read_text(encoding='utf-8'))
template=(root/'scripts/candidate-template.html').read_text(encoding='utf-8')
parser=argparse.ArgumentParser();parser.add_argument('--piece',choices=list(data['pieces']));args=parser.parse_args()
# Model pages activate automatically when their checked standalone viewer exists.
for piece,images in data['pieces'].items():
    if args.piece and piece!=args.piece:continue
    if piece=='bishop':
        subprocess.run([sys.executable,str(root/'scripts/bishop/build_review.py')],check=True)
        continue
    page=template
    model_page=f'{piece}-model.html'
    model={'page':model_page} if model_page and (root/model_page).is_file() else None
    if piece == 'pawn' and model:
        revision = hashlib.sha256((root/model_page).read_bytes()).hexdigest()[:12]
        model['page'] = f'{model_page}?v={revision}'
    projection_page=f'{piece}-projections.html'
    projections={'page':projection_page} if (root/projection_page).is_file() else None
    extra_tab='<button id="tab-projections" type="button" role="tab" aria-selected="false" aria-controls="panel-projections" tabindex="-1">Projection variants</button>' if projections else ''
    extra_panel=f'<section id="panel-projections" role="tabpanel" aria-labelledby="tab-projections" hidden><iframe id="projections-frame" title="{piece.title()} projection variants" sandbox="allow-scripts allow-downloads"></iframe></section>' if projections else ''
    nav=' '.join(f'<a href="{p}-review.html"'+(' aria-current="page"' if p==piece else '')+f'>{p.title()}</a>' for p in data['pieces'])
    def options(selected):
        groups=[('Originals',[i for i in images if i['id'] in ('black','white')]),('Black enlargements',[i for i in images if i['id'].startswith('candidate-')]),('White enlargements',[i for i in images if i['id'].startswith('white-candidate-')])]
        return ''.join('<optgroup label="'+label+'">'+''.join(f'<option value="{v["id"]}"'+(' selected' if v['id']==selected else '')+f'>{v["label"]}</option>' for v in entries)+'</optgroup>' for label,entries in groups)
    for key,value in {'__EXTRA_TAB__':extra_tab,'__EXTRA_PANEL__':extra_panel,'__PIECE__':piece.title(),'__LOWER_PIECE__':piece,'__NAV__':nav,'__OPTIONS_A__':options('black'),'__OPTIONS_B__':options(images[2]['id']),'__FIRST_A__':images[0]['file'],'__FIRST_B__':images[2]['file'],'__DATA__':json.dumps(dict(piece=piece.title(),images=images,viewPadding=5 if piece=='king' else 0,model=model,projections=projections,**({"initialTab":"model"} if piece in ("king","pawn") and model else {})),separators=(',',':')).replace('<','\\u003c')}.items():page=page.replace(key,value)
    if piece in ('king','pawn') and model:
        page=page.replace('id="tab-candidates" type="button" role="tab" aria-selected="true" aria-controls="panel-candidates" tabindex="0"','id="tab-candidates" type="button" role="tab" aria-selected="false" aria-controls="panel-candidates" tabindex="-1"')
        page=page.replace('id="tab-model" type="button" role="tab" aria-selected="false" aria-controls="panel-model" tabindex="-1">Model','id="tab-model" type="button" role="tab" aria-selected="true" aria-controls="panel-model" tabindex="0">Reconstruction')
        page=page.replace('id="panel-candidates" role="tabpanel" aria-labelledby="tab-candidates">','id="panel-candidates" role="tabpanel" aria-labelledby="tab-candidates" hidden>')
        page=page.replace('id="panel-model" role="tabpanel" aria-labelledby="tab-model" hidden>','id="panel-model" role="tabpanel" aria-labelledby="tab-model">')
        page=page.replace('id="model-empty" class="model-empty">','id="model-empty" class="model-empty" hidden>')
    (root/f'{piece}-review.html').write_text(page,encoding='utf-8')
print('Built five reference/model review pages.')

"""Build five reference/model review pages; never writes the queen review."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'assets/candidates/alignment.json').read_text(encoding='utf-8'))
template=(root/'scripts/candidate-template.html').read_text(encoding='utf-8')
# Add a model here when its standalone comparison page is available.
model_pages={'king':'king-model.html'}
for piece,images in data['pieces'].items():
    page=template
    model_page=model_pages.get(piece)
    model={'page':model_page} if model_page and (root/model_page).is_file() else None
    nav=' '.join(f'<a href="{p}-review.html"'+(' aria-current="page"' if p==piece else '')+f'>{p.title()}</a>' for p in data['pieces'])
    def options(selected):
        groups=[('Originals',[i for i in images if i['id'] in ('black','white')]),('Black enlargements',[i for i in images if i['id'].startswith('candidate-')]),('White enlargements',[i for i in images if i['id'].startswith('white-candidate-')])]
        return ''.join('<optgroup label="'+label+'">'+''.join(f'<option value="{v["id"]}"'+(' selected' if v['id']==selected else '')+f'>{v["label"]}</option>' for v in entries)+'</optgroup>' for label,entries in groups)
    for key,value in {'__PIECE__':piece.title(),'__LOWER_PIECE__':piece,'__NAV__':nav,'__OPTIONS_A__':options('black'),'__OPTIONS_B__':options(images[2]['id']),'__FIRST_A__':images[0]['file'],'__FIRST_B__':images[2]['file'],'__DATA__':json.dumps(dict(piece=piece.title(),images=images,viewPadding=5 if piece=='king' else 0,model=model),separators=(',',':')).replace('<','\\u003c')}.items():page=page.replace(key,value)
    (root/f'{piece}-review.html').write_text(page,encoding='utf-8')
print('Built five reference/model review pages.')

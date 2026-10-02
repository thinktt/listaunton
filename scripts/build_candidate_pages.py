"""Build five reference comparison pages; never writes the queen review."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'assets/candidates/alignment.json').read_text(encoding='utf-8'))
template=(root/'scripts/candidate-template.html').read_text(encoding='utf-8')
for piece,images in data['pieces'].items():
    page=template
    nav=' '.join(f'<a href="{p}-review.html"'+(' aria-current="page"' if p==piece else '')+f'>{p.title()}</a>' for p in data['pieces'])
    def options(selected):
        groups=[('Originals',images[:2]),('Black enlargements',images[2:5]),('White enlargements',images[5:])]
        return ''.join('<optgroup label="'+label+'">'+''.join(f'<option value="{v["id"]}"'+(' selected' if v['id']==selected else '')+f'>{v["label"]}</option>' for v in entries)+'</optgroup>' for label,entries in groups)
    for key,value in {'__PIECE__':piece.title(),'__NAV__':nav,'__OPTIONS_A__':options('black'),'__OPTIONS_B__':options('candidate-1'),'__FIRST_A__':images[0]['file'],'__FIRST_B__':images[2]['file'],'__DATA__':json.dumps(dict(piece=piece.title(),images=images,viewPadding=5 if piece=='king' else 0),separators=(',',':')).replace('<','\\u003c')}.items():page=page.replace(key,value)
    (root/f'{piece}-review.html').write_text(page,encoding='utf-8')
print('Built five comparison pages.')

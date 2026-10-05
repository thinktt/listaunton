"""Build whole-set reference comparison and the side-view gallery."""
from pathlib import Path
from html import escape
import hashlib,json
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'assets/candidates/alignment.json').read_text(encoding='utf-8'))['pieces']
q=json.loads((root/'assets/queen/original-reference-alignment.json').read_text(encoding='utf-8'))
data['queen']=[{'id':'queen-reference','label':'Selected queen reference','file':q['target'],'scale':q['canvas_size'][0]/q['scale']/300,'x':-q['offset_x']/q['scale']/3,'y':-q['offset_y']/q['scale']/3}]
manifest=json.loads((root/'assets/side-views/manifest.json').read_text(encoding='utf-8'))
sides=manifest['pieces']
scales=json.loads((root/manifest['scale']).read_text(encoding='utf-8'))
measurements={item['piece']:item for item in scales['pieces']}
assert [item['piece'] for item in sides]==['king','queen','rook','bishop','knight','pawn']
cards=[]
for item in sides:
    for key in ['file','generation','review','source_file','source_generation']:
        path=(root/item[key]).resolve()
        assert path.is_relative_to(root) and path.is_file(),item[key]
    assert hashlib.sha256((root/item['file']).read_bytes()).hexdigest()==item['sha256'],item['piece']+' side image changed'
    row=measurements[item['piece']]
    assert row['cutout']['file']==item['file'] and row['cutout']['sha256']==item['sha256'], 'Rerun measure_side_views.py'
    assert hashlib.sha256((root/row['original']['file']).read_bytes()).hexdigest()==row['original']['sha256']
    display=row['display']
    style=f'width:{display["image_width_px"]:.6f}px;left:calc(50% + {display["left_from_center_px"]:.6f}px);top:{display["top_px"]:.6f}px'
    name=escape(item['name']);image=escape(item['file'],quote=True)
    ratio=f'{row["base_ratio_to_king"]:.0%}'
    cards.append(f'''<article class="card side-card" data-side-piece="{item["piece"]}">
<h2>{name}</h2><span class="side-ratio">Base: {ratio} of king</span>
<a class="side-image" href="{image}" target="_blank" rel="noopener" aria-label="Open full-size {name.lower()} cutout">
<img src="{image}" alt="Generated {name.lower()} side view based on the {item["referenceColor"]} reference" width="{item["width"]}" height="{item["height"]}" style="{style}" loading="lazy" decoding="async"></a>
<div class="side-links"><a href="{escape(item["review"],quote=True)}">Review {name.lower()}</a><a href="{image}" target="_blank" rel="noopener">Full-size cutout</a><a href="{escape(item["source_file"],quote=True)}" target="_blank" rel="noopener">Before removal</a><a href="{escape(item["generation"],quote=True)}" target="_blank" rel="noopener">Prompt &amp; sources</a></div></article>''')
template=(root/'scripts/set-comparison-template.html').read_text(encoding='utf-8')
output=template.replace('__DATA__',json.dumps(data,separators=(',',':')).replace('<','\\u003c')).replace('__SIDE_CARDS__','\n'.join(cards))
assert '__SIDE_CARDS__' not in output and '__DATA__' not in output
(root/'set-comparison.html').write_text(output,encoding='utf-8')
print('Built whole-set comparison and six side views at one king-relative scale.')

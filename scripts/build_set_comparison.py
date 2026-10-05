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
slider_data={'min':50,'max':150,'ground':670,'stageHeight':672,'minSlotWidth':320,'pieces':[]}
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
    top=display['top_px']+slider_data['ground']-scales['display']['ground_y_px']
    origin_x=-display['left_from_center_px']
    origin_y=row['cutout']['ground_y_px']*display['scale']
    style=f'width:{display["image_width_px"]:.6f}px;left:calc(50% + {display["left_from_center_px"]:.6f}px);top:{top:.6f}px;transform-origin:{origin_x:.6f}px {origin_y:.6f}px'
    slider_data['pieces'].append({'piece':item['piece'],'name':item['name'],'height':display['visible_height_px']})
    name=escape(item['name']);image=escape(item['file'],quote=True)
    ratio=f'{row["height_check"]["height_ratio_to_king"]:.1%}'
    # Load the whole set even while its tab is hidden or cards are outside the scroll viewport.
    cards.append(f'''<article class="card side-card" data-side-piece="{item["piece"]}">
<h2>{name}</h2><span class="side-ratio" id="side-ratio-{item['piece']}">Height: {ratio} of king</span>
<a class="side-image" href="{image}" target="_blank" rel="noopener" aria-label="Open full-size {name.lower()} cutout">
<img id="side-picture-{item['piece']}" src="{image}" alt="Generated {name.lower()} side view based on the {item["referenceColor"]} reference" width="{item["width"]}" height="{item["height"]}" style="{style}" loading="eager" decoding="auto"></a>
<div class="side-scale-controls"><div class="side-scale-label"><label for="side-scale-{item['piece']}">Scale</label><output id="side-scale-value-{item['piece']}" for="side-scale-{item['piece']}">100%</output><button id="side-reset-{item['piece']}" type="button" aria-label="Reset {name.lower()} scale to model estimate">Reset</button></div><input id="side-scale-{item['piece']}" type="range" min="50" max="150" step="1" value="100" aria-label="{name} scale" aria-valuetext="100% of model estimate"></div>
<div class="side-links"><a href="{escape(item["review"],quote=True)}">Review {name.lower()}</a><a href="{image}" target="_blank" rel="noopener">Full-size cutout</a><a href="{escape(item["source_file"],quote=True)}" target="_blank" rel="noopener">Before removal</a><a href="{escape(item["generation"],quote=True)}" target="_blank" rel="noopener">Prompt &amp; sources</a></div></article>''')
template=(root/'scripts/set-comparison-template.html').read_text(encoding='utf-8')
output=template.replace('__DATA__',json.dumps(data,separators=(',',':')).replace('<','\\u003c')).replace('__SIDE_CARDS__','\n'.join(cards))
output=output.replace('__SIDE_SCALE_DATA__',json.dumps(slider_data,separators=(',',':')))
assert '__SIDE_CARDS__' not in output and '__DATA__' not in output and '__SIDE_SCALE_DATA__' not in output
(root/'set-comparison.html').write_text(output,encoding='utf-8')
print('Built whole-set comparison and six side views at one king-relative scale.')

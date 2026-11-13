"""Build whole-set reference, generated side-view and current-model comparisons."""
from pathlib import Path
from html import escape
import hashlib,json
from png_profile_bounds import profile_bounds
from board_comparison_data import build_board_data
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'assets/candidates/alignment.json').read_text(encoding='utf-8'))['pieces']
q=json.loads((root/'assets/queen/original-reference-alignment.json').read_text(encoding='utf-8'))
data['queen']=[{'id':'queen-reference','label':'Selected queen reference','file':q['target'],'scale':q['canvas_size'][0]/q['scale']/300,'x':-q['offset_x']/q['scale']/3,'y':-q['offset_y']/q['scale']/3}]
manifest=json.loads((root/'assets/side-views/manifest.json').read_text(encoding='utf-8'))
sides=manifest['pieces']
scales=json.loads((root/manifest['scale']).read_text(encoding='utf-8'))
measurements={item['piece']:item for item in scales['pieces']}
defaults=json.loads((root/'assets/side-views/defaults.json').read_text(encoding='utf-8'))
assert len(defaults['order'])==6 and set(defaults['order'])=={item['piece'] for item in sides}
assert set(defaults['scales'])==set(defaults['order'])
assert all(type(value) is int and 50<=value<=150 for value in defaults['scales'].values())
slider_data={'min':50,'max':150,'ground':670,'stageHeight':672,'minSlotWidth':320,
             'defaultsRevision':defaults['revision'],'defaultOrder':defaults['order'],'pieces':[]}
assert [item['piece'] for item in sides]==['king','queen','rook','bishop','knight','pawn']
cards={}
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
    default_scale=defaults['scales'][item['piece']]
    style=f'width:{display["image_width_px"]:.6f}px;left:calc(50% + {display["left_from_center_px"]:.6f}px);top:{top:.6f}px;transform-origin:{origin_x:.6f}px {origin_y:.6f}px;transform:scale({default_scale/100})'
    slider_data['pieces'].append({'piece':item['piece'],'name':item['name'],'height':display['visible_height_px'],'defaultScale':default_scale})
    name=escape(item['name']);image=escape(item['file'],quote=True)
    ratio=f'{row["height_check"]["height_ratio_to_king"]*default_scale/defaults["scales"]["king"]:.1%}'
    # Load the whole set even while its tab is hidden or cards are outside the scroll viewport.
    cards[item['piece']]=f'''<article id="side-card-{item['piece']}" class="card side-card" data-side-piece="{item["piece"]}">
<div class="side-heading"><button id="side-left-{item['piece']}" type="button" aria-label="Move {name.lower()} left">←</button><h2>{name}</h2><button id="side-right-{item['piece']}" type="button" aria-label="Move {name.lower()} right">→</button></div><span class="side-ratio" id="side-ratio-{item['piece']}">Height: {ratio} of king</span>
<button id="side-drag-{item['piece']}" class="side-image" type="button" aria-label="Move {name.lower()}: drag sideways or use left and right arrow keys" title="Drag sideways to reorder">
<img id="side-picture-{item['piece']}" src="{image}" alt="Generated {name.lower()} side view based on the {item["referenceColor"]} reference" width="{item["width"]}" height="{item["height"]}" style="{style}" loading="eager" decoding="auto" draggable="false"></button>
<div class="side-scale-controls"><div class="side-scale-label"><label for="side-scale-{item['piece']}">Scale</label><output id="side-scale-value-{item['piece']}" for="side-scale-{item['piece']}">{default_scale}%</output><button id="side-reset-{item['piece']}" type="button" aria-label="Reset {name.lower()} scale to chosen default">Reset</button></div><input id="side-scale-{item['piece']}" type="range" min="50" max="150" step="1" value="{default_scale}" aria-label="{name} scale" aria-valuetext="{default_scale}% of model estimate"></div>
<div class="side-links"><a href="{escape(item["review"],quote=True)}">Review {name.lower()}</a><a href="{image}" target="_blank" rel="noopener">Full-size cutout</a><a href="{escape(item["source_file"],quote=True)}" target="_blank" rel="noopener">Before removal</a><a href="{escape(item["generation"],quote=True)}" target="_blank" rel="noopener">Prompt &amp; sources</a></div></article>'''
template=(root/'scripts/set-comparison-template.html').read_text(encoding='utf-8')
profile_files={'king':'assets/king/profile.png','queen':'assets/queen/queen-wood-profile.png',
               'bishop':'assets/bishop/side-profile.png','knight':'assets/knight/guide-render.png',
               'rook':'assets/rook/profile.png','pawn':'assets/pawn/profile.png'}
profiles={piece:{'file':file,'version':hashlib.sha256((root/file).read_bytes()).hexdigest()[:16],
                 **profile_bounds(root/file)} for piece,file in profile_files.items()}
output=template.replace('__DATA__',json.dumps(data,separators=(',',':')).replace('<','\\u003c')).replace('__SIDE_CARDS__','\n'.join(cards[piece] for piece in defaults['order']))
output=output.replace('__SIDE_SCALE_DATA__',json.dumps(slider_data,separators=(',',':')))
output=output.replace('__MODEL_PROFILE_DATA__',json.dumps(profiles,separators=(',',':')))
output=output.replace('__SIDE_ORDER_RUNTIME__',(root/'scripts/side-order-runtime.js').read_text(encoding='utf-8'))
output=output.replace('__MODEL_LINEUP_RUNTIME__',(root/'scripts/model-lineup-runtime.js').read_text(encoding='utf-8'))
output=output.replace('__BOARD_DATA__',json.dumps(build_board_data(root),separators=(',',':')))
output=output.replace('__BOARD_RUNTIME__',(root/'scripts/board-comparison-runtime.js').read_text(encoding='utf-8'))
assert all(token not in output for token in ['__SIDE_CARDS__','__DATA__','__SIDE_SCALE_DATA__','__MODEL_PROFILE_DATA__','__SIDE_ORDER_RUNTIME__','__MODEL_LINEUP_RUNTIME__','__BOARD_DATA__','__BOARD_RUNTIME__'])
(root/'set-comparison.html').write_text(output,encoding='utf-8')
print('Built the whole-set reference, side-view, model and board comparisons.')

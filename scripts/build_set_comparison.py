"""Build the six-piece contact sheet from existing reference placements."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'assets/candidates/alignment.json').read_text())['pieces']
q=json.loads((root/'assets/queen/original-reference-alignment.json').read_text())
data['queen']=[{'id':'queen-reference','label':'Selected queen reference','file':q['target'],'scale':q['canvas_size'][0]/q['scale']/300,'x':-q['offset_x']/q['scale']/3,'y':-q['offset_y']/q['scale']/3}]
template=(root/'scripts/set-comparison-template.html').read_text()
(root/'set-comparison.html').write_text(template.replace('__DATA__',json.dumps(data,separators=(',',':')).replace('<','\\u003c')))

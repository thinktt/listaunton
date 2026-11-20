from pathlib import Path
import json
from PIL import Image,ImageOps
from cheek_review import patch
D=Path(__file__).resolve().parent
m={}
for label in ['parent','A']:
 m[label]={}
 for flank in ['near','far']:
  im=Image.open(D/f'wood-{label}'/f'{flank}.png').convert('RGBA')
  if flank=='far':im=ImageOps.mirror(im)
  m[label][flank]=patch(im,(325,220,365,245))
(D/'paired-cheek.json').write_text(json.dumps({'aligned_flank_rect':[325,220,365,245],'measurements':m},indent=2)+'\n')
print(m)

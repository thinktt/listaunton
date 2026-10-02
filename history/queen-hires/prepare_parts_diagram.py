from pathlib import Path
from io import BytesIO
import base64, re
from PIL import Image

root=Path(__file__).resolve().parents[2]
fragment=Path(r'C:\Users\toby\.codex\visualizations\2026\10\01\01a0f7cb-d3ba-7ff3-9242-1a3e9c781dd3\queen-parts.html')
im=Image.open(root/'outputs/queen-hires/reference.png').convert('RGB')
im=im.crop((180,35,790,1110)).resize((488,860),Image.Resampling.LANCZOS)
buffer=BytesIO();im.save(buffer,format='JPEG',quality=90,optimize=True)
uri='data:image/jpeg;base64,'+base64.b64encode(buffer.getvalue()).decode('ascii')
html=fragment.read_text(encoding='utf-8')
assert html.count('QUEEN_IMAGE_DATA')==1
html=html.replace('QUEEN_IMAGE_DATA',uri)
fragment.write_text(html,encoding='utf-8')
assert len(html.encode('utf-8'))<1000000
assert not re.search(r'<(?:!doctype|html|head|body)(?:\s|>)',html,re.I)
assert '\\"' not in html and '\\n' not in html
ids=re.findall(r'\bid="([^"]+)"',html)
assert len(ids)==len(set(ids))
assert sorted(map(int,re.findall(r'data-part="(\d+)"',html)))==list(range(1,15))
script=re.search(r'<script>(.*?)</script>',html,re.S).group(1)
(root/'work/queen-hires/queen-parts-check.js').write_text(script,encoding='utf-8')
print(f'Prepared 14-part diagram: {len(html.encode("utf-8"))} bytes. Embedded source image, unique IDs, and all part buttons verified.')

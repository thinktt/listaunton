from PIL import Image
from pathlib import Path
p=Path(r'C:\Users\toby\Documents\Codex\2026-10-01\go-x20')
im=Image.open(p/'outputs/queen-hires/reference.png')
print(im.size)
for name,box in [('crown',(285,40,680,370)),('collars',(280,310,690,590)),('foot',(185,575,780,1100))]:
 im.crop(box).resize(((box[2]-box[0])*2,(box[3]-box[1])*2)).save(p/'work/queen-hires'/f'{name}-reference.png')

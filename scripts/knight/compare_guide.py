"""Compare the side-study at a shared physical base scale and inferred camera."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json
root=Path(__file__).resolve().parents[2];a=root/'assets/knight'
guide=Image.open(a/'concepts/side-01.png').convert('RGB')
render=Image.open(a/'guide-render.png').convert('RGBA')
background=Image.new('RGB',guide.size,'#1b1c1e');background.paste(render,mask=render.getchannel('A'))
mask=render.getchannel('A').point(lambda a:255 if a>127 else 0)
edge=np.array(mask.filter(ImageFilter.MaxFilter(3)))!=np.array(mask.filter(ImageFilter.MinFilter(3)))
overlay=np.array(guide);overlay[edge]=[45,225,235];overlay=Image.fromarray(overlay)
canvas=Image.new('RGB',(1254*3,1304),'#17191d');d=ImageDraw.Draw(canvas)
for i,(im,label) in enumerate([(guide,'Approved side guide'),(background,'Current walnut render - registered 7 degree side camera'),(overlay,'Cyan: rebuilt silhouette, fixed base registration')]):
 canvas.paste(im,(1254*i,50));d.text((1254*i+25,18),label,fill='white')
canvas.save(a/'guide-comparison.png');overlay.save(a/'guide-overlay.png')
report={'priority':'Original sprite governs the elevated fit. This imagined side guide provides an independent style and proportion comparison.','registration':json.loads((a/'guide-camera.json').read_text()),'review':'Compare broad cheek continuity, blunt gently conical muzzle, wide S neck/chest, arched mane and flat plinth directly. Silhouette metrics cannot establish anatomical quality.'}
(a/'guide-comparison.json').write_text(json.dumps(report,indent=2)+'\n')

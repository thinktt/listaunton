"""Separate small pigment variations from broad shading for a relief experiment.

This generates a height map, not a new color reference or an accepted material.
It does not assume that every luminance variation is physical wood relief.
"""
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--gain',type=float,default=2)
p.add_argument('--radius',type=int,default=8)
p.add_argument('--out',default='build/bishop-mission/114-fine-relief')
a=p.parse_args();out=ROOT/a.out
assert out.resolve().is_relative_to((ROOT/'build/bishop-mission').resolve())
out.mkdir(parents=True,exist_ok=True)
source=ROOT/'assets/bishop/bishop-boxwood-albedo.png'
pixels=np.array(Image.open(source).convert('RGB'),dtype=np.float32)/255
linear=np.where(pixels<=.04045,pixels/12.92,((pixels+.055)/1.055)**2.4)
lum=linear@np.array([.2126,.7152,.0722],dtype=np.float32)
detail=blur(lum,1)-blur(lum,a.radius)
height=np.clip(.5+a.gain*detail,.2,.8)
Image.fromarray(np.uint16(np.rint(height*65535))).save(out/'fine-relief.png')
record=dict(source=source.relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
 height_map=(out/'fine-relief.png').relative_to(ROOT).as_posix(),height_map_sha256=hashlib.sha256((out/'fine-relief.png').read_bytes()).hexdigest(),
 width=height.shape[1],height=height.shape[0],gain=a.gain,inner_blur_radius=1,outer_blur_radius=a.radius,
 range=[float(height.min()),float(height.max())],standard_deviation=float(height.std()),
 note='Bounded linear-luminance band-pass, stored as 16-bit non-color height. Broad pigment/shading removed from this relief input only. Color atlas unchanged; hypothesis, not recovered surface measurement.')
(out/'height-provenance.json').write_text(json.dumps(record,indent=2)+'\n',newline='\n')
cfg=dict(source='history/bishop-mission-013/bishop-rebuilt.blend',variant=out.name,samples=256,
 material='Bishop — inferred boxwood pigment and varnish.001',height=record,
 note='Replace only the pigment-derived portion of the bump with the fine height map. Existing noise, bump distance/strength, base color, coat and all lights preserved.')
(out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n',newline='\n')
print(json.dumps(record,indent=2))

"""Upper-patch pigment repair gated by measured excess red; preserve other regions."""
from pathlib import Path
import json,hashlib,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];source=ROOT/'assets/rook/pigment.png';assert hashlib.sha256(source.read_bytes()).hexdigest()=='37de531d5e4bef1eb0bd370c1aa2c85171297032677552aac26d659c9352b9b6'
a=np.array(Image.open(source).convert('RGB'),dtype=np.float32);h,w=a.shape[:2];U,V=np.meshgrid((np.arange(w)+.5)/w,1-(np.arange(h)+.5)/h)
q=((U-.5645)/.022)**2+((V-.4727)/.012)**2
spatial=np.clip((2-q)/.8,0,1);spatial=spatial*spatial*(3-2*spatial)
red=np.clip((.40-a[:,:,1]/np.maximum(a[:,:,0],1))/.22,0,1);red=red*red*(3-2*red);mask=spatial*red
for n,strength in [(59,.8),(60,1.2)]:
 out=ROOT/f'build/rook-mission/{n:03d}-local-pigment';out.mkdir(parents=True,exist_ok=True);result=np.clip(a+mask[:,:,None]*np.array([20,32,16])*strength,0,255).round().astype(np.uint8);Image.fromarray(result).save(out/'pigment.png');(out/'parameters.json').write_text(json.dumps({'source_atlas_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'strength':strength,'center_uv':[.5645,.4727],'radii_uv':[.022,.012],'additive_srgb_delta':[20,32,16],'excess_red_gate':'smoothstep of clamp((.40-G/R)/.22)','unmasked_pixels_exact':bool(np.array_equal(result[mask==0],a.astype(np.uint8)[mask==0])),'method':'Upper patch only, color-gated pigment lift; no resampling; inferred artistic correction, not recovered albedo.'},indent=2)+'\n')

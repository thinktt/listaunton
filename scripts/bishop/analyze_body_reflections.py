"""Compare predicted removal of each measured body reflector against the reference."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--responses',required=True);a=p.parse_args();out=ROOT/a.responses
manifest=json.loads((out/'manifest.json').read_text());base=np.load(out/'base.npy')[:,:,:3];actual=np.load(out/'actual-current.npy')
target=np.array(Image.open(ROOT/'assets/bishop/reference.png').convert('RGBA'),dtype=np.float32)/255
def display(rgb):
    rgb=np.maximum(rgb,0);return np.clip(np.where(rgb<=.0031308,rgb*12.92,1.055*np.power(rgb,1/2.4)-.055),0,1)
responses=[]
for i,lamp in enumerate(manifest['original_lights']):
    basis=blur(np.maximum(np.load(out/f'reflector-{i+1}.npy')[:,:,:3]-base,0),1)
    responses.append(basis*(lamp['energy']/manifest['basis_energy'])*np.array(lamp['color']))
current=display(actual[:,:,:3]);predicted=display(base+sum(responses))
mask=(actual[:,:,3]>.995)&(target[:,:,3]>127/255)&(target[:,:,:3].max(2)>12/255)
mask=blur(mask.astype(np.float32),4)>.999
regions={'upper_head':(450,278,590,355),'lower_head_glare':(535,417,630,477),
    'collars':(310,470,675,610),'stem_socket':(355,610,635,865),'base_foot':(220,865,760,1120)}
variants=[('Selected reference',target[:,:,:3]),('Actual current',current)]
for lamp,response in zip(manifest['original_lights'],responses):
    variants.append(('Without '+lamp['name'],display(actual[:,:,:3]-response)))
report={'note':'Subtracted-light images are predictions from measured linear BSDF responses, not accepted beauty renders. Reference/geometry/camera unchanged.',
    'reconstruction_mean_rgb_error_8bit':float(np.abs(predicted[mask]-current[mask]).mean()*255),'regions':{}}
for name,(x0,y0,x1,y1) in regions.items():
    sl=np.s_[y0:y1,x0:x1];m=mask[sl];t=target[sl][:,:,:3]
    values={label:float(np.abs(v[sl][m]-t[m]).mean()*255) for label,v in variants[1:]}
    values['mean_reflector_contribution_8bit']={lamp['name']:float((current[sl]-display(actual[:,:,:3]-response)[sl])[m].mean()*255) for lamp,response in zip(manifest['original_lights'],responses)}
    report['regions'][name]=values
for name,box in [('head-subtractions.png',(285,270,690,610)),('body-subtractions.png',(180,270,800,1120))]:
    x0,y0,x1,y1=box;tw=400;th=round(tw*(y1-y0)/(x1-x0));canvas=Image.new('RGB',(tw*len(variants),th+40),'#171b21');d=ImageDraw.Draw(canvas)
    for i,(label,value) in enumerate(variants):
        im=Image.fromarray(np.uint8(np.rint(value[y0:y1,x0:x1]*255))).resize((tw,th),Image.Resampling.LANCZOS)
        canvas.paste(im,(i*tw,40));d.text((i*tw+8,12),label,fill='white')
    canvas.save(out/name)
(out/'analysis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

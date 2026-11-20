"""Normalize narrowed reflector power to its previous intended glint, not its spill."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from image_math import blur
p=argparse.ArgumentParser();p.add_argument('--previous',required=True);p.add_argument('--responses',required=True);p.add_argument('--out',required=True)
a=p.parse_args();old=ROOT/a.previous;new=ROOT/a.responses;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
om=json.loads((old/'manifest.json').read_text());nm=json.loads((new/'manifest.json').read_text());ob=np.load(old/'base.npy')[:,:,:3];nb=np.load(new/'base.npy')[:,:,:3]
regions={'socket reflection':(520,765,600,812),'base reflection':(535,975,610,1030)}
lights=[];record={};contributions=[]
for i,lamp in enumerate(nm['original_lights']):
    prior=om['original_lights'][i];assert lamp['name']==prior['name']
    response=blur(np.maximum(np.load(new/f'reflector-{i+1}.npy')[:,:,:3]-nb,0),1)*np.array(lamp['color'])
    energy=lamp['energy']
    if lamp['name'] in regions:
        previous=blur(np.maximum(np.load(old/f'reflector-{i+1}.npy')[:,:,:3]-ob,0),1)*np.array(prior['color'])*(prior['energy']/om['basis_energy'])
        x0,y0,x1,y1=regions[lamp['name']];sl=np.s_[y0:y1,x0:x1];t=previous[sl];v=response[sl]
        mask=t.max(2)>.2*t.max();assert mask.sum()>100
        coefficient=float(np.sum(v[mask]*t[mask])/np.sum(v[mask]*v[mask]));energy=coefficient*nm['basis_energy']
        spec=next(x for x in nm['lighting_config']['lights'] if x['name']==lamp['name'])
        lights.append({**spec,'energy':energy})
        record[lamp['name']]={'old_energy':prior['energy'],'new_energy':energy,'primary_glint_box':regions[lamp['name']],
            'primary_glint_pixels':int(mask.sum()),'primary_response_relative_l2_error':float(np.linalg.norm(coefficient*v[mask]-t[mask])/np.linalg.norm(t[mask]))}
    contributions.append(response*(energy/nm['basis_energy']))
def display(rgb):
    rgb=np.maximum(rgb,0);return np.clip(np.where(rgb<=.0031308,rgb*12.92,1.055*np.power(rgb,1/2.4)-.055),0,1)
prediction=display(nb+sum(contributions));np.save(out/'predicted-display.npy',prediction)
config={'source':nm['source'],'variant':out.name,'samples':48,'lights':lights,
    'hypothesis':'Narrow socket/base emitter spread to 30 degrees; normalize measured real-BSDF contribution at each intended glint while suppressing upper-head spill. Geometry, camera, pigment and all other lighting unchanged from source.'}
(out/'lighting-config.json').write_text(json.dumps(config,indent=2)+'\n');(out/'normalization.json').write_text(json.dumps({'previous_response':a.previous,'new_response':a.responses,'lights':record},indent=2)+'\n')
ref=np.array(Image.open(ROOT/'assets/bishop/reference.png').convert('RGB'),dtype=np.float32)/255
current=np.array(Image.open((ROOT/nm['source']).parent/'wood.png').convert('RGB'),dtype=np.float32)/255
canvas=Image.new('RGB',(1200,380),'#171b21');d=ImageDraw.Draw(canvas)
for i,(label,value) in enumerate([('Selected reference',ref),('Before confinement',current),('Predicted confined lights',prediction)]):
    im=Image.fromarray(np.uint8(np.rint(value[270:610,285:690]*255))).resize((400,336),Image.Resampling.LANCZOS);canvas.paste(im,(400*i,40));d.text((400*i+8,12),label,fill='white')
canvas.save(out/'prediction.png');print(json.dumps(record,indent=2))

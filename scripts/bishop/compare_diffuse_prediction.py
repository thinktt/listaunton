import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'scripts/bishop'))
from image_math import blur
folder=root/'build/bishop-mission/101-diffuse-basis';fit=json.loads((root/'build/bishop-mission/102-fitted-continuous-wood/fit.json').read_text());size=320
base=np.load(folder/'preserved-reflections.npy');pred=base[:,:,:3].copy()
for i,spec in enumerate(fit['lights']):
    response=np.maximum(np.load(folder/f'basis-{i:02d}.npy')[:,:,:3]-base[:,:,:3],0)
    pred+=response*spec['energy']*np.array(spec['color'])
def linear(ar):return np.where(ar<=.04045,ar/12.92,((ar+.055)/1.055)**2.4)
def resize(ar):return np.array(Image.fromarray(ar.astype(np.float32)).resize((size,size),Image.Resampling.BILINEAR))
def load(path):
    ar=np.array(Image.open(path).convert('RGBA'),dtype=np.float32)/255
    return np.stack([resize(v) for v in np.moveaxis(linear(ar[:,:,:3]),2,0)],axis=2),resize(ar[:,:,3])
def srgb(ar):return np.clip(np.where(ar<=.0031308,ar*12.92,1.055*np.maximum(ar,0)**(1/2.4)-.055),0,1)
ref,alpha=load(root/'assets/bishop/reference.png');actual,_=load(root/'build/bishop-mission/102-fitted-continuous-wood/wood.png')
mask=(alpha>.99)&(base[:,:,3]>.999)&(ref.max(2)>.005)&(ref.max(2)<.85);mask=blur(mask.astype(np.float32),3)>.999
record={'prediction_reference_mae':float(np.abs(srgb(pred)[mask]-srgb(ref)[mask]).mean()*255),
 'actual_reference_mae_same_mask':float(np.abs(srgb(actual)[mask]-srgb(ref)[mask]).mean()*255),
 'prediction_actual_mae_same_mask':float(np.abs(srgb(pred)[mask]-srgb(actual)[mask]).mean()*255),
 'mean_prediction_rgb':(srgb(pred)[mask].mean(0)*255).tolist(),'mean_actual_rgb':(srgb(actual)[mask].mean(0)*255).tolist(),
 'note':'Saved actual full render reduced in linear RGB, same fitting mask; prediction is not an accepted image.'}
(root/'build/bishop-mission/102-fitted-continuous-wood/prediction-check.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

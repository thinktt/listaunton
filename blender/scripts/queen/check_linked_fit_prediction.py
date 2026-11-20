"""Compare approximate linked fitting radiance with the actual beauty render."""
from pathlib import Path
import json
import bpy,numpy as np,PyOpenColorIO as ocio
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'build/queen-mission/083-linked-reflections'
settings=json.loads((out/'parameters.json').read_text())
sun=ROOT/'build/queen-mission/directional-reflections-006'
old=ROOT/'build/queen-mission/specular-expanded-039'
specs={s['name']:s for s in json.loads((sun/'manifest.json').read_text())['specs']+json.loads((old/'manifest.json').read_text())['specs']}
ids=np.load(ROOT/'build/queen-mission/082-render-regions-equivalence/region-ids.npy')
names=['foot','base','socket','stem','lower-collar','middle-collar','upper-collar','crown-body','bowl','finial']
labels=np.rint(ids[:,:,0]*16).astype(int)-1
baseline=np.load(sun/'diffuse-baseline.npy')
linear=baseline[:,:,:3].copy()
for light in settings['lights']:
    if not light.get('receiver_parts'):continue
    region=light['receiver_parts'][0];name=light['name'].removeprefix('Linked '+region+' ')
    path=(sun if name.startswith('distant-') else old)/(name+'.npy')
    if name=='base-key':path=ROOT/'build/queen-mission/071-limited-base-reflector/diagnostic-limited-reflector.npy'
    response=np.load(path)[:,:,:3].mean(2)
    linear+=(labels==names.index(region))[:,:,None]*response[:,:,None]*np.array(light['color'])[None,None,:]*(light['energy']/specs[name]['energy'])
config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
processor=config.getProcessor(ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX')).getDefaultCPUProcessor()
prediction=linear.copy();processor.applyRGB(prediction)
actual=np.load(out/'actual-display.npy')
reference=np.load(ROOT/'build/queen-mission/pigment-fit-039/reference-srgb.npy').reshape(418,3,418,3,3).mean((1,3))
report={}
for i,name in enumerate(names):
    mask=(labels==i)&(baseline[:,:,3]>.995)&(abs(ids[:,:,0]*16-np.rint(ids[:,:,0]*16))<.01)
    report[name]={'actual_vs_prediction_mae_255':float(abs(actual-prediction)[mask].mean()*255),
       'actual_vs_reference_mae_255':float(abs(actual-reference)[mask].mean()*255),
       'prediction_vs_reference_mae_255':float(abs(prediction-reference)[mask].mean()*255),
       'mean_actual_rgb_255':(actual[mask].mean(0)*255).tolist(),
       'mean_prediction_rgb_255':(prediction[mask].mean(0)*255).tolist()}
np.save(out/'fit-prediction-diagnostic.npy',prediction)
(out/'prediction-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

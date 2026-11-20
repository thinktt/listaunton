"""Fit measured RGB wood responses with a smaller area/spot-only linked rig."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np,PyOpenColorIO as ocio
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from configure_rig import configure
from render_regions import link
directory=ROOT/'build/queen-mission/linked-wood-responses-083'
manifest=json.loads((directory/'manifest.json').read_text())
source=ROOT/manifest['source']
assert hashlib.sha256(source.read_bytes()).hexdigest()==manifest['source_sha256']
records=[r for r in manifest['responses'] if r['spec'].get('type','AREA')!='SUN']
base=np.load(directory/'diffuse-baseline.npz')['pixels']
mask=base[:,:,3]>.995
baseline=base[:,:,:3][mask].astype(np.float64)
reference=np.load(ROOT/'build/queen-mission/pigment-fit-039/reference-srgb.npy').reshape(418,3,418,3,3).mean((1,3))[mask]
response=[]
for record in records:
    path=directory/record['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']
    response.append(np.load(path)['pixels'][:,:,:3][mask])
matrix=np.stack(response,axis=2).astype(np.float64)
del response
weight=.35+np.clip(reference.min(1)*3,0,1)
config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
processor=config.getProcessor(ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX')).getDefaultCPUProcessor()
def display(values):
    values=np.asarray(values,dtype=np.float32).copy();processor.applyRGB(values);return values.astype(np.float64)
def radiance(f):return baseline+np.einsum('nck,k->nc',matrix,f,optimize=True)
def loss(f):
    prediction=display(radiance(f))
    return float(np.mean(weight[:,None]*(prediction-reference)**2)),prediction
f=np.ones(len(records));history=[]
for step in range(20):
    linear=radiance(f);value,prediction=loss(f)
    jacobian=np.empty((len(baseline),3,3),dtype=np.float64)
    for channel in range(3):
        epsilon=np.maximum(.0001,linear[:,channel]*.005)
        plus=linear.copy();minus=linear.copy()
        plus[:,channel]+=epsilon;minus[:,channel]=np.maximum(minus[:,channel]-epsilon,0)
        jacobian[:,:,channel]=(display(plus)-display(minus))/(plus[:,channel]-minus[:,channel])[:,None]
    gram=np.zeros((len(records),len(records)));rhs=np.zeros(len(records))
    for channel in range(3):
        derivative=np.einsum('nq,nqk->nk',jacobian[:,channel,:],matrix,optimize=True)
        gram+=derivative.T@(derivative*weight[:,None])
        rhs+=derivative.T@((reference-prediction)[:,channel]*weight)
    rhs+=gram@f
    scale=np.maximum(np.sqrt(np.diag(gram)),1e-8)
    normalized=gram/np.outer(scale,scale)+np.eye(len(records))*1e-4
    target_rhs=rhs/scale;proposal=f*scale;upper=10*scale
    for iteration in range(1000):
        previous=proposal.copy()
        for i in range(len(records)):
            proposal[i]=np.clip(proposal[i]+(target_rhs[i]-normalized[i]@proposal)/normalized[i,i],0,upper[i])
        if np.max(abs(proposal-previous))<1e-6:break
    target=proposal/scale;chosen=f;new_value=value
    for rate in (1,.5,.25,.125,.0625):
        candidate=f+(target-f)*rate;candidate_loss,_=loss(candidate)
        if candidate_loss<new_value:chosen=candidate;new_value=candidate_loss;break
    f=chosen;history.append({'step':step,'loss':value,'accepted_loss':new_value})
    print('FULL_WOOD_LINKED_FIT',history[-1],flush=True)
    if value-new_value<1e-8:break
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;settings=json.loads(scene['mission_material_config'])
parts={o['mission_render_region']:o for o in scene.objects if o.get('mission_render_region')}
lights=[dict(v) for v in manifest['baseline']]
for record,factor in zip(records,f):
    if factor<1e-6:continue
    spec=dict(record['spec']);spec['energy']*=float(factor);lights.append(spec)
settings['lights']=lights;settings['variant']='085-full-wood-area-reflections'
settings['full_wood_fit']={'source_sha256':manifest['source_sha256'],'response_manifest':(directory/'manifest.json').relative_to(ROOT).as_posix(),
    'response_manifest_sha256':hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest(),
    'input_emitters':len(records),'output_emitters':len(lights)-len(manifest['baseline']),
    'factor_bounds':[0,10],'history':history,'render_samples':256,
    'method':'Actual linked RGB wood responses, with a full AgX RGB Jacobian. Exclude distant emitters to reduce light count and sampling variance. Real-render verification remains necessary.'}
configure(scene,settings)
for spec in lights:
    if spec.get('receiver_parts'):
        link(bpy.data.objects[spec['name']],[parts[n] for n in spec['receiver_parts']],'+'.join(spec['receiver_parts']))
scene['mission_material_config']=json.dumps(settings,sort_keys=True)
out=ROOT/'build/queen-mission'/settings['variant'];out.mkdir(parents=True,exist_ok=True)
prediction=np.zeros((418,418,3),dtype=np.float32);prediction[mask]=loss(f)[1]
np.save(out/'prediction-diagnostic.npy',prediction)
scene.render.filepath=str(out/'wood.png');scene.cycles.samples=256
scene.cycles.use_adaptive_sampling=False;scene.cycles.use_denoising=True;scene.render.use_persistent_data=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n')
print('FULL_WOOD_AREA_RENDER_DONE',flush=True)

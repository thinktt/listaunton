"""Fit actual regional reflectors after verifying render-partition equivalence.

The cached basis is an approximation for the solve. Acceptance requires the
new actual Cycles beauty render with light-linked receiver objects.
"""
from pathlib import Path
import hashlib, json, sys
import bpy
import numpy as np
import PyOpenColorIO as ocio
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from configure_rig import configure
from render_regions import link, REGION_NAMES
directory=ROOT/'build/queen-mission/082-render-regions-equivalence'
check=json.loads((directory/'equivalence.json').read_text())
assert check['alpha_identical'] and check['foreground_mean_error_255']<.01
source=directory/'queen.blend'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
settings=json.loads(scene['mission_material_config'])
parts={o['mission_render_region']:o for o in scene.objects if o.get('mission_render_region')}
assert sorted(parts)==sorted(REGION_NAMES)
out=ROOT/'build/queen-mission/083-linked-reflections'
out.mkdir(parents=True,exist_ok=True)
sun_dir=ROOT/'build/queen-mission/directional-reflections-006'
sun_manifest=json.loads((sun_dir/'manifest.json').read_text())
base=np.load(sun_dir/'diffuse-baseline.npy')
mask=base[:,:,3]>.995
baseline=base[:,:,:3][mask].astype(np.float64)
ids=np.load(directory/'region-ids.npy')[:,:,0][mask]*16
regions=np.rint(ids).astype(int)-1
interior=abs(ids-np.rint(ids))<.01
reference=np.load(ROOT/'build/queen-mission/pigment-fit-039/reference-srgb.npy').reshape(418,3,418,3,3).mean((1,3))[mask]
specs=[];responses=[];inputs=[]
for spec in sun_manifest['specs']:
    path=sun_dir/(spec['name']+'.npy')
    specs.append(dict(spec));responses.append(np.load(path)[:,:,:3].mean(2)[mask])
    inputs.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
old_dir=ROOT/'build/queen-mission/specular-expanded-039'
for spec in json.loads((old_dir/'manifest.json').read_text())['specs']:
    if 'energy' not in spec:continue  # The fixed world is already in the baseline.
    spec=dict(spec);spec['diffuse_factor']=0;spec['specular_factor']=1
    path=old_dir/(spec['name']+'.npy')
    # Include the accepted narrow base light rather than its obsolete wide spread.
    if spec['name']=='base-key':
        spec['spread_degrees']=36
        path=ROOT/'build/queen-mission/071-limited-base-reflector/diagnostic-limited-reflector.npy'
    specs.append(spec);responses.append(np.load(path)[:,:,:3].mean(2)[mask])
    inputs.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
matrix=np.stack(responses,axis=1).astype(np.float64)
color=np.array([1,.7,.5])
config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
processor=config.getProcessor(ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX')).getDefaultCPUProcessor()
def display(v):
    a=np.asarray(v,dtype=np.float32).copy();processor.applyRGB(a);return a.astype(np.float64)
def fit(selected):
    X=matrix[selected];b=baseline[selected];ref=reference[selected]
    weight=.35+np.clip(ref.min(1)*3,0,1)
    def loss(f):
        prediction=display(b+(X@f)[:,None]*color)
        return float(np.mean(weight[:,None]*(prediction-ref)**2)),prediction
    f=np.zeros(len(specs));history=[]
    for step in range(30):
        value,prediction=loss(f);amp=X@f;linear=b+amp[:,None]*color
        epsilon=np.maximum(.0001,amp*.005)
        derivative=(display(linear+epsilon[:,None]*color)-display(np.maximum(linear-epsilon[:,None]*color,0)))/(2*epsilon[:,None])
        norm=(derivative**2).sum(1)*weight
        rhs_pixel=((ref-prediction)*derivative).sum(1)*weight+norm*amp
        scale=np.maximum(np.sqrt((X*X*norm[:,None]).sum(0)),1e-6)
        A=X/scale;gram=A.T@(A*norm[:,None])+np.eye(len(specs))*1e-4;rhs=A.T@rhs_pixel
        proposal=f*scale
        for iteration in range(500):
            previous=proposal.copy()
            for i in range(len(specs)):
                proposal[i]=max(0,proposal[i]+(rhs[i]-gram[i]@proposal)/gram[i,i])
            if np.max(abs(proposal-previous))<1e-6:break
        target=proposal/scale;chosen=f;new_value=value
        for rate in (1,.5,.25,.125,.0625):
            trial=f+(target-f)*rate;candidate,_=loss(trial)
            if candidate<new_value:chosen=trial;new_value=candidate;break
        history.append({'step':step,'loss':value,'accepted_loss':new_value});f=chosen
        if value-new_value<1e-8:break
    return f,history
lights=[dict(v) for v in settings['lights'] if v.get('diffuse_factor',1)==1]
fits=[]
for region_index,name in enumerate(REGION_NAMES):
    selected=(regions==region_index)&interior
    assert selected.sum()>50,(name,selected.sum())
    factors,history=fit(selected)
    active=0
    for spec,factor in zip(specs,factors):
        if factor<1e-7:continue
        item=dict(spec);item['name']='Linked '+name+' '+spec['name']
        item['energy']*=float(factor);item['color']=list(color);item['receiver_parts']=[name]
        lights.append(item);active+=1
    record={'region':name,'fit_pixels':int(selected.sum()),'active_lights':active,'history':history}
    fits.append(record);print('REGIONAL_LIGHT_FIT',name,'lights',active,'loss',history[-1]['accepted_loss'],flush=True)
settings['lights']=lights;settings['variant']=out.name
settings['linked_reflections']={'source_sha256':source_hash,'equivalence':check,'regions':fits,
    'response_inputs':inputs,'caveat':'Art-directed Cycles light linking. Each part receives fitted real reflected lights; diffuse lighting remains global. The closed editable control mesh is preserved. Cached global responses approximate fitting only; actual linked render decides acceptance.'}
configure(scene,settings)
for spec in lights:
    if spec.get('receiver_parts'):
        link(bpy.data.objects[spec['name']],[parts[n] for n in spec['receiver_parts']],'+'.join(spec['receiver_parts']))
assert len({o.light_linking.receiver_collection for o in scene.objects if o.type=='LIGHT' and o.light_linking.receiver_collection})<=len(REGION_NAMES)
scene['mission_material_config']=json.dumps(settings,sort_keys=True)
scene.render.filepath=str(out/'wood.png');scene.render.use_persistent_data=True
scene.cycles.samples=64;scene.cycles.use_denoising=True
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'))
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):scene.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n')
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
print('LINKED_REFLECTIONS_RENDER_DONE',flush=True)

"""Fit shadowed bowl-contact reflectors with the accepted geometry and BSDF intact."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy,numpy as np,PyOpenColorIO as ocio
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import link
p=argparse.ArgumentParser();p.add_argument('config',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);cfg=json.loads(a.config.read_text(encoding='utf-8'))
source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
capture=ROOT/cfg['capture'];cm=json.loads((capture/'manifest.json').read_text());assert cm['source_sha256']==digest
positions=np.load(capture/'position.npy');normals=np.load(capture/'normal.npy');cx,cy,_,_=cm['crop']
targets=ROOT/cfg['targets'];tm=json.loads((targets/'manifest.json').read_text());crop=tm['crop'];x1,y1,x2,y2=crop
out=ROOT/'build/queen-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s)
settings=json.loads(s['mission_material_config']);view=(s.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
levels=[(m,m.levels) for m in obj.modifiers if m.type=='SUBSURF']
for m,_ in levels:m.levels=m.render_levels
bpy.context.view_layer.update()
tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
inverse=obj.matrix_world.inverted()
for m,level in levels:m.levels=level
parts=[o for o in s.objects if o.get('mission_render_region') in cfg['receiver_parts']]
assert len(parts)==len(cfg['receiver_parts'])
new=[];records=[]
for i,(x,y) in enumerate(cfg['target_pixels']):
    ix,iy=x-cx,y-cy;position=Vector(positions[iy,ix,:3]);assert positions[iy,ix,3]>.999
    near=[]
    for yy in range(iy-1,iy+2):
        for xx in range(ix-1,ix+2):
            if positions[yy,xx,3]>.999 and np.linalg.norm(positions[yy,xx,:3]-np.asarray(position))<.025:near.append(normals[yy,xx,:3])
    normal=Vector(np.mean(near,axis=0)).normalized();direction=(2*normal.dot(view)*normal-view).normalized()
    position_lamp=position+cfg['distance']*direction
    local_direction=inverse.to_3x3()@direction
    hit=tree.ray_cast(inverse@(position+direction*.001),local_direction.normalized(),local_direction.length*(cfg['distance']-.001))
    data=bpy.data.lights.new(f'Bowl contact {i:02}','SPOT');data.energy=0;data.color=cfg['color'];data.shadow_soft_size=cfg['radius']
    data.spot_size=math.radians(cfg['cone']);data.spot_blend=.9;data.use_shadow=True
    lamp=bpy.data.objects.new(data.name,data);s.collection.objects.link(lamp);lamp.location=position_lamp
    lamp.rotation_euler=(position-position_lamp).to_track_quat('-Z','Y').to_euler();lamp.visible_diffuse=False;lamp.visible_glossy=True
    link(lamp,parts,'bowl-contact');new.append(lamp)
    spec={'name':lamp.name,'type':'SPOT','energy':cfg['energy'],'color':list(data.color),'position':list(lamp.location),'target':list(position),'target_pixel':[x,y],'size':cfg['radius']*2,'shadow_soft_size':cfg['radius'],'spot_degrees':cfg['cone'],'spot_blend':.9,'rotation_euler':list(lamp.rotation_euler),'diffuse_factor':0,'receiver_parts':cfg['receiver_parts'],'use_shadow':True}
    records.append({'spec':spec,'normal':list(normal),'center_ray_blocked':hit[0] is not None,'block_distance':float((obj.matrix_world@hit[0]-position).length) if hit[0] is not None else None})
print('CONTACT_CENTRAL_RAYS',json.dumps([{k:v for k,v in r.items() if k!='spec'} for r in records]),flush=True)
existing=[o for o in s.objects if o.type=='LIGHT' and o not in new];powers={o.name:o.data.energy for o in existing}
world=s.world.node_tree.nodes['Background'];world_power=world.inputs['Strength'].default_value
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=(x1+.01)/1254;s.render.border_max_x=(x2+.01)/1254;s.render.border_min_y=(1254-y2+.01)/1254;s.render.border_max_y=(1254-y1+.01)/1254
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
s.cycles.samples=cfg['samples'];s.cycles.use_adaptive_sampling=False;s.cycles.use_light_tree=False;s.cycles.use_denoising=False;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
def render(name):
    path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(str(path),check_existing=False);w,h=im.size;assert(w,h)==(x2-x1,y2-y1)
    values=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(values);bpy.data.images.remove(im)
    values=values.reshape(h,w,4)[::-1,:,:3].copy();np.save(out/(name+'.npy'),values);return values
baseline=render('baseline')
for o in existing:o.data.energy=0
world.inputs['Strength'].default_value=0
responses=[]
for i,lamp in enumerate(new):
    lamp.data.energy=cfg['energy'];response=render(f'response-{i:02}');responses.append(response);lamp.data.energy=0
    records[i]['mean_linear_response']=float(response.mean());records[i]['max_linear_response']=float(response.max())
    print('CONTACT_RESPONSE',i,records[i]['mean_linear_response'],records[i]['max_linear_response'],flush=True)
oc=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
assert s.view_settings.exposure==0 and s.view_settings.gamma==1 and s.view_settings.look in ('None','NONE')
processor=oc.getProcessor(ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX')).getDefaultCPUProcessor()
def display(values):
    values=np.ascontiguousarray(values,dtype=np.float32).copy();processor.applyRGB(values);return values.astype(np.float64)
# Apply the same Gaussian diagnostic blur to predicted display RGB. This does
# not alter any image asset, shader or scene; full fresh renders decide acceptance.
def blur(values):
    sigma=tm['blur_radius'];radius=int(math.ceil(sigma*3));t=np.arange(-radius,radius+1,dtype=float)
    kernel=np.exp(-.5*(t/sigma)**2);kernel/=kernel.sum();a=values.reshape(y2-y1,x2-x1,3)
    for axis in (0,1):
        pad=[(0,0),(0,0),(0,0)];pad[axis]=(radius,radius)
        padded=np.pad(a,pad,mode='edge');a=np.apply_along_axis(lambda v:np.convolve(v,kernel,mode='valid'),axis,padded)
    return a.reshape(-1,3)
base=baseline.reshape(-1,3);X=np.stack(responses,axis=-1).reshape(-1,3,len(new))
refs=[np.load(targets/(name+'.npy')).reshape(-1,3) for name in ['original','highres']]
weights=np.array(cfg['reference_weights']);assert abs(weights.sum()-1)<1e-9
target=sum(w*r for w,r in zip(weights,refs));f=np.zeros(len(new));history=[]
def loss(f):
    pred=blur(display(base+X@f));errors=[float(np.mean((pred-r)**2)) for r in refs]
    return float(weights@errors),pred,errors
for step in range(cfg['fit_steps']):
    err,pred,errors=loss(f);linear=base+X@f;J=np.empty((len(base),3,len(new)))
    for i in range(len(new)):
        J[:,:,i]=(blur(display(linear+X[:,:,i]*.02))-blur(display(np.maximum(linear-X[:,:,i]*.02,0))))/.04
    A=J.reshape(-1,len(new));rhs=(target-pred).reshape(-1)+A@f;gram=A.T@A+np.eye(len(new))*1e-5;b=A.T@rhs;proposal=f.copy()
    for _ in range(300):
        before=proposal.copy()
        for i in range(len(new)):proposal[i]=np.clip(proposal[i]+(b[i]-gram[i]@proposal)/max(gram[i,i],1e-10),0,cfg['power_gain_limit'])
        if np.max(abs(proposal-before))<1e-6:break
    best=f;newerr=err
    for rate in [1,.5,.25,.125]:
        candidate=f+(proposal-f)*rate;v,_,_=loss(candidate)
        if v<newerr:best=candidate;newerr=v;break
    history.append({'step':step,'before_loss':err,'after_loss':newerr,'reference_errors_before':errors});f=best
    print('CONTACT_FIT',step,newerr,f.tolist(),flush=True)
    if err-newerr<1e-8:break
np.save(out/'predicted-diagnostic.npy',loss(f)[1].reshape(y2-y1,x2-x1,3))
for o in existing:o.data.energy=powers[o.name]
world.inputs['Strength'].default_value=world_power
for lamp,gain,record in zip(new,f,records):
    lamp.data.energy=cfg['energy']*float(gain);record['gain']=float(gain);record['spec']['energy']=float(lamp.data.energy)
    settings['lights'].append(record['spec'])
settings['variant']=cfg['variant'];settings['finial_contact_fit']={'source_sha256':digest,'config':cfg,'targets':tm,'lights':records,'history':history,'predicted_errors_before':loss(np.zeros(len(new)))[2],'predicted_errors_after':loss(f)[2],'method':'Real shadowed glossy BSDF transport, nonnegative light powers fitted through AgX to both unchanged registered references. No material or geometry edit.'}
s['mission_material_config']=json.dumps(settings);s['mission_variant']=cfg['variant']
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
s.cycles.samples=256;s.cycles.use_denoising=True;s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False);s=bpy.context.scene
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n',encoding='utf-8')
(out/'fit.json').write_text(json.dumps(settings['finial_contact_fit'],indent=2)+'\n',encoding='utf-8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('CONTACT_FIT_RENDERED',flush=True)

"""Fit confined cross reflectors from actual linear Cycles light responses."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np,PyOpenColorIO as ocio
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,run,gpu

def pixels(image):
    w,h=image.size;a=np.empty(w*h*4,dtype=np.float32);image.pixels.foreach_get(a);return a.reshape(h,w,4)[::-1].copy()

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
    names=cfg['lights'];lights=[bpy.data.objects[n] for n in names];powers=[o.data.energy for o in lights]
    assert all(o.type=='LIGHT' and not o.visible_diffuse for o in lights)
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    s.cycles.samples=96;s.cycles.use_denoising=True;s.render.use_persistent_data=True
    s.render.use_border=True;s.render.use_crop_to_border=False;w=s.render.resolution_x;h=s.render.resolution_y
    s.render.border_min_x=350/w;s.render.border_max_x=660/w;s.render.border_min_y=1-235/h;s.render.border_max_y=1
    s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
    def capture(name):
        s.render.filepath=str(out/(name+'.exr'));bpy.ops.render.render(write_still=True)
        image=bpy.data.images.load(s.render.filepath,check_existing=False);a=pixels(image);bpy.data.images.remove(image);assert a.shape==(h,w,4);return a
    for light in lights:light.data.energy=0
    base=capture('fixed-light-response');responses=[]
    for index,(light,power) in enumerate(zip(lights,powers)):
        light.data.energy=power;response=capture('response-'+str(index))-base;responses.append(response[:,:,:3]);light.data.energy=0
    ref=bpy.data.images.load(str(ROOT/'assets/king/reference.png'),check_existing=False);assert not ref.is_float
    a=pixels(ref);display=(a[:,:,:3]*a[:,:,3:4]).astype(np.float32);target=display.copy()
    color=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
    transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX');transform.setDirection(ocio.TRANSFORM_DIR_INVERSE)
    assert s.view_settings.look=='None' and s.view_settings.exposure==0 and s.view_settings.gamma==1
    color.getProcessor(transform).getDefaultCPUProcessor().applyRGB(target)
    mask=np.zeros((h,w),dtype=bool);mask[6:155,400:615]=True;mask&=(base[:,:,3]>.99)&(a[:,:,3]>.8)
    weights=np.sqrt(1+3*np.clip((display.min(2)-.15)/.25,0,1))
    A=np.stack([(v[mask]*weights[mask,None]).reshape(-1) for v in responses],axis=1).astype(float)
    b=((target[:,:,:3]-base[:,:,:3])[mask]*weights[mask,None]).reshape(-1).astype(float)
    G=A.T@A;rhs=A.T@b;gain=np.ones(len(names));G+=np.diag(np.diag(G)*.002)
    for iteration in range(200):
        old=gain.copy()
        for j in range(len(names)):
            if G[j,j]>1e-15:gain[j]=np.clip((rhs[j]-G[j]@gain+G[j,j]*gain[j])/G[j,j],0,20)
        if abs(old-gain).max()<1e-8:break
    fitted={name:float(power*g) for name,power,g in zip(names,powers,gain)}
    for light,power in zip(lights,fitted.values()):light.data.energy=power
    report={'source_sha256':digest,'original_powers':dict(zip(names,powers)),'fitted_powers':fitted,'gain':gain.tolist(),'before_weighted_squared_residual':float(np.mean((A@np.ones(len(names))-b)**2)),'predicted_weighted_squared_residual':float(np.mean((A@gain-b)**2)),'iterations':iteration+1,'pixels':int(mask.sum()),'method':'Nonnegative coordinate-descent fit of actual linear BSDF light responses; actual full render determines acceptance, not predicted loss.'}
    (out/'fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg={k:v for k,v in cfg.items() if k!='source_sha256'};rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),original_source=cfg['source'],original_source_sha256=digest,light_fit=report)
    # mission_trial interprets a 'lights' list as a complete light replacement.
    rendercfg['fitted_lights']=rendercfg.pop('lights');run(rendercfg)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8')))

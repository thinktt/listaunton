"""Fit real linked reflectors through AgX using isolated colored-BSDF responses."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np,PyOpenColorIO as ocio
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu,run

def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
    assert s.view_settings.look=='None' and s.view_settings.exposure==0 and s.view_settings.gamma==1
    lights=[o for o in s.objects if o.type=='LIGHT'];powers={o.name:o.data.energy for o in lights};selected=[bpy.data.objects[n] for n in cfg['lights']]
    assert all(not o.visible_diffuse and o.visible_glossy for o in selected)
    world=s.world.node_tree.nodes['Background'];worldpower=world.inputs['Strength'].default_value
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    w=s.render.resolution_x;h=s.render.resolution_y;x0,y0,x1,y1=cfg['bounds'];s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=x0/w;s.render.border_max_x=x1/w;s.render.border_min_y=1-y1/h;s.render.border_max_y=1-y0/h
    s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.use_persistent_data=True
    s.cycles.samples=cfg.get('response_samples',512);s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
    def pixels(im):
        a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);return a.reshape(h,w,4)[::-1].copy()
    def capture(name):
        path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);im=bpy.data.images.load(str(path),check_existing=False);a=pixels(im);bpy.data.images.remove(im);return a
    for ob in selected:ob.data.energy=0
    fixed=capture('fixed-response')
    for ob in lights:ob.data.energy=0
    world.inputs['Strength'].default_value=0;responses=[]
    for i,ob in enumerate(selected):
        ob.data.energy=powers[ob.name];responses.append(capture('response-%02d'%i)[:,:,:3]);ob.data.energy=0
    im=bpy.data.images.load(str(ROOT/'assets/king/reference.png'),check_existing=False);assert not im.is_float;raw=pixels(im);target=raw[:,:,:3]*raw[:,:,3:4]
    mask=np.zeros((h,w),dtype=bool);mask[y0:y1,x0:x1]=True;mask&=(fixed[:,:,3]>.99)&(raw[:,:,3]>.8)
    base=fixed[:,:,:3][mask].astype(float);X=np.stack([r[mask] for r in responses],axis=-1).astype(float);target=target[mask].astype(float)
    color=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'));transform=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX');processor=color.getProcessor(transform).getDefaultCPUProcessor()
    def display(a):
        a=np.ascontiguousarray(a,dtype=np.float32);processor.applyRGB(a);return a.astype(float)
    weights=.5+np.clip((target.min(1)-.2)*3,0,1);gain=np.ones(len(selected));history=[]
    def loss(g):
        pred=display(base+X@g);return float(np.mean(weights[:,None]*(pred-target)**2)),pred
    for iteration in range(25):
        err,pred=loss(gain);linear=base+X@gain;J=np.stack([(display(linear+X[:,:,i]*.02)-display(np.maximum(linear-X[:,:,i]*.02,0)))/.04 for i in range(len(selected))],axis=-1)
        A=J.reshape(-1,len(selected));weight=np.repeat(weights,3);rhs=(target-pred).reshape(-1)+A@gain;G=A.T@(A*weight[:,None])+np.eye(len(selected))*.0001;b=A.T@(rhs*weight);proposal=gain.copy()
        for step in range(150):
            old=proposal.copy()
            for i in range(len(selected)):proposal[i]=np.clip(proposal[i]+(b[i]-G[i]@proposal)/max(G[i,i],1e-10),0,cfg.get('maximum_gain',12))
            if abs(old-proposal).max()<1e-6:break
        best=gain;newerr=err
        for rate in [1,.5,.25,.125]:
            candidate=gain+(proposal-gain)*rate;candidate_err,_=loss(candidate)
            if candidate_err<newerr:best=candidate;newerr=candidate_err;break
        history.append(dict(iteration=iteration,before_mse=err,after_mse=newerr));gain=best
        if err-newerr<1e-8:break
    for ob in lights:ob.data.energy=powers[ob.name]
    world.inputs['Strength'].default_value=worldpower
    fitted={ob.name:float(powers[ob.name]*g) for ob,g in zip(selected,gain)}
    for name,value in fitted.items():bpy.data.objects[name].data.energy=value
    report=dict(source_sha256=digest,pixels=int(mask.sum()),bounds=cfg['bounds'],original_powers={o.name:powers[o.name] for o in selected},fitted_powers=fitted,gain=gain.tolist(),history=history,method='Isolated real colored-BSDF light responses fitted through AgX, with all other lights fixed. Full render, not fitted loss, governs acceptance.')
    (out/'fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.cycles.use_adaptive_sampling=True;s.cycles.use_denoising=True
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg=dict(cfg);rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=digest,light_fit=report);rendercfg['fitted_lights']=rendercfg.pop('lights');run(rendercfg)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))

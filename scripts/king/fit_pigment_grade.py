"""Fit three bounded pigment multipliers on non-highlight socket pixels."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np,PyOpenColorIO as ocio
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu,run
from render_regions import controls


def main(cfg):
    source=ROOT/cfg['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==cfg['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s)
    assert s.view_settings.look=='None' and s.view_settings.exposure==0 and s.view_settings.gamma==1
    mat=controls(s)[0].data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links
    grade=nodes[cfg['attribute']+' grade'];attr=nodes[cfg['attribute']+' mask'];output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');original_output=output.inputs['Surface'].links[0].from_socket
    out=ROOT/'build/king-mission'/cfg['variant'];out.mkdir(parents=True,exist_ok=True)
    w=s.render.resolution_x;h=s.render.resolution_y;x0,y0,x1,y1=cfg['bounds'];s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=x0/w;s.render.border_max_x=x1/w;s.render.border_min_y=1-y1/h;s.render.border_max_y=1-y0/h
    s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.use_persistent_data=True
    s.cycles.samples=cfg.get('response_samples',512);s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
    def pixels(im):
        a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);return a.reshape(h,w,4)[::-1].copy()
    def capture(name):
        path=out/(name+'.exr');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);im=bpy.data.images.load(str(path),check_existing=False);a=pixels(im);bpy.data.images.remove(im);return a
    emission=nodes.new('ShaderNodeEmission');links.new(attr.outputs['Fac'],emission.inputs['Color']);links.new(emission.outputs[0],output.inputs['Surface'])
    weights_image=capture('grade-mask')[:,:,0];links.new(original_output,output.inputs['Surface']);nodes.remove(emission)
    grade.inputs[2].default_value=(1,1,1,1);fixed=capture('unit-grade');responses=[]
    for i in range(3):
        value=[1,1,1,1];value[i]=2;grade.inputs[2].default_value=value;responses.append(capture('grade-response-'+str(i))[:,:,:3]-fixed[:,:,:3])
    im=bpy.data.images.load(str(ROOT/'assets/king/reference.png'),check_existing=False);raw=pixels(im);target=raw[:,:,:3]*raw[:,:,3:4]
    mask=np.zeros((h,w),dtype=bool);mask[y0:y1,x0:x1]=True
    mask&=(weights_image>.15)&(fixed[:,:,3]>.99)&(raw[:,:,3]>.99)&(target.max(2)<.69)&(target[:,:,2]<.25)&(target[:,:,0]>.15)
    assert mask.sum()>500
    base=fixed[:,:,:3][mask].astype(float);X=np.stack([r[mask] for r in responses],axis=-1).astype(float);goal=target[mask].astype(float);weights=weights_image[mask].astype(float)
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
    processor=config.getProcessor(ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX')).getDefaultCPUProcessor()
    def display(a):
        a=np.ascontiguousarray(a,dtype=np.float32);processor.applyRGB(a);return a.astype(float)
    def loss(g):
        pred=display(np.maximum(base+X@g,0));return float(np.mean(weights[:,None]*(pred-goal)**2)),pred
    gain=np.array(cfg.get('initial_multiplier',[1,1,1]),dtype=float)-1;history=[]
    for iteration in range(20):
        error,pred=loss(gain);linear=base+X@gain
        J=np.stack([(display(np.maximum(linear+X[:,:,i]*.02,0))-display(np.maximum(linear-X[:,:,i]*.02,0)))/.04 for i in range(3)],axis=-1)
        A=J.reshape(-1,3);weight=np.repeat(weights,3);rhs=(goal-pred).reshape(-1)+A@gain;G=A.T@(A*weight[:,None])+np.eye(3)*1e-5;b=A.T@(rhs*weight)
        proposal=gain.copy()
        for _ in range(100):
            old=proposal.copy()
            for i in range(3):proposal[i]=np.clip(proposal[i]+(b[i]-G[i]@proposal)/max(G[i,i],1e-10),-.4,3)
            if abs(old-proposal).max()<1e-7:break
        best=gain;new_error=error
        for rate in [1,.5,.25,.125]:
            candidate=gain+rate*(proposal-gain);e,_=loss(candidate)
            if e<new_error:best=candidate;new_error=e;break
        history.append(dict(iteration=iteration,before_mse=error,after_mse=new_error));gain=best
        if error-new_error<1e-9:break
    fitted=(1+gain).tolist();grade.inputs[2].default_value=(*fitted,1)
    report=dict(source_sha256=digest,attribute=cfg['attribute'],pixels=int(mask.sum()),bounds=cfg['bounds'],fitted_linear_multiplier=fitted,
                history=history,method='Three local material RGB multipliers fitted through AgX from real response renders; high-reflection reference pixels excluded; all lights fixed. Full rendering governs acceptance.')
    (out/'fit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');np.savez_compressed(out/'fit-mask.npz',mask=mask,weights=weights_image)
    s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.cycles.use_adaptive_sampling=True;s.cycles.use_denoising=True
    bpy.data.images.remove(im);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'prepared.blend'))
    rendercfg=dict(cfg);rendercfg.update(source=(out/'prepared.blend').relative_to(ROOT).as_posix(),source_sha256=hashlib.sha256((out/'prepared.blend').read_bytes()).hexdigest(),original_source=cfg['source'],original_source_sha256=digest,pigment_fit=report)
    run(rendercfg);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(json.loads(Path(a.config).read_text(encoding='utf-8-sig')))

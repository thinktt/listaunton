"""Compare identical king scene data and raw fixed-sample saved-file renders."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu
from check_base_light_checkpoint import snapshot
from check_socket_checkpoint import extra
p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');p.add_argument('--samples',type=int,default=256)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=ROOT/a.output;out.mkdir(parents=True,exist_ok=True)
first,lights1,_=snapshot(a.before);ex1=extra();second,lights2,_=snapshot(a.after);ex2=extra()
assert first==second and lights1==lights2 and ex1==ex2,'Unexpected scene difference'
report=dict(scene_snapshot_exact=True,all_float_attributes_packed_images_and_lights_exact=True,samples=a.samples,adaptive=False,denoising=False,files={})
pixels=[]
for label,path in [('before',a.before),('after',a.after)]:
    src=ROOT/path;digest=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False);s=bpy.context.scene;gpu(s)
    report[label+'_saved_sampling']={k:getattr(s.cycles,k,None) for k in ['samples','seed','use_animated_seed','use_adaptive_sampling','use_denoising','denoiser','denoising_prefilter','denoising_input_passes','denoising_use_gpu']}
    s.cycles.samples=a.samples;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
    s.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(s.render.filepath,check_existing=False);data=np.array(im.pixels[:],dtype=np.float32)
    pixels.append(data.reshape(s.render.resolution_y,s.render.resolution_x,4)[::-1]);bpy.data.images.remove(im)
    report['files'][label]=dict(source=path,source_sha256=digest,render_sha256=hashlib.sha256((out/(label+'.png')).read_bytes()).hexdigest())
    assert hashlib.sha256(src.read_bytes()).hexdigest()==digest
d=abs(pixels[0]-pixels[1]);y,x,c=np.unravel_index(d.argmax(),d.shape)
report['difference']=dict(maximum_display_channel_255=float(d.max()*255),mean_display_channel_255=float(d.mean()*255),maximum_at=[int(x),int(y),int(c)],alpha_exact=bool(np.array_equal(pixels[0][:,:,3],pixels[1][:,:,3])))
(out/'diagnostic.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('KING_RAW_RENDER_COMPARISON',json.dumps(report),flush=True)

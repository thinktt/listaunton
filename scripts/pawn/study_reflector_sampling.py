"""Separate new-reflector support from changes in the Cycles sample sequence."""
import argparse,json,sys,shutil
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from mission_render import ROOT,BUILD,render,save_json,sha
from polish_trial import open_source

def run(cfg):
    out=BUILD/cfg['measurement'];out.mkdir(parents=True,exist_ok=True);record={'config':cfg,'renders':{}}
    for pose in cfg['sources']:
        scene,body=open_source({**pose,'samples':512});scene.cycles.seed=31
        path=out/(pose['name']+'-seed31.png');render(scene,path);record['renders'][pose['name']]=sha(path)
    if 'prior_baseline' in cfg:
        previous=ROOT/cfg['prior_baseline']['render']
        assert sha(previous)==cfg['prior_baseline']['sha256']
        shutil.copyfile(previous,out/'before-seed31.png');record['reused_before_seed31_sha256']=sha(previous)
    if 'isolate_lights' in cfg:
        from fit_lighting import response
        wanted=set(cfg['isolate_lights']);assert wanted<=set(o.name for o in scene.objects if o.type=='LIGHT')
        for ob in scene.objects:
            if ob.type=='LIGHT' and ob.name not in wanted:ob.data.energy=0
        scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
        scene.cycles.use_denoising=False;scene.cycles.use_adaptive_sampling=False;scene.cycles.seed=0
        scene.render.image_settings.file_format='OPEN_EXR';scene.render.image_settings.color_depth='32'
        rgba=response(scene,out);np.save(out/'isolated-response.npy',rgba)
        record['isolated_response_sha256']=sha(out/'lighting-response.exr')
    else:
        image=bpy.data.images.load(str(ROOT/cfg['isolated_response']),check_existing=False)
        try:
            w,h=image.size;rgba=np.empty(w*h*4,np.float32);image.pixels.foreach_get(rgba)
            rgba=rgba.reshape(h,w,4)[::-1].copy();np.save(out/'isolated-response.npy',rgba)
            record['isolated_response_sha256']=sha(ROOT/cfg['isolated_response'])
        finally:bpy.data.images.remove(image)
    save_json(out/'measurement.json',record)
    print('Reflector sampling study saved; no accepted scene changed.',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    run(json.loads(a.config.read_text(encoding='utf8')))

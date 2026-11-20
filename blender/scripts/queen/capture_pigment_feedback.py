"""Measure a saved queen pigment trial for one bounded inverse-color feedback step."""
from pathlib import Path
import sys,json,hashlib,argparse
import bpy,numpy as np
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r/'scripts/queen'));from queen_scene import editable_mesh
p=argparse.ArgumentParser();p.add_argument('variant');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);src=r/'build/queen-mission'/args.variant/'queen.blend';bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False);s=bpy.context.scene;obj=editable_mesh(s);mat=obj.data.materials[0];ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF');output=next(n for n in ns if n.type=='OUTPUT_MATERIAL');mix=bs.inputs['Base Color'].links[0].from_node
out=src.parent;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA';s.render.use_persistent_data=True;s.cycles.samples=128
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
def render(name):
 p=out/(name+'.exr');s.render.filepath=str(p);bpy.ops.render.render(write_still=True);im=bpy.data.images.load(str(p),check_existing=False);w,h=im.size;a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1].copy();np.save(out/(name+'.npy'),a);return a
beauty=render('linear-beauty');em=ns.new('ShaderNodeEmission');ls.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);ls.new(em.outputs[0],output.inputs['Surface']);pigment=render('actual-pigment');ls.new(mix.inputs[0].links[0].from_socket,em.inputs['Color']);factor=render('actual-factor');s.cycles.samples=1
p=r/'build/queen-mission/pigment-fit-011';black=np.load(p/'black-bsdf.npy')[:,:,:3];white=np.load(p/'white-bsdf.npy')[:,:,:3];target=np.load(p/'reference-linear.npy');pred=black+(white-black)*pigment[:,:,:3];m=pigment[:,:,3]>.995
regions=dict(bowl=(350,110,610,310),body=(370,350,600,430),stem=(400,560,570,710),base=(260,840,700,990));metrics={}
for name,(x1,y1,x2,y2) in regions.items():
 a=np.s_[y1:y2,x1:x2];mask=m[a];actual=beauty[a][:,:,:3][mask];pr=pred[a][mask];ref=target[a][mask];metrics[name]={'factor_quantile':np.quantile(factor[a][:,:,0][mask],[.1,.5,.9]).tolist(),'actual_to_prediction':np.median(actual/np.maximum(pr,.001),axis=0).tolist(),'actual_to_target':np.median(actual/np.maximum(ref,.001),axis=0).tolist(),'prediction_to_target':np.median(pr/np.maximum(ref,.001),axis=0).tolist()}
(out/'feedback-manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'samples':128,'note':'Diagnostic pigment and linear BSDF passes; source model unchanged.'},indent=2));(out/'inverse-check.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics),flush=True)

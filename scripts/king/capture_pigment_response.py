"""Capture black/white real-BSDF response for a king pigment estimate."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT,gpu,meshes
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/args.source;out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
digest=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;gpu(s);s.cycles.samples=96;s.cycles.use_denoising=True;s.render.use_persistent_data=True
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
mat=meshes(s)[0].data.materials[0];bs=mat.node_tree.nodes['Principled BSDF']
assert len({o.data.materials[0] for o in meshes(s)})==1
for link in list(bs.inputs['Base Color'].links):mat.node_tree.links.remove(link)
for name,value in [('black',0),('white',1)]:
    bs.inputs['Base Color'].default_value=(value,value,value,1)
    s.render.filepath=str(out/(name+'.exr'));bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(s.render.filepath,check_existing=False);w,h=im.size
    ar=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(ar);ar=ar.reshape(h,w,4)[::-1].copy();assert np.isfinite(ar).all()
    np.save(out/(name+'.npy'),ar);bpy.data.images.remove(im)
report={'source':args.source,'source_sha256':digest,'resolution':[w,h],'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'display_device':s.display_settings.display_device,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'method':'Black and white pigment in the actual Principled BSDF, retaining normals, coat, lights, geometry and camera. Difference approximates local diffuse response; multibounce effects limit inversion.'}
(out/'response.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
print('KING_PIGMENT_RESPONSE',json.dumps(report),flush=True)

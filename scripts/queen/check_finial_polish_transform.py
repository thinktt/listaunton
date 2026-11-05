"""Verify the actual finial-polish field follows a translated piece and camera."""
from pathlib import Path
import bpy,numpy as np,json,hashlib,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
source=ROOT/'build/queen-mission/176-standard-light-sampling/queen.blend';digest=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
nodes=editable_mesh(s).data.materials[0].node_tree.nodes;links=editable_mesh(s).data.materials[0].node_tree.links
socket=nodes['Bump.001'].inputs['Distance'].links[0].from_socket
scale=nodes.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=100;links.new(socket,scale.inputs[0])
em=nodes.new('ShaderNodeEmission');links.new(scale.outputs[0],em.inputs['Color']);output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');links.new(em.outputs[0],output.inputs['Surface'])
s.cycles.samples=16;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.image_settings.color_mode='RGBA'
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
out=ROOT/'build/queen-mission/finial-polish-transform-017';out.mkdir(exist_ok=True,parents=True)
def render(name):
    s.render.filepath=str(out/(name+'.exr'));bpy.ops.render.render(write_still=True);im=bpy.data.images.load(s.render.filepath,check_existing=False);w,h=im.size;pixels=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(pixels);bpy.data.images.remove(im);return pixels.reshape(h,w,4)[::-1].copy()
a=render('before')
for o in s.objects:
    if o.parent is None:o.location+=Vector((1.25,-.75,.5))
b=render('translated');opaque=(a[:,:,3]>.999)&(b[:,:,3]>.999)
error=abs(a[:,:,0]-b[:,:,0])/100
report={'source_sha256':digest,'translation':[1.25,-.75,.5],'comparison':'Actual emitted bump Distance, divided by diagnostic scale 100, over pixels opaque in both camera-matched views. No beauty shader/source file modified.',
        'mean_distance_error':float(error[opaque].mean()),'p999_distance_error':float(np.quantile(error[opaque],.999)),'max_distance_error':float(error[opaque].max()),'opaque_pixels':int(opaque.sum()),'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==digest}
assert report['source_unchanged'] and report['max_distance_error']<.00001,report
report['passed']=True;(out/'check.json').write_text(json.dumps(report,indent=2)+'\n');print('FINIAL_POLISH_TRANSLATION_CHECK',json.dumps(report),flush=True)

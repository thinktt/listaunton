"""Read the actual BSDF normal input through an unsaved emission diagnostic."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--points',required=True)
p.add_argument('--border',nargs=4,type=int,default=[450,370,565,465],metavar=('X0','Y0','X1','Y1'))
p.add_argument('--mean-radius',type=int,default=0)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.source;out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
points=json.loads((ROOT/a.points).read_text());materials={m for ob in s.objects if ob.type=='MESH' and not ob.hide_render for m in ob.data.materials}
for material in materials:
    ns=material.node_tree.nodes;ls=material.node_tree.links;bs=ns['Principled BSDF']
    normal=bs.inputs['Normal'].links[0].from_socket if bs.inputs['Normal'].is_linked else ns.new('ShaderNodeNewGeometry').outputs['Normal']
    add=ns.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(1,1,1);ls.new(normal,add.inputs[0])
    half=ns.new('ShaderNodeVectorMath');half.operation='SCALE';half.inputs['Scale'].default_value=.5;ls.new(add.outputs['Vector'],half.inputs[0])
    emission=ns.new('ShaderNodeEmission');ls.new(half.outputs['Vector'],emission.inputs['Color']);ls.new(emission.outputs[0],ns['Material Output'].inputs['Surface'])
s.render.use_border=True;s.render.use_crop_to_border=False;w,h=s.render.resolution_x,s.render.resolution_y
x0,y0,x1,y1=a.border;assert 0<=x0<x1<=w and 0<=y0<y1<=h and a.mean_radius>=0
s.render.border_min_x=x0/w;s.render.border_max_x=x1/w;s.render.border_min_y=1-y1/h;s.render.border_max_y=1-y0/h
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32'
s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.use_denoising=False;s.render.filepath=str(out/'normals.exr')
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(str(out/'normals.exr'),check_existing=False)
values=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1].copy();normal=values[:,:,:3]*2-1
np.save(out/'normals.npy',normal);records={}
for name,(x,y) in points.items():
    radius=a.mean_radius;assert x0+radius<=x<x1-radius and y0+radius<=y<y1-radius
    region=normal[y-radius:y+radius+1,x-radius:x+radius+1]
    alpha=values[y-radius:y+radius+1,x-radius:x+radius+1,3];assert alpha.min()>.999
    v=region.mean((0,1));v/=np.linalg.norm(v);records[name]={'pixel':[x,y],'normal':v.tolist(),'alpha':float(values[y,x,3]),'mean_radius':radius}
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
(out/'manifest.json').write_text(json.dumps({'source':a.source,'source_sha256':sha,'points':records,
 'border_pixels':a.border,
 'note':'Unsaved BSDF-normal emission diagnostic, including shader bump. This is not a beauty render; source model unchanged.'},indent=2)+'\n')
print(json.dumps(records,indent=2))

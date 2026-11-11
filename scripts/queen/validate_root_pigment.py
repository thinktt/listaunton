"""Validate the local pigment-only change and its object-space preview formula."""
from pathlib import Path
import argparse,hashlib,json,sys
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh,render_meshes
from validate_profile_preservation import inspect
p=argparse.ArgumentParser();p.add_argument('current');p.add_argument('--out',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=ROOT/a.current;digest=hashlib.sha256(source.read_bytes()).hexdigest()
baseline=ROOT/'history/queen-mission-021/queen-rebuilt.blend';before=inspect(baseline);after=inspect(source)
s=bpy.context.scene;o=editable_mesh(s);settings=json.loads(s['mission_material_config']);change=settings['finial_root_pigment'];cfg=change['config']
assert change['source_sha256']==hashlib.sha256(baseline.read_bytes()).hexdigest()
assert cfg['gain']==2.5 and cfg['height_rise']==[4.025,4.065] and cfg['height_fall']==[4.08,4.14] and cfg['radius_fall']==[.215,.245]
added=set(change['nodes_added']);assert set(after['material_nodes'])-set(before['material_nodes'])==added
for name,value in before['material_nodes'].items():assert after['material_nodes'][name]==value,name
old_name,old_socket=change['previous_base_color_link']
retained=[v for v in after['material_links'] if v[0] not in added and v[2] not in added]
retained.append((old_name,old_socket,'Principled BSDF','Base Color'))
assert sorted(retained)==before['material_links']
for key in ['lights','camera','object_matrix']:assert before[key]==after[key],key
assert np.allclose(after['object_matrix'],np.eye(4).reshape(-1),rtol=0,atol=1e-8), 'Viewer root field assumes baked identity object transform'
nodes=o.data.materials[0].node_tree.nodes;links=o.data.materials[0].node_tree.links
labels={n.label:n for n in nodes if n.name in added}
local=labels['Root pigment local position'];assert(local.vector_type,local.convert_from,local.convert_to)==('POINT','WORLD','OBJECT')
for label,limits in [('Root pigment lower blend',cfg['height_rise']),('Root pigment upper blend',cfg['height_fall']),('Root pigment radial blend',cfg['radius_fall'])]:
    node=labels[label];assert node.interpolation_type=='SMOOTHSTEP' and node.clamp
    assert np.allclose([node.inputs['From Min'].default_value,node.inputs['From Max'].default_value],limits,rtol=0,atol=1e-6)
gain=labels['Root pigment gain'];assert gain.operation=='MULTIPLY_ADD' and gain.inputs[1].default_value==cfg['gain']-1 and gain.inputs[2].default_value==1
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
# An emission-only diagnostic checks the actual material field, never a beauty.
surface=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');em=nodes.new('ShaderNodeEmission')
links.new(gain.outputs[0],em.inputs['Color']);links.new(em.outputs[0],surface.inputs['Surface'])
crop=[400,225,570,300];x1,y1,x2,y2=crop
s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=(x1+.01)/1254;s.render.border_max_x=(x2+.01)/1254;s.render.border_min_y=(1254-y2+.01)/1254;s.render.border_max_y=(1254-y1+.01)/1254
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.cycles.samples=32;s.cycles.use_denoising=False;s.render.use_persistent_data=True
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
if any(d.use for d in prefs.devices):s.cycles.device='GPU'
def render(name):
    s.render.filepath=str(out/(name+'.exr'));bpy.ops.render.render(write_still=True);im=bpy.data.images.load(s.render.filepath,check_existing=False)
    w,h=im.size;assert(w,h)==(x2-x1,y2-y1);arr=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(arr);bpy.data.images.remove(im)
    return arr.reshape(h,w,4)[::-1].copy()
field=render('root-pigment-field')
capture=ROOT/'build/queen-mission/finial-contact-surface-021'
assert json.loads((capture/'manifest.json').read_text())['source_sha256']==change['source_sha256']
position=np.load(capture/'position.npy');assert position.shape==field.shape
def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
coords=position[:,:,:3];z=coords[:,:,2];r=np.linalg.norm(coords[:,:,:2],axis=2)
expected=1+(cfg['gain']-1)*smooth(*cfg['height_rise'],z)*(1-smooth(*cfg['height_fall'],z))*(1-smooth(*cfg['radius_fall'],r))
mask=(position[:,:,3]>.999)&(field[:,:,3]>.999);error=abs(field[:,:,0]-expected)[mask]
assert float(error.mean())<.003 and float(np.quantile(error,.99))<.02
delta=Vector((1.3,-.8,.6))
for obj in [o]+render_meshes(s)+[s.camera]:obj.location+=delta
bpy.context.view_layer.update();moved=render('root-pigment-field-translated');translation_error=abs(moved-field)[mask,:3]
assert float(translation_error.mean())<.001 and float(np.quantile(translation_error,.99))<.005
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
report={'passed':True,'source_sha256':digest,'baseline_sha256':change['source_sha256'],'all_existing_material_nodes_and_packed_images_identical':True,'only_base_color_link_extended':True,'all_lights_camera_transform_identical':True,'lights':len(before['lights']),'relief_unchanged':True,'coordinate_space':'OBJECT','field_formula_mean_error':float(error.mean()),'field_formula_p99_error':float(np.quantile(error,.99)),'translation_mean_error':float(translation_error.mean()),'translation_p99_error':float(np.quantile(translation_error,.99)),'gain_bounds':[1,cfg['gain']],'diagnostic_only':'Emission field images validate the mask, not visual fidelity.'}
(out/'root-pigment-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('ROOT_PIGMENT_VALIDATION',json.dumps(report),flush=True)

"""Compare true rendered silhouettes under identical uniform primary sampling."""
from pathlib import Path
import bpy,numpy as np,json,sys,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import set_material
p=argparse.ArgumentParser();p.add_argument('--baseline',default='history/queen-mission-015/queen-rebuilt.blend');p.add_argument('--trial',default='155-fitted-ridge-crescents');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=ROOT/'build/queen-mission'/a.trial;paths=[ROOT/a.baseline,out/'queen.blend'];hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths];alphas=[];cameras=[]
for label,path in zip(['baseline','candidate'],paths):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.context.scene
 c=s.camera;cameras.append({'matrix':[list(row) for row in c.matrix_world],'type':c.data.type,'scale':c.data.ortho_scale,'shift':[c.data.shift_x,c.data.shift_y],'sensor_fit':c.data.sensor_fit,'resolution':[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage]})
 mat=bpy.data.materials.new('Uniform silhouette diagnostic');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.2,.2,.2,1);o=n.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(e.outputs[0],o.inputs['Surface']);set_material(s,mat)
 s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):s.cycles.device='GPU'
 destination=out/('uniform-silhouette-'+label+'.png');s.render.filepath=str(destination);bpy.ops.render.render(write_still=True)
 image=bpy.data.images.load(str(destination),check_existing=False);pixels=np.empty(image.size[0]*image.size[1]*4,dtype=np.float32);image.pixels.foreach_get(pixels);alphas.append(pixels.reshape(-1,4)[:,3].copy());bpy.data.images.remove(image)
assert cameras[0]==cameras[1],'Camera or registration differs'
different=int(np.count_nonzero((alphas[0]>.5)!=(alphas[1]>.5)))
report={'baseline_sha256':hashes[0],'trial_sha256':hashes[1],'samples':256,'adaptive_sampling':False,'geometry_only_emission_diagnostic':True,'camera_identical':True,'camera':cameras[0],'different_binary_silhouette_pixels':different,'max_alpha_difference':float(abs(alphas[0]-alphas[1]).max()),'passed':different==0}
(out/'uniform-silhouette-check.json').write_text(json.dumps(report,indent=2)+'\n')
assert [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]==hashes
print('UNIFORM_SILHOUETTE',json.dumps(report),flush=True)
assert report['passed'],'Uniform silhouettes differ; do not claim only a sampling change'

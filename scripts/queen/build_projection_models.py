"""Build reduced-resolution, physically refitted queen studies from a read-only baseline.

Run with Blender --background --python scripts/queen/build_projection_models.py.
The candidate is saved with its reference camera, then exported and rendered from
that exact geometry. The common front camera is only used in memory afterwards.
"""
from pathlib import Path
import sys, json, hashlib, math
import bpy, bmesh
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from projection_geometry import deform
A=ROOT/'assets/queen-projections'
info=json.loads((A/'baseline-info.json').read_text(encoding='utf-8'))
manifest=json.loads((A/'variants.json').read_text(encoding='utf-8'))
resume='--resume' in sys.argv
controls=np.load(A/'baseline-controls.npz')['points']
baseline=ROOT/'models/queen/queen-rebuilt.blend'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(baseline)==info['sourceSha256']
def dump(path,data):path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def flat(m):return [float(x) for row in m for x in row]
def camera_record(scene):
 cam=scene.camera;d=cam.data;r=scene.render;dg=bpy.context.evaluated_depsgraph_get()
 return dict(type=d.type,worldToCamera=flat(cam.matrix_world.inverted()),projectionMatrix=flat(cam.calc_matrix_camera(dg,x=r.resolution_x,y=r.resolution_y,scale_x=r.pixel_aspect_x,scale_y=r.pixel_aspect_y)),orthoScale=d.ortho_scale,shiftX=d.shift_x,shiftY=d.shift_y,width=r.resolution_x,height=r.resolution_y,pixelAspectX=r.pixel_aspect_x,pixelAspectY=r.pixel_aspect_y,clipStart=d.clip_start,clipEnd=d.clip_end,matrixConvention='4x4 row-major; multiplication by a column vector')
def aim(cam,target):cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
def configure_reference(scene,fit):
 e=math.radians(fit['elevation']);s=fit['scale'];w=1254
 target=(fit['yfloor']-w/2)/(s*math.cos(e));cam=scene.camera
 cam.data.type='ORTHO';cam.data.ortho_scale=w/s;cam.data.shift_x=(w/2-fit['cx'])/w;cam.data.shift_y=0;cam.data.sensor_fit='AUTO'
 cam.location=(0,-12*math.cos(e),target+12*math.sin(e));aim(cam,(0,0,target))
 scene.render.resolution_x=w;scene.render.resolution_y=w;scene.render.resolution_percentage=100
 scene.render.pixel_aspect_x=scene.render.pixel_aspect_y=1
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
 scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.cycles.device='CPU'
 bpy.context.view_layer.update()
def bounds(p):
 lo=p.min(0);hi=p.max(0)
 return dict(min=lo.tolist(),max=hi.tolist(),center=((hi+lo)/2).tolist(),size=(hi-lo).tolist())
def export(scene,obj,model,folder):
 dg=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles()
 p=np.array([ev.matrix_world@v.co for v in mesh.vertices],dtype='<f4');normalmat=ev.matrix_world.to_3x3().inverted().transposed()
 normals=np.array([(normalmat@v.normal).normalized() for v in mesh.vertices],dtype='<f4')
 indices=np.array([t.vertices for t in mesh.loop_triangles],dtype='<u4').reshape(-1)
 attrs=np.concatenate([p,normals],axis=1).astype('<f4')
 bm=bmesh.new();bm.from_mesh(mesh)
 qa=dict(vertices=len(mesh.vertices),triangles=len(indices)//3,boundaryEdges=sum(e.is_boundary for e in bm.edges),nonManifoldEdges=sum(not e.is_manifold for e in bm.edges),signedVolume=bm.calc_volume(signed=True),allAttributesFinite=bool(np.isfinite(attrs).all()),allIndicesInRange=bool(indices.max()<len(p)),maxNormalLengthError=float(abs(np.linalg.norm(normals,axis=1)-1).max()),floor=float(p[:,2].min()),baseWidth=float(np.ptp(p[:,0])),height=float(np.ptp(p[:,2])))
 assert qa['boundaryEdges']==qa['nonManifoldEdges']==0 and qa['signedVolume']>0
 assert qa['allAttributesFinite'] and qa['allIndicesInRange'] and qa['maxNormalLengthError']<1e-5
 assert abs(qa['floor'])<1e-5
 bm.free();bb=bounds(p);cam=camera_record(scene)
 (folder/'mesh.bin').write_bytes(attrs.tobytes()+indices.tobytes())
 meta=dict(schemaVersion=1,sourceBlend=model.relative_to(ROOT).as_posix(),sourceSha256=digest(model),binary=(folder/'mesh.bin').relative_to(ROOT).as_posix(),coordinateSystem='Blender world XYZ, right-handed, +Z up; no axis conversion',endianness='little',vertexType='float32',indexType='uint32',vertexCount=len(p),indexCount=len(indices),triangleCount=len(indices)//3,vertexStrideBytes=24,positionOffsetBytes=0,normalOffsetBytes=12,vertexByteOffset=0,vertexByteLength=attrs.nbytes,indexByteOffset=attrs.nbytes,indexByteLength=indices.nbytes,totalByteLength=attrs.nbytes+indices.nbytes,bounds=bb,parts=[dict(name=obj.name,vertexOffset=0,vertexCount=len(p),indexOffset=0,indexCount=len(indices),triangleCount=len(indices)//3,bounds=bb,subdivisionLevels=[1])],referenceCamera=cam,validation=qa)
 dump(folder/'mesh.json',meta);dump(folder/'camera.json',cam);dump(folder/'geometry-check.json',qa)
 ev.to_mesh_clear();return qa
def render(scene,path):
 scene.render.filepath=str(path)
 bpy.ops.render.render(write_still=True)
for row in manifest['variants']:
 folder=ROOT/row['assetDir'];fit=json.loads((folder/'fit.json').read_text(encoding='utf-8'));model=ROOT/row['model'];model.parent.mkdir(parents=True,exist_ok=True)
 if resume and model.exists() and all((folder/name).exists() for name in ('mesh.bin','mesh.json','camera.json','geometry-check.json')):
  meta=json.loads((folder/'mesh.json').read_text(encoding='utf-8'));assert digest(model)==meta['sourceSha256']
  qa=json.loads((folder/'geometry-check.json').read_text(encoding='utf-8'))
  row.update(height=qa['height'],baseWidth=qa['baseWidth'],heightToBaseWidth=qa['height']/qa['baseWidth'])
  if all((folder/name).exists() for name in ('render.png','profile.png','profile-camera.json')):
   print('PRESERVED COMPLETE',row['id'],flush=True);continue
  bpy.ops.wm.open_mainfile(filepath=str(model));scene=bpy.context.scene
  assert scene['projection_elevation']==row['elevation']
  print('RESUMING RENDERS',row['id'],flush=True)
 else:
  bpy.ops.wm.open_mainfile(filepath=str(baseline));scene=bpy.context.scene;obj=bpy.data.objects[info['object']]
  points,yfloor=deform(controls,info,row['elevation'],fit['parameters']);assert abs(yfloor-fit['yfloor'])<1e-8
  obj.data.vertices.foreach_set('co',points.astype(np.float32).reshape(-1));obj.data.update()
  for mod in obj.modifiers:
   if mod.type=='SUBSURF':mod.levels=mod.render_levels=1
  obj['projection_elevation']=row['elevation'];obj['projection_baseline_sha256']=info['sourceSha256'];obj['projection_refit_parameters']=fit['parameters']
  scene['projection_study']='Queen geometry refit; fixed physical base width and floor';scene['projection_elevation']=row['elevation']
  configure_reference(scene,fit)
  # The original builder's packed reference planes are hidden in render and viewport.
  bpy.context.preferences.filepaths.save_version=0
  bpy.ops.wm.save_as_mainfile(filepath=str(model))
  qa=export(scene,obj,model,folder)
  row.update(height=qa['height'],baseWidth=qa['baseWidth'],heightToBaseWidth=qa['height']/qa['baseWidth'])
 # GPU is a render-only preference; saved candidates retain CPU fallback.
 try:
  prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
  gpu=False
  for device in prefs.devices:device.use=device.type!='CPU';gpu|=device.use
  if gpu:scene.cycles.device='GPU'
 except Exception:pass
 render(scene,folder/'render.png')
 cam=scene.camera;cam.location=(0,-16,2.9);aim(cam,(0,0,2.9));cam.data.shift_x=cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=6.2
 scene.render.resolution_x=600;scene.render.resolution_y=900;bpy.context.view_layer.update()
 dump(folder/'profile-camera.json',camera_record(scene));render(scene,folder/'profile.png')
 dump(A/'variants.json',manifest)
 print('COMPLETE',row['id'],qa,flush=True)
assert digest(baseline)==info['sourceSha256']
print('QUEEN PROJECTION MODEL BUILD COMPLETE',flush=True)

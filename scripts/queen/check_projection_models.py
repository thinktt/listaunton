"""Reopen saved queen candidates and compare their reduced surfaces with dense ones."""
from pathlib import Path
import bpy,json,hashlib,sys
import numpy as np
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'assets/queen-projections'
sys.path.insert(0,str(Path(__file__).parent));from projection_geometry import deform
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=read(A/'baseline-info.json');rows=read(A/'variants.json')['variants'];controls=np.load(A/'baseline-controls.npz')['points'];results=[]
for row in rows:
 source=ROOT/row['model'];before=sha(source);folder=ROOT/row['assetDir'];fit=read(folder/'fit.json');meta=read(folder/'mesh.json');cam=meta['referenceCamera']
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);scene=bpy.context.scene;ob=bpy.data.objects[info['object']]
 p=np.array([tuple(v.co) for v in ob.data.vertices]);expected,_=deform(controls,info,row['elevation'],fit['parameters']);error=float(abs(p-expected).max());assert error<1e-6
 assert scene['continuous_crown'] and scene['crown_tip_count']==8
 actual=np.array(scene.camera.matrix_world.inverted()).reshape(-1);assert np.max(abs(actual-np.array(cam['worldToCamera'])))<1e-7
 dg=bpy.context.evaluated_depsgraph_get();projection=np.array(scene.camera.calc_matrix_camera(dg,x=1254,y=1254,scale_x=1,scale_y=1)).reshape(-1);assert np.max(abs(projection-np.array(cam['projectionMatrix'])))<1e-7
 def surface(level):
  for mod in ob.modifiers:
   if mod.type=='SUBSURF':mod.levels=mod.render_levels=level
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
  vs=[v.co.copy() for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles];ev.to_mesh_clear();return vs,tris
 low,lt=surface(1);dense,dt=surface(2);tree=BVHTree.FromPolygons(low,lt,all_triangles=True)
 distances=[tree.find_nearest(dense[i])[3] for i in range(0,len(dense),max(1,len(dense)//5000))]
 result=dict(id=row['id'],sourceSha256=before,savedReferenceCameraVerified=True,controlGeometryMaxError=error,continuousCrownTips=8,denseTriangles=len(dt),candidateTriangles=len(lt),sampleCount=len(distances),surfaceDistanceMax=max(distances),surfaceDistanceP95=float(np.percentile(distances,95)),surfaceDistanceMaxOriginalPixels=max(distances)*273.5/4.218205761316873)
 assert result['surfaceDistanceMaxOriginalPixels']<.5
 assert sha(source)==before==meta['sourceSha256'];results.append(result);print(json.dumps(result),flush=True)
(A/'saved-model-check.json').write_text(json.dumps(dict(passed=True,variants=results),indent=2)+'\n',encoding='utf-8')
print('SAVED QUEEN MODELS VERIFIED; NONE MODIFIED',flush=True)

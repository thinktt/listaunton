"""Build actual rook geometry variants and shared-camera profile renders.

Blender --background --python scripts/rook/build_projection_models.py -- --root REPO
Optional --angles 48,52 selects candidates to regenerate. Canonical files are read
only; each invocation of the established builder runs in an isolated build root.
"""
import bpy,bmesh,sys,json,shutil,runpy,hashlib,math
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROOT=Path(args[args.index('--root')+1]) if '--root' in args else Path(__file__).resolve().parents[2]
angles=set(map(int,args[args.index('--angles')+1].split(','))) if '--angles' in args else None
manifest_path=ROOT/'assets/rook-projections/variants.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
preserved=json.loads((ROOT/'assets/rook-projections/baseline-preservation.json').read_text(encoding='utf-8'))['sha256']
for name,expected in preserved.items():assert sha(ROOT/name)==expected,('Changed canonical input',name)
for item in manifest['variants']:
 if angles is not None and item['elevation'] not in angles:continue
 ident=item['id'];dest=ROOT/item['assetDir'];temp=ROOT/'build/rook-projections'/ident
 (temp/'scripts/rook').mkdir(parents=True,exist_ok=True);(temp/'assets/rook').mkdir(parents=True,exist_ok=True)
 shutil.copy2(dest/'profile.json',temp/'scripts/rook/profile.json')
 for name in ['ref.png','original.png','original-white.png','original-alignment.json']:shutil.copy2(ROOT/'assets/rook'/name,temp/'assets/rook'/name)
 sys.argv=[str(ROOT/'scripts/rook/build_rook.py'),'--','--root',str(temp)]
 namespace=runpy.run_path(str(ROOT/'scripts/rook/build_rook.py'),run_name='__main__')
 # Blender's exact Boolean can leave coincident intersection vertices apart by
 # float epsilon at a few angles. Weld only when closure inspection detects it,
 # then save/re-export/re-render that evaluated geometry through the same code.
 body=namespace['body'];bpy.context.view_layer.update()
 ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
 before=sum(not edge.is_manifold for edge in bm.edges);bm.free();ev.to_mesh_clear()
 if before:
  weld=body.modifiers.new('Numerical Boolean seam weld','WELD');weld.merge_threshold=1e-6;bpy.context.view_layer.update()
  ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
  after=sum(not edge.is_manifold for edge in bm.edges);bm.free();ev.to_mesh_clear();assert after==0,(ident,'Boolean seam repair failed',before,after)
  bpy.ops.wm.save_as_mainfile(filepath=str(temp/'models/rook/rook-rebuilt.blend'))
  source=(ROOT/'scripts/rook/build_rook.py').read_text(encoding='utf-8');export=source[source.index('# Export evaluated triangle'):]
  exec(compile(export,str(ROOT/'scripts/rook/build_rook.py')+' [re-export]','exec'),namespace)
  item['numericalSeamWeld']={'threshold_world_units':1e-6,'nonmanifold_edges_before':before,'nonmanifold_edges_after':after}
 model=ROOT/item['model'];model.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(temp/'models/rook/rook-rebuilt.blend',model)
 for name in ['mesh.bin','mesh.json','camera.json','render.png']:shutil.copy2(temp/'assets/rook'/name,dest/name)
 meta=json.loads((dest/'mesh.json').read_text(encoding='utf-8'));graph=bpy.context.evaluated_depsgraph_get();components=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
  count=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
  assert count==0 and volume>0,(ident,ob.name,count,volume)
  components.append({'name':ob.name,'nonmanifold_edges':count,'signed_volume':volume,'vertices':len(bm.verts),'faces':len(bm.faces),'hidden_construction':ob.hide_render})
  bm.free();ev.to_mesh_clear()
 volumes=[c['signed_volume'] for c in components if c['hidden_construction']]
 assert len(components)==5 and len(volumes)==4 and max(volumes)-min(volumes)<1e-7
 item['height']=meta['bounds']['size'][2];item['baseWidth']=meta['bounds']['size'][0];item['heightToBaseWidth']=item['height']/item['baseWidth']
 assert abs(meta['bounds']['min'][2])<1e-6
 # The profile camera and lighting remain identical; image framing never rescales
 # a candidate to its own height or substitutes a camera-only version of the mesh.
 scene=bpy.context.scene;cam=scene.camera;cam.scale=(1,1,1);cam.location=(0,-12,1.95);aim(cam,(0,0,1.95));cam.data.shift_x=0;cam.data.shift_y=0;cam.data.ortho_scale=4.4;cam.data.sensor_fit='VERTICAL'
 scene.render.resolution_x=600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.filepath=str(dest/'profile.png')
 bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();projection=cam.calc_matrix_camera(graph,x=600,y=900)
 pc={'type':'ORTHO','worldToCamera':[float(v) for row in cam.matrix_world.inverted() for v in row],'projectionMatrix':[float(v) for row in projection for v in row],'width':600,'height':900,'orthoScale':4.4,'shiftX':0,'shiftY':0}
 (dest/'profile-camera.json').write_text(json.dumps(pc,indent=2));bpy.ops.render.render(write_still=True)
 validation={'components':components,'sourceSha256':meta['sourceSha256'],'source_hash_matches':sha(model)==meta['sourceSha256'],'renderSha256':sha(dest/'render.png'),'profileSha256':sha(dest/'profile.png'),'cameraSha256':sha(dest/'camera.json'),'equal_merlon_volumes':True,'note':'Evaluated body union and four hidden editable merlons are closed with positive signed volumes; hidden merlons are rotationally equal.'}
 (dest/'validation.json').write_text(json.dumps(validation,indent=2));manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
 print('ROOK_PROJECTION_DONE',ident,item['heightToBaseWidth'],flush=True)
manifest['sharedView']={'center':[0,0,1.95],'orthoHeight':4.4,'distance':12}
manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
for name,expected in preserved.items():assert sha(ROOT/name)==expected,('Canonical changed',name)
print('ALL_ROOK_PROJECTIONS_BUILT',flush=True)

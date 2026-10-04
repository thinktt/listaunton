"""Build/export/render the fitted king candidates without changing the current king.

Run with Blender --background --python this_file.py [-- --root REPO].
Reuses the existing king builder inside isolated, regenerable build folders.
"""
import bpy,bmesh,sys,json,shutil,runpy,hashlib,math
from pathlib import Path
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROOT=Path(args[args.index('--root')+1]) if '--root' in args else Path(__file__).resolve().parents[2]
manifest_path=ROOT/'assets/king-projections/variants.json';manifest=json.loads(manifest_path.read_text())
def aim(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
for item in manifest['variants']:
 ident=item['id'];dest=ROOT/item['assetDir'];temp=ROOT/'build/king-projections'/ident
 (temp/'scripts/king').mkdir(parents=True,exist_ok=True);(temp/'assets/king').mkdir(parents=True,exist_ok=True)
 shutil.copy2(dest/'profile.json',temp/'scripts/king/profile.json')
 for name in ['reference.png','original.png','original-alignment.json']:shutil.copy2(ROOT/'assets/king'/name,temp/'assets/king'/name)
 sys.argv=[str(ROOT/'scripts/king/build_king.py'),'--','--root',str(temp)]
 runpy.run_path(str(ROOT/'scripts/king/build_king.py'),run_name='__main__')
 model=ROOT/item['model'];model.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(temp/'models/king/king-rebuilt.blend',model)
 for name in ['mesh.bin','mesh.json','camera.json','render.png']:shutil.copy2(temp/'assets/king'/name,dest/name)
 meta=json.loads((dest/'mesh.json').read_text());graph=bpy.context.evaluated_depsgraph_get();components=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  ev=ob.evaluated_get(graph);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me)
  count=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
  assert count==0 and volume>0,(ident,ob.name,count,volume)
  components.append({'name':ob.name,'nonmanifold_edges':count,'signed_volume':volume,'vertices':len(bm.verts),'faces':len(bm.faces)})
  bm.free();ev.to_mesh_clear()
 (dest/'validation.json').write_text(json.dumps({'components':components,'sourceSha256':meta['sourceSha256'],'source_hash_matches':hashlib.sha256(model.read_bytes()).hexdigest()==meta['sourceSha256'],'note':'Body and cross are closed editable components; they intersect at the pedestal.'},indent=2))
 item['height']=meta['bounds']['size'][2];item['baseWidth']=meta['bounds']['size'][0];item['heightToBaseWidth']=item['height']/item['baseWidth']
 # Identical board-level orthographic camera, framing and lights across profiles.
 scene=bpy.context.scene;cam=scene.camera;cam.location=(0,-16,3.5);aim(cam,(0,0,3.5));cam.data.shift_x=0;cam.data.shift_y=0;cam.data.ortho_scale=7.6;cam.data.sensor_fit='VERTICAL'
 scene.render.resolution_x=600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.filepath=str(dest/'profile.png')
 bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();projection=cam.calc_matrix_camera(graph,x=600,y=900)
 pc={'type':'ORTHO','worldToCamera':[float(v) for row in cam.matrix_world.inverted() for v in row],'projectionMatrix':[float(v) for row in projection for v in row],'width':600,'height':900,'orthoScale':7.6,'shiftX':0,'shiftY':0}
 (dest/'profile-camera.json').write_text(json.dumps(pc,indent=2));bpy.ops.render.render(write_still=True)
 print('PROJECTION_DONE',ident,item['heightToBaseWidth'],flush=True)
manifest['sharedView']={'center':[0,0,3.45],'orthoHeight':7.6,'distance':16}
manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
print('ALL_PROJECTIONS_BUILT',flush=True)

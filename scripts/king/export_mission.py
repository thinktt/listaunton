"""Export exact evaluated triangle corners, normals, atlas UVs and saved camera."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy,bmesh
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/args.source;out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True);sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest();before=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene
sys.path.insert(0,str(Path(__file__).resolve().parent))
from render_regions import controls
from validate_render_regions import check as check_regions
receiver_validation=check_regions(s)
objects=sorted(controls(s),key=lambda ob:ob.name);assert len(objects)==2
for ob in objects:
    for modifier in ob.modifiers:
        if modifier.type=='SUBSURF':modifier.levels=modifier.render_levels
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get();blocks=[];parts=[]
for ob in objects:
    ev=ob.evaluated_get(graph);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=graph);me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
    nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert nonmanifold==0 and volume>0
    uv=me.uv_layers.get('Pigment atlas');assert uv is not None
    rows=[];normal_matrix=ob.matrix_world.to_3x3().inverted().transposed()
    for tri in me.loop_triangles:
        for vi,li in zip(tri.vertices,tri.loops):
            pos=ob.matrix_world@me.vertices[vi].co;normal=(normal_matrix@me.corner_normals[li].vector).normalized()
            rows.append(tuple(pos)+tuple(normal)+tuple(uv.data[li].uv))
    blocks.append(np.array(rows,dtype='<f4'));parts.append({'name':ob.name,'vertices':len(me.vertices),'triangleCount':len(me.loop_triangles),'nonmanifold_edges':nonmanifold,'signed_volume':volume})
    bm.free();ev.to_mesh_clear()
corners=np.concatenate(blocks);vertices,inverse=np.unique(corners,axis=0,return_inverse=True);vertices=vertices.astype('<f4');indices=inverse.astype('<u4')
assert np.array_equal(vertices[indices],corners);assert np.isfinite(vertices).all();assert np.allclose(np.linalg.norm(vertices[:,3:6],axis=1),1,atol=2e-6)
raw=vertices.tobytes()+indices.tobytes();(out/'mesh.bin').write_bytes(raw);assert np.array_equal(np.frombuffer(raw,dtype='<f4',count=vertices.size).reshape(-1,8),vertices)
cam=s.camera;axis=cam.matrix_world.to_3x3()@Vector((0,0,1));elevation=math.degrees(math.asin(axis.z));assert cam.data.type=='ORTHO' and abs(elevation-54)<.001
W=s.render.resolution_x;H=s.render.resolution_y;P=cam.calc_matrix_camera(graph,x=W,y=H)
camera={'type':'ORTHO','worldToCamera':[float(v) for row in cam.matrix_world.inverted() for v in row],'projectionMatrix':[float(v) for row in P for v in row],'width':W,'height':H,'orthoScale':cam.data.ortho_scale,'shiftX':cam.data.shift_x,'shiftY':cam.data.shift_y,'elevationDegrees':elevation}
lo=vertices[:,:3].min(0);hi=vertices[:,:3].max(0)
meta={'vertexCount':len(vertices),'indexCount':len(indices),'triangleCount':len(indices)//3,'vertexStrideBytes':32,'uvOffsetBytes':24,'uvLayer':'Pigment atlas','vertexByteLength':vertices.nbytes,'indexByteOffset':vertices.nbytes,'totalByteLength':len(raw),'bounds':{'min':lo.tolist(),'max':hi.tolist(),'size':(hi-lo).tolist(),'center':((hi+lo)/2).tolist()},'parts':parts,'sourceSha256':before,'referenceCamera':camera,'texture':s['king_pigment_atlas'],'textureSha256':sha(ROOT/s['king_pigment_atlas'])}
assert sha(source)==before
validation={'components':parts,'sourceSha256':before,'source_hash_matches':True,'elevationDegrees':elevation,'cameraOrthographic':True,'exactCornerPositionNormalUvRoundtrip':True,'allAttributesFinite':True,'allNormalsUnit':True,'packedPigment':bool(bpy.data.images[s.get('king_pigment_image','King pigment atlas')].packed_file),'note':'Body and cross remain separate closed intersecting components. Viewer lighting is approximate.'}
validation['renderReceivers']=receiver_validation
for name,value in [('mesh.json',meta),('camera.json',camera),('validation.json',validation)]: (out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
print(json.dumps(validation,indent=2));print('KING_EXPORT_DONE',meta['triangleCount'],len(vertices),len(raw))

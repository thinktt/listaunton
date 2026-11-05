"""Export exact evaluated bishop positions, normals and pigment UVs."""
import argparse,hashlib,json,sys,math
from pathlib import Path
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--model',default='models/bishop/bishop-rebuilt.blend');p.add_argument('--out',default='assets/bishop');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
model=ROOT/a.model;bpy.ops.wm.open_mainfile(filepath=str(model),load_ui=False)
s=bpy.context.scene;bpy.context.view_layer.update();g=bpy.context.evaluated_depsgraph_get();blocks=[];parts=[];count=0
for ob in [o for o in s.objects if o.type=='MESH' and not o.hide_render]:
    ev=ob.evaluated_get(g);me=ev.to_mesh();me.calc_loop_triangles();uv=me.uv_layers['Wood atlas'];block=[]
    for tri in me.loop_triangles:
        for vi,li in zip(tri.vertices,tri.loops):block.append(tuple(ob.matrix_world@me.vertices[vi].co)+tuple((ob.matrix_world.to_3x3()@me.corner_normals[li].vector).normalized())+(tuple(uv.data[li].uv) if tri.material_index==0 else (-1.,-1.)))
    ar=np.array(block,dtype='<f4');assert np.isfinite(ar).all();blocks.append(ar);parts.append({'name':ob.name,'vertexCount':len(ar),'indexCount':len(ar),'indexOffset':count,'vertexOffset':count,'triangleCount':len(ar)//3});count+=len(ar);ev.to_mesh_clear()
ar=np.concatenate(blocks);indices=np.arange(len(ar),dtype='<u4');raw=ar.tobytes()+indices.tobytes();lo=ar[:,:3].min(0);hi=ar[:,:3].max(0)
cam=s.camera;W=s.render.resolution_x;H=s.render.resolution_y;projection=cam.calc_matrix_camera(g,x=W,y=H)
camera={'type':'ORTHO','worldToCamera':[float(v) for row in cam.matrix_world.inverted() for v in row],'projectionMatrix':[float(v) for row in projection for v in row],'width':W,'height':H,'orthoScale':cam.data.ortho_scale,'shiftX':cam.data.shift_x,'shiftY':cam.data.shift_y,'elevationDegrees':54}
assert abs(math.degrees(math.asin((cam.matrix_world.to_3x3()@__import__('mathutils').Vector((0,0,1))).z))-54)<1e-4
texture=ROOT/'assets/bishop/bishop-boxwood-albedo.png'
meta={'vertexCount':len(ar),'indexCount':len(ar),'triangleCount':len(ar)//3,'vertexStrideBytes':32,'vertexByteLength':ar.nbytes,'indexByteOffset':ar.nbytes,'totalByteLength':len(raw),'bounds':{'min':lo.tolist(),'max':hi.tolist(),'size':(hi-lo).tolist(),'center':((hi+lo)/2).tolist()},'parts':parts,'sourceSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'referenceCamera':camera,'material':{'texture':'assets/bishop/bishop-boxwood-albedo.png','textureSha256':hashlib.sha256(texture.read_bytes()).hexdigest(),'uvLayer':'Wood atlas','lighting':'Approximate browser studio lighting; fixed overlay uses the actual saved Cycles render.'}}
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True);(out/'mesh.bin').write_bytes(raw);(out/'mesh.json').write_text(json.dumps(meta,indent=2)+'\n');(out/'camera.json').write_text(json.dumps(camera,indent=2)+'\n')
print('BISHOP_TEXTURED_MESH_EXPORTED',meta['triangleCount'],meta['sourceSha256'])

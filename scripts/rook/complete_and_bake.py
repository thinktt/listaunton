"""Complete unseen rook pigment and bake only color to editable-control UVs."""
from pathlib import Path
import sys,json,hashlib,math
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'build/rook-mission/003-separated-light-pigment/rook.blend'
out=ROOT/'build/rook-mission/004-continuous-atlas';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;gpu(s)
objects=[o for o in s.objects if o.type=='MESH'];body=next(o for o in objects if not o.hide_render)
mat=body.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF']
pigment=n['Rook inferred diffuse pigment'].image;confidence=n['Rook pigment confidence'].image
w,h=pigment.size
rgb=np.array(pigment.pixels[:],np.float32).reshape(h,w,4)[:,:,:3]
conf=np.array(confidence.pixels[:],np.float32).reshape(h,w,4)[:,:,0]
filled=rgb.copy();valid=conf>.70;xs=np.arange(w);good_rows=[]
for y in range(h):
    ix=np.where(valid[y])[0]
    if len(ix)>8:
        good_rows.append(y)
        for c in range(3):filled[y,:,c]=np.interp(xs,ix,rgb[y,ix,c])
assert good_rows
for y in range(h):
    if y not in good_rows:
        nearest=good_rows[np.argmin(np.abs(np.array(good_rows)-y))];filled[y]=filled[nearest]
im=bpy.data.images.new('Rook completed diffuse source',width=w,height=h,alpha=False,float_buffer=True)
im.colorspace_settings.name='Linear Rec.709';im.pixels.foreach_set(np.dstack([filled,np.ones((h,w),np.float32)]).reshape(-1))
im.file_format='OPEN_EXR';im.filepath_raw=str(out/'completed-pigment.exr');im.save();im.pack()
def mathnode(op,*values):
    node=n.new('ShaderNodeMath');node.operation=op
    for i,v in enumerate(values):
        if isinstance(v,(int,float)):node.inputs[i].default_value=v
        else:l.new(v,node.inputs[i])
    return node.outputs[0]
coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],sep.inputs[0])
x,y,z=[sep.outputs[k] for k in ['X','Y','Z']]
xx=mathnode('MULTIPLY',x,.65)
rr=mathnode('ADD',mathnode('MULTIPLY',x,x),mathnode('MULTIPLY',y,y))
yy=mathnode('MULTIPLY',mathnode('SQRT',mathnode('MAXIMUM',mathnode('SUBTRACT',rr,mathnode('MULTIPLY',xx,xx)),0)),-1)
fold=n.new('ShaderNodeCombineXYZ');l.new(xx,fold.inputs[0]);l.new(yy,fold.inputs[1]);l.new(z,fold.inputs[2])
uv=n.new('ShaderNodeCombineXYZ');coeff=json.loads((source.parent/'report.json').read_text())['projection']
for dim in [0,1]:
    dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=coeff[dim][:3];l.new(fold.outputs[0],dot.inputs[0]);l.new(mathnode('ADD',dot.outputs['Value'],coeff[dim][3]),uv.inputs[dim])
tex=n.new('ShaderNodeTexImage');tex.image=im;tex.extension='EXTEND';tex.name='Inferred continuous rear wood';l.new(uv.outputs[0],tex.inputs[0])
l.new(tex.outputs['Color'],n['Rook bounded reference pigment'].inputs[1])
# Assign separate, non-overlapping islands to the original lathe and merlons.
co=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,128,3)
r=np.linalg.norm(co[:,:,:2],axis=2).mean(1);zz=co[:,:,2].mean(1)
arc=np.r_[0,np.cumsum(np.hypot(np.diff(r),np.diff(zz)))];arc/=arc[-1]
layer=body.data.uv_layers.new(name='Pigment atlas');body.data.uv_layers.active=layer;layer.active_render=True
for face in body.data.polygons:
    us=[(body.data.loops[li].vertex_index%128)/128 for li in face.loop_indices]
    seam=len(us)==4 and max(us)-min(us)>.5
    for li,u in zip(face.loop_indices,us):
        layer.data[li].uv=(.01+.74*(u+(1 if seam and u<.5 else 0)),.01+.98*arc[body.data.loops[li].vertex_index//128])
for ob in s.objects:ob.select_set(False)
for j,ob in enumerate(sorted([o for o in objects if o!=body],key=lambda o:o.name)):
    ob.hide_set(False);ob.select_set(True);bpy.context.view_layer.objects.active=ob
    layer=ob.data.uv_layers.new(name='Pigment atlas');ob.data.uv_layers.active=layer;layer.active_render=True
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.151917,island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
    layer=ob.data.uv_layers['Pigment atlas'];a=np.array([v.uv[:] for v in layer.data],np.float32);a[:,0]=.78+.21*a[:,0];a[:,1]=.01+j*.245+.225*a[:,1];layer.data.foreach_set('uv',a.reshape(-1));ob.data.update();ob.select_set(False);ob.hide_set(True)
body.hide_set(False);body.select_set(True);bpy.context.view_layer.objects.active=body
atlas=bpy.data.images.new('Rook pigment atlas v1',width=3072,height=3072,alpha=False);atlas.colorspace_settings.name='sRGB'
target=n.new('ShaderNodeTexImage');target.image=atlas;target.name='Baked rook pigment'
for node in n:node.select=False
target.select=True;n.active=target
output=n['Material Output'];emit=n.new('ShaderNodeEmission');l.new(bs.inputs['Base Color'].links[0].from_socket,emit.inputs['Color']);l.new(emit.outputs[0],output.inputs['Surface'])
s.cycles.samples=1;s.render.bake.margin=8;bpy.ops.object.bake(type='EMIT',use_clear=True)
atlas.file_format='PNG';atlas.filepath_raw=str(out/'pigment.png');atlas.save();atlas.pack()
l.new(bs.outputs[0],output.inputs['Surface']);n.remove(emit)
uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map='Pigment atlas';l.new(uvnode.outputs[0],target.inputs[0]);l.new(target.outputs['Color'],bs.inputs['Base Color'])
s['rook_pigment_image']=atlas.name;s['rook_pigment_atlas_bakes_lighting']=False
s['rook_pigment_uv']='Pigment atlas';s['rook_pigment_atlas']='build/rook-mission/004-continuous-atlas/pigment.png'
s.cycles.samples=64;s.render.resolution_percentage=100;s.render.filepath=str(out/'wood.png')
before=np.array(atlas.pixels[:],np.float32);atlasname=atlas.name
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s)
error=float(np.max(np.abs(before-np.array(bpy.data.images[atlasname].pixels[:],np.float32))));assert error<=1/255+.0001,error
bpy.ops.render.render(write_still=True)
cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.ortho_scale=4.5;cam.location=(0,-12,1.4);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_percentage=60;s.render.filepath=str(out/'side.png');bpy.ops.render.render(write_still=True)
cam.location=(0,12,1.4);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(out/'rear.png');bpy.ops.render.render(write_still=True)
(out/'report.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'atlas_sha256':hashlib.sha256((out/'pigment.png').read_bytes()).hexdigest(),'packed_roundtrip_max_error':error,'atlas_bakes_lighting':False,'hidden_finish':'Folded front-surface pigment with row-interpolated low-confidence regions; inferred not original evidence','status':'trial, not promoted'},indent=2))
print('ROOK_ATLAS_COMPLETE')

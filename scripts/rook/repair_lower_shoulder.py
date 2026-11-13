"""Replace contaminated pigment bands using adjacent wood sampled in atlas space."""
from pathlib import Path
import sys,json,hashlib,math
import bpy,numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
source=ROOT/'build/rook-mission/025-separated-edge-rig/rook.blend'
for variant,strip in [('026-lower-shoulder-pigment',False)]:
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;gpu(s);body=next(o for o in s.objects if o.get('rook_editable_control'));mat=body.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF'];original=bs.inputs['Base Color'].links[0].from_socket;atlas=original.node.image
    co=np.array([v.co[:] for v in body.data.vertices]).reshape(-1,128,3);r=np.linalg.norm(co[:,:,:2],axis=2).mean(1);z=co[:,:,2].mean(1);arc=np.r_[0,np.cumsum(np.hypot(np.diff(r),np.diff(z)))];v=.01+.98*arc/arc[-1]
    uv=n.new('ShaderNodeUVMap');uv.uv_map='Pigment atlas';sep=n.new('ShaderNodeSeparateXYZ');l.new(uv.outputs[0],sep.inputs[0])
    def op(kind,*args):
        ob=n.new('ShaderNodeMath');ob.operation=kind
        for i,a in enumerate(args):
            if isinstance(a,(int,float,np.floating)):ob.inputs[i].default_value=float(a)
            else:l.new(a,ob.inputs[i])
        return ob.outputs[0]
    result=original;bands=[]
    for name,lo,hi,donorlo,donorhi in [('lower-shoulder',15,21,14,17)]:
        start,end=float(v[lo]),float(v[hi]);a,b=float(v[donorlo]),float(v[donorhi]);t=op('DIVIDE',op('SUBTRACT',sep.outputs['Y'],start),end-start)
        sample=n.new('ShaderNodeCombineXYZ');l.new(sep.outputs['X'],sample.inputs[0]);l.new(op('ADD',a,op('MULTIPLY',t,b-a)),sample.inputs[1])
        tex=n.new('ShaderNodeTexImage');tex.image=atlas;tex.name='Adjacent wood '+name;l.new(sample.outputs[0],tex.inputs[0])
        # Smooth ramps avoid introducing a new hard pigment boundary.
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='EASE';ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1]);ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=(0,0,0,1)
        for pos,c in [(.18,1),(.82,1),(1,0)]:e=ramp.color_ramp.elements.new(pos);e.color=(c,c,c,1)
        l.new(t,ramp.inputs[0]);gate=op('MULTIPLY',ramp.outputs['Color'],op('LESS_THAN',sep.outputs['X'],.76))
        mix=n.new('ShaderNodeMixRGB');mix.name='Repair pigment '+name;l.new(gate,mix.inputs[0]);l.new(result,mix.inputs[1]);l.new(tex.outputs['Color'],mix.inputs[2]);result=mix.outputs[0]
        bands.append({'name':name,'destination_v':[start,end],'source_v':[a,b],'control_rows':[lo,hi],'donor_rows':[donorlo,donorhi]})
    l.new(result,bs.inputs['Base Color'])
    if strip:
        for ob in s.objects:
            if ob.type=='LIGHT' and ob.name.startswith('Rook '):ob.data.energy=0
        d=bpy.data.lights.new('Rook strip','AREA');d.shape='RECTANGLE';d.size=8;d.size_y=.12;d.energy=450
        ob=bpy.data.objects.new(d.name,d);s.collection.objects.link(ob);ob.location=(0,-4,5);ob.rotation_euler=(Vector((0,0,1.3))-ob.location).to_track_quat('-Z','Y').to_euler();ob.visible_diffuse=False
    out=ROOT/'build/rook-mission'/variant;out.mkdir(parents=True,exist_ok=True);s.cycles.samples=64;s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'));bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
    (out/'parameters.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'model_sha256':hashlib.sha256((out/'rook.blend').read_bytes()).hexdigest(),'bands':bands,'strip':strip,'method':'Real Principled material. UV-space resampling of adjacent existing pigment; source atlas and references unchanged.'},indent=2)+'\n')
    cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=4.3;cam.location=(0,-12,1.4);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=600;s.render.resolution_y=900;s.render.filepath=str(out/'side.png');bpy.ops.render.render(write_still=True);print('BAND_REPAIR_DONE',variant,flush=True)

"""Prove a lower-base lighting checkpoint preserves geometry, finish and camera."""
from pathlib import Path
import argparse,hashlib,json,sys,math
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mission_trial import ROOT
from render_regions import controls
from validate_render_regions import check as check_receivers

def digest(values):
    return hashlib.sha256(np.asarray(values,dtype='<f4').tobytes()).hexdigest()

def value(x):
    if isinstance(x,(float,int,bool,str)):return x
    try:return list(x)
    except TypeError:return str(type(x))

def graph(tree,normalize_relief=False):
    result=dict(nodes={n.name:dict(type=n.bl_idname,inputs={s.identifier:value(s.default_value) for s in n.inputs if hasattr(s,'default_value')},image=n.image.name if hasattr(n,'image') and n.image else None,attribute=getattr(n,'attribute_name',None)) for n in tree.nodes},links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links))
    if normalize_relief:
        socket=tree.nodes['Fine varnish relief'].inputs['Strength'];assert len(socket.links)==1
        mix=socket.links[0].from_node;assert mix.bl_idname=='ShaderNodeMixRGB' and mix.blend_type=='MIX'
        attr=mix.inputs[0].links[0].from_node;assert attr.bl_idname=='ShaderNodeAttribute' and attr.attribute_name=='Lower flare relief mask'
        strength=normalize_relief[0];assert np.allclose(mix.inputs[2].default_value,(strength,strength,strength,1),atol=1e-8)
        original=mix.inputs[1].links[0];removed={mix.name,attr.name}
        for name in removed:result['nodes'].pop(name)
        result['links']=[l for l in result['links'] if l[0] not in removed and l[2] not in removed]
        result['links'].append((original.from_node.name,original.from_socket.identifier,'Fine varnish relief',socket.identifier));result['links'].sort()
    return result

def snapshot(path,normalize_relief=False):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/path),load_ui=False);s=bpy.context.scene;objects={}
    for ob in controls(s):
        attributes={a.name:digest([v.value for v in a.data]) for a in ob.data.attributes if a.data_type=='FLOAT' and a.domain in ('POINT','CORNER') and not a.name.startswith('.') and a.name!='Lower flare relief mask'}
        if normalize_relief:
            expected=np.zeros(len(ob.data.vertices),dtype=np.float32)
            if 'body' in ob.name:
                _,start,end=normalize_relief;ring=np.arange(len(expected))//96;t=np.clip((ring-start)/(end-start),0,1);expected[:]=1-t*t*(3-2*t);t=np.clip((ring-10)/2,0,1);expected*=t*t*(3-2*t)
            actual=np.array([v.value for v in ob.data.attributes['Lower flare relief mask'].data]);assert np.array_equal(expected,actual)
        objects[ob.name]=dict(positions=digest([v.co[:] for v in ob.data.vertices]),faces=[list(p.vertices) for p in ob.data.polygons],matrix=[v for row in ob.matrix_world for v in row],uv={l.name:digest([v.uv[:] for v in l.data]) for l in ob.data.uv_layers},attributes=attributes,subdivision=[(m.type,m.levels,m.render_levels) for m in ob.modifiers if m.type=='SUBSURF'],material=graph(ob.data.materials[0].node_tree,normalize_relief))
    image=bpy.data.images[s.get('king_pigment_image','King pigment atlas')]
    pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
    cam=s.camera;lights={}
    for ob in s.objects:
        if ob.type!='LIGHT':continue
        data=ob.data;members=ob.light_linking.receiver_collection
        lights[ob.name]=dict(type=data.type,energy=data.energy,color=list(data.color),matrix=[v for row in ob.matrix_world for v in row],diffuse=ob.visible_diffuse,glossy=ob.visible_glossy,size=getattr(data,'size',None),size_y=getattr(data,'size_y',None),radius=getattr(data,'shadow_soft_size',None),cone=getattr(data,'spot_size',None),receivers=sorted(o.get('king_render_region',o.name) for o in members.objects) if members else None)
    state=dict(objects=objects,pigment_pixels=digest(pixels),pigment_packed_sha256=hashlib.sha256(bytes(image.packed_file.data)).hexdigest(),camera=dict(matrix=[v for row in cam.matrix_world for v in row],kind=cam.data.type,scale=cam.data.ortho_scale,shift=[cam.data.shift_x,cam.data.shift_y],size=[s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage],aspect=[s.render.pixel_aspect_x,s.render.pixel_aspect_y]),color_management=[s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma],world=graph(s.world.node_tree),light_paths={k:getattr(s.cycles,k) for k in ['max_bounces','diffuse_bounces','glossy_bounces','sample_clamp_indirect']})
    return state,lights,check_receivers(s)

def main(before,after,output,lower_relief=False,upper_cone=None,split_flare=False):
    a,old,_=snapshot(before);b,new,receivers=snapshot(after,lower_relief)
    assert a==b,'Geometry, UVs, material, packed pigment, camera or world changed'
    disabled=['Base lower left focused','Base lower center focused','Base lower right focused']
    for name,light in old.items():
        expected=dict(light)
        if name in disabled:expected['energy']=0
        if name=='Base upper focused' and upper_cone is not None:expected['cone']=float(np.float32(math.radians(upper_cone)))
        if split_flare and expected['receivers'] and 'flare' in expected['receivers']:
            expected['receivers']=sorted([r for r in expected['receivers'] if r!='flare']+(['upper-flare'] if name=='Base upper focused' else ['lower-flare','upper-flare']))
        assert new[name]==expected,('Unexpected old-light change',name)
    added=sorted(set(new)-set(old));assert added==['Base lower shaped 03','Base lower shaped 04','Base lower shaped 05']
    for name in added:assert new[name]['receivers']==(['lower-flare'] if split_flare else ['flare']) and not new[name]['diffuse'] and new[name]['glossy']
    report=dict(before=before,after=after,editableGeometryAllUvsPigmentCameraAndWorldExact=True,materialExactApartFromDeclaredLowerRelief=bool(lower_relief),materialFullyExact=not lower_relief,lowerRelief={'strength':lower_relief[0],'lowerFade':[10,12],'upperFade':list(lower_relief[1:])} if lower_relief else None,editedUpperConeDegrees=upper_cone,splitFlareAtRing17=split_flare,allOtherLightSettingsExact=True,lightPathsUnchanged=b['light_paths'],disabledLights=disabled,addedLights={n:new[n] for n in added},packedPigmentSha256=b['pigment_packed_sha256'],renderReceivers=receivers)
    out=ROOT/output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('KING_BASE_LIGHT_SCOPE_PASS')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before');p.add_argument('after');p.add_argument('output');p.add_argument('--lower-relief',action='store_true');p.add_argument('--relief-strength',type=float,default=.02);p.add_argument('--upper-fade',nargs=2,type=float,default=[18,22]);p.add_argument('--upper-cone',type=float);p.add_argument('--split-flare',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);main(a.before,a.after,a.output,(a.relief_strength,*a.upper_fade) if a.lower_relief else False,a.upper_cone,a.split_flare)

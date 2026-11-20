"""Install, reopen and inspect the pigment-only R14A trial; paths relative to this file."""
from pathlib import Path
import hashlib,json,math,sys
import bpy,numpy as np
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path.insert(0,str(R/'scripts/knight'))
from mission_scene import configure_render,render,save_model,use_side_camera,visible_meshes,sha
PARENT='eaecb543e309c713db12fc83888bb2ffc0142686a06917ee6c76d24e7d2b2188'
PIG='1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b'
def opened(f):
    bpy.ops.wm.open_mainfile(filepath=str(D/f),load_ui=False)
    return bpy.context.scene
def tex(s):return s.objects['Knight | swept rounded mane'].active_material.node_tree.nodes['Knight delivered albedo'].image
def stamp(s):
    parts={}
    for ob in visible_meshes(s):
        m=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=m.to_mesh();h=hashlib.sha256()
        for collection,key,columns,dtype in [(me.vertices,'co',3,np.float32),(me.loops,'vertex_index',1,np.int32),(me.uv_layers['Knight wood atlas'].data,'uv',2,np.float32),(me.polygons,'material_index',1,np.int32)]:
            a=np.empty((len(collection),columns),dtype);collection.foreach_get(key,a.ravel());h.update(a.tobytes())
        h.update(np.array(m.matrix_world).tobytes());parts[ob.name]=[h.hexdigest(),len(me.vertices),len(me.polygons),[slot.material.name for slot in ob.material_slots]];m.to_mesh_clear()
    lights={ob.name:[list(v for row in ob.matrix_world for v in row),ob.data.type,ob.data.energy,list(ob.data.color),ob.hide_render,getattr(ob.data,'size',0),getattr(ob.data,'size_y',0)] for ob in s.objects if ob.type=='LIGHT'}
    mat={}
    for material in sorted({sl.material for ob in visible_meshes(s) for sl in ob.material_slots},key=lambda v:v.name):
        nodes=material.node_tree.nodes;props=[]
        for n in nodes:
            inputs=[]
            for i in n.inputs:
                w=getattr(i,'default_value',None)
                if isinstance(w,(int,float,bool,str)) or w is None:default=w
                elif hasattr(w,'__len__'):default=list(w)
                else:default=str(w.name) if hasattr(w,'name') else None
                inputs.append((i.name,default,[(a.from_node.name,a.from_socket.name) for a in i.links]))
            props.append((n.name,n.type,inputs))
        mat[material.name]=hashlib.sha256(json.dumps(props,sort_keys=True).encode()).hexdigest()
    cam=s.camera
    return {'meshes':parts,'lights':lights,'material_nodes_inputs_and_links':mat,'camera':[list(q for row in cam.matrix_world for q in row),cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y]}
def install(s):
    a=tex(s);assert hashlib.sha256(bytes(a.packed_file.data)).hexdigest()==PIG
    new=bpy.data.images.load(str(D/'pigment.png'),check_existing=False);new.colorspace_settings.name='sRGB'
    new.name='Knight walnut | crosscut billet 014-A';new.pack()
    assert hashlib.sha256(bytes(new.packed_file.data)).hexdigest()==sha(D/'pigment.png')
    new.filepath='//../../assets/knight/wood-atlas-improvement-014-A.png'
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image==a:n.image=new
    if a.users==0:bpy.data.images.remove(a)
    s['knight_atlas_sha256']=sha(D/'pigment.png')
def crop(s):
    side=s.render.resolution_x
    s.render.use_border=True;s.render.use_crop_to_border=False
    s.render.border_min_x=145/side;s.render.border_max_x=390/side;s.render.border_min_y=1-704/side;s.render.border_max_y=1-340/side
def flat(s,kind):
    if kind=='neutral':
        clay=bpy.data.materials.new('R14 matched grey clay')
        clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF')
        bs.inputs['Base Color'].default_value=(.22,.22,.22,1);bs.inputs['Roughness'].default_value=.54
        for ob in visible_meshes(s):
            for slot in ob.material_slots:slot.material=clay
        for ob in s.objects:
            if ob.type=='LIGHT':ob.hide_render=True
        s.world=bpy.data.worlds.new('R14 clay world');s.world.use_nodes=True
        bg=s.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(1,1,1,1);bg.inputs['Strength'].default_value=.26
        for sign in (-1,1):
            light=bpy.data.lights.new('R14 clay softbox','AREA');light.energy=510;light.shape='DISK';light.size=4.4
            ob=bpy.data.objects.new(light.name,light);s.collection.objects.link(ob);ob.location=(2.,sign*5.2,7.9)
            ob.rotation_euler=(Vector((-.28,0,3.2))-ob.location).to_track_quat('-Z','Y').to_euler()
        return
    for m in {sl.material for ob in visible_meshes(s) for sl in ob.material_slots}:
        bs=m.node_tree.nodes.get('Principled BSDF');base=bs.inputs['Base Color']
        if kind=='albedo':
            em=m.node_tree.nodes.new('ShaderNodeEmission');m.node_tree.links.new(base.links[0].from_socket,em.inputs['Color']);out=next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output);m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
        else:
            for a in list(base.links):m.node_tree.links.remove(a)
            base.default_value=(.12,.12,.12,1)
def camera(s,az,elev=12):
    a,e=map(math.radians,(az,elev));cam=s.camera;t=Vector((-.1,0,2.64))
    cam.data.ortho_scale=6.;cam.data.shift_x=cam.data.shift_y=0.
    cam.location=t+Vector((12*math.sin(a)*math.cos(e),-12*math.cos(a)*math.cos(e),12*math.sin(e)));cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
def previews():
    for k in ['studio','albedo']:
        s=opened('parent.blend');install(s);configure_render(s,36);crop(s)
        if k=='albedo':flat(s,k)
        render(s,D/('preview-'+k+'.png'))
def preview_orbit():
    s=opened('parent.blend');install(s);configure_render(s,24)
    s.render.resolution_x=s.render.resolution_y=440
    for name,az in [('near',10.3),('rear-quarter',-39.7),('back',-79.7),('far-quarter',-119.7),('far',190.3)]:
        camera(s,az);render(s,D/('trial-'+name+'.png'))
def freeze():
    assert sha(D/'parent.blend')==PARENT
    s=opened('parent.blend');control=stamp(s);install(s);configure_render(s,144)
    save_model(s,D/'knight.blend')
    s=opened('knight.blend');current=stamp(s);assert control==current
    packed=hashlib.sha256(bytes(tex(s).packed_file.data)).hexdigest();assert packed==sha(D/'pigment.png')
    (D/'native-check.json').write_text(json.dumps({'parent_sha256':PARENT,'scene_sha256':sha(D/'knight.blend'),'packed_sha256':packed,'identical_parent_and_candidate':control},indent=2)+'\n')
    print('FROZEN',sha(D/'knight.blend'),packed,flush=True)
def publish_pair():
    s=opened('knight.blend');configure_render(s,144);render(s,D/'wood.png');use_side_camera(s);render(s,D/'wood-side.png')
    (D/'renders.json').write_text(json.dumps({'samples':144,'fixed_sha256':sha(D/'wood.png'),'side_sha256':sha(D/'wood-side.png'),'rendered_source_sha256':sha(D/'knight.blend'),'device':json.loads(s['knight_render_device'])},indent=2)+'\n')
def turn(kinds=('wood','albedo','neutral','uniform')):
    for k in kinds:
        s=opened('knight.blend');configure_render(s,22)
        if k in ('albedo','neutral'):flat(s,k)
        if k=='uniform':
            for ob in s.objects:
                if ob.type=='LIGHT':ob.hide_render=True
            world=bpy.data.worlds.new('Diffuse all-direction inspection')
            world.use_nodes=True;s.world=world
            bg=world.node_tree.nodes.get('Background')
            bg.inputs['Color'].default_value=(1,1,1,1);bg.inputs['Strength'].default_value=.9
        if k in ('albedo','neutral'):
            crop(s);render(s,D/(k+'-fixed.png'));s.render.use_border=False
        s.render.resolution_x=s.render.resolution_y=480
        for name,az in [('near',10.3),('rear-quarter',-39.7),('back',-79.7),('far-quarter',-119.7),('far',190.3)]:
            camera(s,az);render(s,D/(k+'-'+name+'.png'))
if __name__=='__main__':
    mode=sys.argv[-1]
    {'preview':previews,'preview-orbit':preview_orbit,'freeze':freeze,'render':publish_pair,'turn':turn,'neutral':lambda:turn(('neutral',))}[mode]()

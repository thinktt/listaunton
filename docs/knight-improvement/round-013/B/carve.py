"""Carve the two eyes and the lower lid into one continuous cheek envelope."""
from pathlib import Path
import hashlib,json,math,sys
import bpy,numpy as np
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path[:0]=[str(D),str(R/'scripts/knight')]
from orbital import AX,UP,O as CENTER,chart,pose,rest_coords,posed,world_vertices,HEAD,BUILD
from evidence import load,flat,flat_views,studio
from diagnostics import diagnostics
from mission_scene import configure_render,render,save_model,sha,use_side_camera
PARENT='739bf4c1e3671770de868593ec10135c5345417bd80c043ee04ee7dea86efe4c'
PIGMENT='1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b'
NET=np.load(D/'field-parent.npz')
U,V,A=NET['u'],NET['v'],NET['surfaces']
UU,VV=np.meshgrid(U,V)
LOW=np.array(json.loads((D/'lower-parent.json').read_text()))
BROW=np.array(json.loads((D/'brow-parent.json').read_text()))
DESIGNS=[
    # envelope fusion, preserved inner crescent, substrate relief factor,
    # support plane strength, transverse slope, brow tail depth, early nasal turn
    (.83,.75,.35,.45,-.46,.015,.006),
    (.95,.68,.20,.72,-.45,.025,.010),
    (.91,.86,.25,.62,-.34,.022,.015),
    (.98,.54,.15,.78,-.40,.032,.012),
    (.84,.85,.45,.42,-.42,.014,.006,.014,0),
    (.85,.90,.38,.50,-.42,.016,.006,.017,1),
    (.90,.81,.35,.55,-.40,.014,.010,.023,2),
    (.91,.89,.32,.48,-.38,.021,.009,.018,3),
    (.83,.88,.43,.48,-.42,.013,.006,.018,4,.165,.24),
    (.86,.89,.42,.49,-.42,.014,.007,.022,5,.214,.26),
    (.83,.88,.44,.50,-.42,.015,.006,.020,6,.200,.33),
    (.80,.90,.50,.51,-.38,.011,.005,.025,7,.159,.30,.015),
    (.85,.90,.46,.54,-.39,.009,.005,.024,8,.163,.33,.020),
    (.83,.89,.48,.52,-.40,.011,.006,.028,9,.136,.26,.022),
    (.83,.89,.48,.52,-.40,.011,.006,.028,10,.136,.26,.022),
    (.83,.89,.48,.52,-.40,.011,.006,.028,11,.136,.26,.022),
    (.83,.89,.48,.52,-.40,.011,.006,.028,12,.136,.26,.022),
    (.83,.89,.48,.52,-.40,.011,.006,.028,13,.136,.26,.022)]
def ease(t):
    t=np.clip(t,0.,1.);return t*t*(3.-2.*t)
def bell(t,w):return np.exp(-(t/w)**2)
def smooth(a,sigma,axis):
    radius=int(np.ceil(3.5*sigma));q=np.arange(-radius,radius+1)
    ker=np.exp(-.5*(q/sigma)**2);ker/=ker.sum()
    return np.apply_along_axis(lambda v:np.convolve(np.pad(v,radius,mode='edge'),ker,mode='valid'),axis,a)
def blur(a,x,y):return smooth(smooth(a,x/.004,1),y/.004,0)
def fill(a):
    out=a.copy()
    for row in out:
        v=np.isfinite(row)
        if v.any():row[:]=np.interp(U,U[v],row[v])
        else:row[:]=0.
    return out
def row_at(field,path):
    return np.array([np.interp(at,V,field[:,j]) for j,at in enumerate(path)])
def sample(field,u,v):
    a=np.clip((u-U[0])/.004,0,len(U)-1.001);b=np.clip((v-V[0])/.004,0,len(V)-1.001)
    i=a.astype(int);j=b.astype(int);t=a-i;s=b-j
    return (1-s)*((1-t)*field[j,i]+t*field[j,i+1])+s*((1-t)*field[j+1,i]+t*field[j+1,i+1])
def fieldvals(design):
    fusion,keep,under,bank,slope,tail,front=design[:7]
    lower=smooth(np.interp(U,LOW[:,2],LOW[:,3]),.031/.004,0)
    brow=smooth(np.interp(U,BROW[:,2],BROW[:,3]),.025/.004,0)
    L=VV-lower;B=VV-brow
    area=ease((UU+.355)/.095)*(1-ease((UU-.32)/.155))*ease((VV+.269)/.077)*(1-ease((VV-.151)/.08))
    dome=bell(UU+.025,.145)*bell(VV-.013+.11*UU,.061)
    nose=ease((UU-.085)/.125)
    lower_gate=ease((UU+.25)/.11)*(1-ease((UU-.20)/.15))
    line=ease((UU-.01)/.19)*(1-ease((UU-.47)/.145))
    output=[]
    common_excess=blur(np.mean(np.where(np.isfinite(A[:,1]),A[:,1]-A[:,0],-.065),axis=0),.008,.006)
    for s in range(2):
        skull=fill(A[s,0]);eye=A[s,1];has=np.isfinite(eye)
        env=np.fmax(skull,eye);soft=blur(env,.064,.039)
        # A broad surface replaces the steep V at the original closed rim.
        # Keep the inner crescent while the outer edge continues onto the
        # existing cheek, most strongly at the lower and forward margins.
        upper=bell(B+.016,.042)*bell(UU+.095,.16)
        layer=fusion*(1-keep*dome)*(1-.32*upper)
        if len(design)>7:
            mask=eye>skull
            curve=np.full(len(U),np.nan)
            for j in np.where(mask.any(0))[0]:curve[j]=V[mask[:,j]][-1]
            valid=np.isfinite(curve);curve=np.interp(U,U[valid],curve[valid])
            curve=smooth(curve,6,0)
            upper=bell(VV-curve,.028)*bell(UU+.018,.216)
            layer=fusion*(1-keep*dome)*(1-.76*upper)
        face=env+(soft-env)*layer
        face+=(design[7] if len(design)>7 else .0085)*dome*(1-.70*nose)
        if len(design)>11:
            # Round the exposed noseward facet up into the open eye.
            face+=design[11]*bell(UU-.108,.117)*bell(VV-.032-.09*UU,.061)
        # One gently curved, longitudinal face supports the glancing light
        # beneath the eye. Its transverse section is tangent to the cheek.
        support=smooth(row_at(soft,lower),.089/.004,0)
        p=support+slope*L-3.9*L**2
        band=bank*lower_gate*bell(L,.064)
        face+=band*(p-face)
        # Long upper shade arcs under the brow and runs down the nose-side
        # cheek. It fades gradually past the actual tear corner.
        if len(design)>7:
            line=ease((UU-.018)/.17)*(1-ease((UU-.375)/.196))
        cut=-tail*line*bell(B+.013,.043 if len(design)>7 else .035)
        brow_roll=tail*.50*line*bell(B-.049,.054)
        face+=cut+brow_roll
        external=env+area*(face-env)+(1-area)*(cut+brow_roll)
        # Match both outer substrates to the same physical envelope. A
        # shallow rebate leaves the center exposed, while the lower and
        # front margins rise tangentially from the actual cheek.
        excess=np.where(has,eye-skull,-.25)
        bias=front*nose*bell(VV-.006,.077)+.006*ease((-VV-.007)/.039)
        contact=excess-bias
        if len(design)>7:
            contact=blur(np.where(has,contact,-.060),.008,.006)
        if len(design)>9:contact=common_excess-bias
        smoothpos=lambda z:np.maximum(z,0.)**2/(np.maximum(z,0.)+.019)
        head_target=external-under*smoothpos(contact)
        eye_target=external-(under+.055)*smoothpos(-contact)
        # The new rebate dissolves into the invisible outer substrate.
        local=area*ease((UU+.288)/.063)*(1-ease((UU-.242)/.085))
        if len(design)>9:local*=1-.32*ease((UU-.182)/.076)
        delta_h=external-env+local*(head_target-(external+skull-env))
        delta_e=np.where(has,external-env+local*(eye_target-(external+eye-env)),0.)
        output.append((delta_h,delta_e,lower,brow,eye_target))
    return output
def relax_axis(u,v,design):
    if len(design)<10:return u,v
    gate=ease((u+.36)/.13)*(1-ease((u-.24)/.25))*bell(v-.030,.180)
    gate*=1-ease((abs(v-.03)-.26)/.12)
    # Open the almond in its transverse direction, relax the descending
    # axis and keep both corners seated in the surrounding cheek.
    add=gate*(design[9]*(u+.015)+design[10]*(v-.025)*bell(u+.005,.176))
    return u,v+add
def update(s,ob,field,insert,design):
    p=pose(s);a=rest_coords(world_vertices(ob),p);u,v=chart(a);sg=np.where(a[:,1]<0,-1.,1.)
    delta=np.where(sg<0,sample(field[0][insert],u,v),sample(field[1][insert],u,v))
    # Keep the original buried polar substrate in the very thin upper
    # margin; the exterior carving lives farther out along the flank.
    if insert:
        delta*=ease((abs(a[:,1])+.22*u-.328)/.051)
    else:
        delta*=ease((abs(a[:,1])-.10)/.13)
    new=a.copy();new[:,1]+=sg*delta
    nu,nv=relax_axis(u,v,design)
    new[:,0]+=(nu-u)*AX[0]+(nv-v)*UP[0];new[:,2]+=(nu-u)*AX[1]+(nv-v)*UP[1]
    change=posed(new,*p)-posed(a,*p)
    co=np.empty((len(a),3),np.float32);ob.data.vertices.foreach_get('co',co.ravel())
    co+=change@np.linalg.inv(np.asarray(ob.matrix_world)[:3,:3]).T
    ob.data.vertices.foreach_set('co',co.ravel());ob.data.update()
    if len(design)>11 and ob.name.endswith(HEAD):
        attr=ob.data.attributes['Knight varnish coverage']
        a0=np.empty(len(a),np.float32);attr.data.foreach_get('value',a0)
        l=np.interp(u,U,field[0][2]);dv=v-l
        matte=bell(u-.009,.234)*bell(dv+.108,.07)*ease((-dv-.04)/.065)
        coat=a0*(1-.62*matte)
        if design[8]>=10:
            face=bell(u-.144,.152)*bell(dv-.008,.061)
            coat+=.21*face*(.77-coat)
        attr.data.foreach_set('value',np.float32(coat))
    return {'max_delta':float(abs(delta).max()),'moved':int((abs(delta)>1e-6).sum())}
def sculpt(s,design):
    field=fieldvals(design)
    changes={}
    if len(design)>7:
        from lens import rebuild
        for name in ['near eye','far eye']:changes[name]=rebuild(s,s.objects['Knight | '+name],field,design)
        local_resolution(s,s.objects['Knight | '+HEAD])
    else:
        for name in ['near eye','far eye']:changes[name]=update(s,s.objects['Knight | '+name],field,1,design)
    for name in [HEAD,BUILD]:changes[name]=update(s,s.objects['Knight | '+name],field,0,design)
    if len(design)>11:install_atlas(s)
    if len(design)>7 and design[8]:
        if design[8]<4:light_shape(s,design[8])
        else:
            from lamps import fit
            fit(s,design[8])
    return changes

def install_atlas(s):
    from hashlib import sha256
    old=s.objects['Knight | near eye'].active_material.node_tree.nodes['Knight delivered albedo'].image
    assert sha256(bytes(old.packed_file.data)).hexdigest()==PIGMENT
    new=bpy.data.images.load(str(D/'pigment.png'),check_existing=False)
    new.name='Knight walnut | integrated orbital grain 013-B';new.colorspace_settings.name='sRGB';new.pack()
    digest=sha256(bytes(new.packed_file.data)).hexdigest();assert digest==sha(D/'pigment.png')
    new.filepath='//../../assets/knight/wood-atlas-improvement-013-B.png'
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image==old:n.image=new
    if old.users==0:bpy.data.images.remove(old)
    s['knight_atlas_sha256']=digest

def local_resolution(s,ob):
    import bmesh
    a=rest_coords(world_vertices(ob),pose(s));u,v=chart(a)
    bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
    selected=[]
    for edge in bm.edges:
        i,j=[vert.index for vert in edge.verts]
        um=(u[i]+u[j])*.5;vm=(v[i]+v[j])*.5
        if .10<um<.69 and -.105<vm<.27 and np.linalg.norm(a[i]-a[j])>.019:
            selected.append(edge)
    if selected:bmesh.ops.subdivide_edges(bm,edges=selected,cuts=2,use_grid_fill=True)
    bm.to_mesh(ob.data);bm.free();ob.data.update()

def light_shape(s,index):
    scale,minor,energy,spread,offset=[(.34,.155,.085,27,-.036),(.47,.176,.116,32,-.052),(.54,.18,.143,43,-.068)][index-1]
    lamp=s.objects['Eye reflection lower'];a=math.radians(pose(s)[2])
    along=Vector((AX[0]*math.cos(a),AX[0]*math.sin(a),AX[1]))
    lamp.location+=offset*along;lamp.data.size=scale;lamp.data.size_y=minor;lamp.data.energy=energy;lamp.data.spread=math.radians(spread)
    bpy.context.view_layer.update()
def border(s,box):
    x,y,a,b=box;s.render.use_border=s.render.use_crop_to_border=True
    s.render.border_min_x=(x+.1)/1254;s.render.border_max_x=(a+.1)/1254
    s.render.border_min_y=(1254-b+.1)/1254;s.render.border_max_y=(1254-y+.1)/1254
def portrait_setup(s,side=-1):
    yaw=math.radians(pose(s)[2]);axis=Vector((math.cos(yaw),math.sin(yaw),0));across=Vector((-axis.y,axis.x,0));up=Vector((0,0,1))
    eyes=[s.objects['Knight | '+n+' eye'].matrix_world.translation.copy() for n in ['near','far']]
    center=(eyes[0]+eyes[1])*.5
    for o in s.objects:
        if o.type=='LIGHT':o.hide_render=True
    for sg in [-1,1]:
        for pt,power,diam in [(center-1.8*axis+sg*3.4*across+4.*up,250,2.6),(center+2.2*axis+sg*2.8*across+1.2*up,75,3.5)]:
            l=bpy.data.lights.new('Portrait bank','AREA');l.energy=power;l.shape='DISK';l.size=diam
            obj=bpy.data.objects.new(l.name,l);s.collection.objects.link(obj);obj.location=pt;obj.rotation_euler=(center-pt).to_track_quat('-Z','Y').to_euler()
    s.world=bpy.data.worlds.new('Neutral ambient');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.24
    s.render.use_border=s.render.use_crop_to_border=False
    s.render.resolution_x=400;s.render.resolution_y=282
    target=eyes[0 if side<0 else 1];cam=s.camera;cam.data.ortho_scale=1.42;cam.data.shift_x=cam.data.shift_y=0
    cam.location=target+7*(side*across+.09*axis+.12*up);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
def trial(i):
    s=load('parent.blend')
    if i>=0:sculpt(s,DESIGNS[i])
    configure_render(s,48);s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=7
    border(s,(448,444,594,527));render(s,D/f'trial-{i}-fixed.png')
    portrait_setup(s);render(s,D/f'trial-{i}-side.png')
    mat=bpy.data.materials.new('Common clay');mat.use_nodes=True;bs=mat.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value=(.4,.42,.43,1);bs.inputs['Roughness'].default_value=.62
    for o in s.objects:
        if o.type=='MESH' and not o.hide_render:
            for slot in o.material_slots:slot.material=mat
    render(s,D/f'trial-{i}-clay.png')
def build(i):
    s=load('parent.blend');details=sculpt(s,DESIGNS[i])
    from mesh_check import inspect
    checks=inspect(s);assert all(p['nonadjacent_crossings']==0 for p in checks['nonadjacent_intersections'].values()),checks
    from mathutils.bvhtree import BVHTree
    graph=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(s.objects['Knight | '+HEAD],graph)
    for name,sg in [('near eye',-1),('far eye',1)]:
        ob=s.objects['Knight | '+name];pt=tree.ray_cast((ob.location.x,2*sg,ob.location.z),(0,-sg,0))[0]
        assert pt is not None and abs(ob.location.y-pt.y)<ob.dimensions.y/2,(name,pt,ob.location,ob.dimensions)
    config={'design':i,'parameters':DESIGNS[i],'parent_sha256':PARENT,'pigment_sha256':s['knight_atlas_sha256'],'parts':details,'native':checks}
    s['knight_improvement_013_B']=json.dumps(config)
    configure_render(s,144);save_model(s,D/'knight.blend')
    config['model_sha256']=sha(D/'knight.blend');(D/'parameters.json').write_text(json.dumps(config,indent=2)+'\n')
if __name__=='__main__':
    assert sha(D/'parent.blend')==PARENT
    args=sys.argv[sys.argv.index('--')+1:]
    if args[0]=='trial':
        for i in map(int,args[1:]):trial(i)
    if args[0]=='build':build(int(args[1]))
    if 'studio' in args:studio()
    if 'orbit' in args:
        flat_views('knight.blend','')
        s=load('knight.blend');configure_render(s,32);diagnostics(s,'',True)

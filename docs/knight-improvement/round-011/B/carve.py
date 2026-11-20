"""Carve a curved inner eye, shallow lower-facing terrace and blended tear corner."""
from pathlib import Path
import hashlib,json,math,sys
import bpy,numpy as np
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;R=D.parents[2]
sys.path[:0]=[str(D),str(R/'scripts/knight')]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,save_model,render,sha,use_side_camera,world_vertices
from evidence import load,flat,flat_views,studio
from diagnostics import diagnostics
PARENT='7fe492399fa2738d264e73e9e85c427c1531cb902234d43ce1e5012468488922'
PIGMENT='86debdcce4b5b6075ae7510cb25f77066ae912cfb8e1a0c4a49101ed43b79978'
EYE_PIGMENT='beee98c4ee1af2c55823485a4c0149dea5332c7eaeaa07e06d82ae7022918fe7'
AX=np.array([1.,-.76])/np.hypot(1.,.76);UP=np.array([-AX[1],AX[0]])
CENTER=np.array([.412,4.158])
FIELD=np.array(json.loads((D/'aperture-curve.json').read_text())['curve'])
# Angular relaxation, inserted inner mound, height and depth of the secondary
# fold, nasal cheek return, maximum of fold, central width and surface finish.
DESIGNS=[(.13,.016,.012,.010,.017,.26,.16,.17),
         (.20,.023,.016,.015,.023,.24,.145,.16),
         (.16,.026,.020,.018,.025,.28,.18,.13),
         (.12,.018,.013,.020,.032,.30,.17,.18),
         (.155,.034,.006,.004,.017,.26,.175,.15,1.0),
         (.155,.046,.005,.007,.018,.25,.162,.17,1.0),
         (.150,.034,.009,.006,.020,.24,.158,.16,1.25),
         (.180,.040,.006,.008,.020,.25,.188,.18,.83),
         (.135,.028,.005,.004,.019,.25,.172,.115,.97,-.44),
         (.145,.033,.005,.006,.023,.25,.172,.115,1.05,-.67),
         (.125,.026,.005,.005,.022,.25,.177,.130,.92,-.90),
         (.140,.031,.004,.004,.018,.25,.174,.101,1.02,-.58,1.),
         (.145,.032,.004,.005,.019,.25,.173,.096,1.0,-.64,1.25)]

def ease(x):
    t=np.clip(x,0,1);return t*t*(3-2*t)
def bell(x,w):return np.exp(-(x/w)**2)
def pose(s):
    p=json.loads(s['knight_mission_pose']);return [p[k] for k in ('dx','dy','twist_degrees')]
def chart(a):
    q=a[:,[0,2]]-CENTER;return q@AX,q@UP
def bounds(u):
    return [np.interp(u,FIELD[:,0],FIELD[:,i]) for i in (1,2)]
def grain_field(u,v,side):
    data=np.load(D/'fine-grain-field.npz');field=data['grain'];low=data['low'];grid=float(data['step'])
    x=np.clip((.92*u-.046-low[0]+.012*side)/grid,0,field.shape[1]-1.01)
    y=np.clip((v-.302-low[1])/grid,0,field.shape[0]-1.01)
    i=x.astype(int);j=y.astype(int);tx=x-i;ty=y-j
    val=(1-tx)*(1-ty)*field[j,i]+tx*(1-ty)*field[j,i+1]+(1-tx)*ty*field[j+1,i]+tx*ty*field[j+1,i+1]
    return np.clip(val/.085,-1.8,1.8)

def densify(ob):
    # Interpolated UVs and point-domain finish stay attached to the original
    # closed spherical substrate. Fine relief is carved into this real mesh.
    bpy.context.view_layer.objects.active=ob
    mod=ob.modifiers.new('Fine carving support','SUBSURF')
    mod.subdivision_type='SIMPLE';mod.levels=2;mod.render_levels=2
    bpy.ops.object.modifier_apply(modifier=mod.name)

def change(scene,ob,design,insert):
    rotation,mound,ridge,incision,corner,core_h,span,central_finish=design[:8]
    p=pose(scene)
    if insert:densify(ob)
    world=world_vertices(ob);old=rest_coords(world,p);u,v=chart(old)
    lo,hi=bounds(u);width=np.maximum(hi-lo,.036)
    h=(v-lo)/width
    gate=ease((.391-abs(u-.025))/.115)*ease((.270-abs(v-.011))/.128)
    gate*=ease((abs(old[:,1])-.13)/.09)
    if insert and len(design)>10:
        # The sloping back of the inherited insert is buried in the socket.
        # Begin the new carving as the substrate rises toward the opening.
        gate*=ease((abs(old[:,1])+.22*u-.332)/.048)
    # Return the tip and lower lid gently upwards toward the nose. The
    # displacement extends over the skin and the eye together so the floor
    # cannot shear free of the inner corners.
    rot=gate*rotation*(u+.046)*bell(v-.009,.154)
    rot-=.009*gate*bell(u+.163,.088)*bell(v-.031,.102)
    if len(design)>8:
        rot*=.18+.82*ease((v-lo+.054)/.074)
    along=-.024*gate*ease((u-.069)/.192)*bell(v-.003,.082)
    if len(design)>9:
        along-=.015*gate*ease((u-.103)/.13)*bell(v-.001,.065)
        rot-=.006*gate*ease((h-.68)/.3)*bell(u+.073,.14)*bell(v-hi,.055)
    a=ease((u+.207)/.083)*ease((.268-u)/.110)
    # A low curved ridge becomes the lower lip of the inner carving. It
    # turns upward at each corner, with the noseward turn shorter and lower.
    arc=core_h+.158*((u+.006)/.18)**2-.115*u/.20
    g=bell(u+.016,span)*a
    # Keep a shallow convex face on the upper two-thirds of the inner eye.
    face=g*bell(h-(arc+.35),.30)
    fold=g*bell(h-arc,.132)
    recess=g*bell(h-(arc+.163),.129)
    if len(design)>8:
        # A compact, inclined wooden boss occupies the rear and upper
        # portion of the eye. Only its lower crescent is cut free; its
        # upper half flows continuously under the existing brow.
        slope=-.115
        center=.035+slope*(u+.025)
        n=(u+.032)/span
        rounded=np.sqrt(np.maximum(.07,1.-np.minimum(n*n,.93)))
        inner_curve=center-(.058*design[8])*rounded
        dy=v-inner_curve
        lateral=ease((1.17-abs(n))/.46)
        belly=bell(u+.035,.125)*bell(v-center,.067)
        roll=ease((dy+.012)/.040)
        face=lateral*belly*roll
        # The secondary shelf is broad in physical section and strongest
        # below the front half of the boss. It fades before the tear corner.
        f=ease((u+.169)/.086)*ease((.223-u)/.077)
        fold=f*bell(u-.039,.125)*bell(dy+.021,.026)
        recess=lateral*bell(u+.005,.142)*bell(dy+.001,.014)
    side=np.sign(old[:,1])
    if insert:
        z=mound*face+ridge*fold-incision*recess
        z-=(.004 if len(design)>8 else .0075)*a*bell(h-.53,.60)
        z-=.011*ease((u-.100)/.145)*a*bell(h-.42,.38)
        if len(design)>8:
            fiber=np.sin(102*v+1.0*np.sin(20*u))*(.5+.5*np.sin(24*u+.4))
            z+=.00085*fiber*(.24+.76*face)*a
        if len(design)>9:
            # A shallow nasal-facing return cut makes the lower crescent a
            # broad inclined surface instead of a second narrow scored line.
            cross=dy+.018
            slope_weight=bell(u-.059,.119)*ease((u+.13)/.095)*ease((.217-u)/.076)
            z+=design[9]*cross*bell(cross,.029)*slope_weight
        if len(design)>10:
            grain=grain_field(u,v,side)
            z+=design[10]*.00165*grain*(.13+.87*face)*a
            z+=.009*bell(u-.203,.072)*bell(h-.37,.38)
        y_delta=gate*z
    else:
        # Convex nasal return and a fine supporting shelf immediately below
        # the opening. The broad cheek reflection remains separately seated.
        above=bell(v-hi+.006,.037)*bell(u+.026,.172)
        low=bell(v-lo+.021,.044)*bell(u-.012,.175)*a
        nasal=bell(u-.230,.092)*bell(v-(lo+.019),.056)
        inside=bell(v-lo-.005,.025)*bell(u-.049,.17)*a
        if len(design)>8:
            y_delta=gate*(.009*above+.0018*low-.0015*inside+corner*nasal)
        else:y_delta=gate*(.008*above+.0075*low-.004*inside+corner*nasal)
    new=old.copy();new[:,1]+=side*y_delta
    new[:,0]+=rot*UP[0]+along*AX[0];new[:,2]+=rot*UP[1]+along*AX[1]
    dif=posed(new,*p)-posed(old,*p);original=np.empty((len(old),3),np.float32)
    ob.data.vertices.foreach_get('co',original.ravel())
    original+=dif@np.linalg.inv(np.asarray(ob.matrix_world)[:3,:3]).T
    ob.data.vertices.foreach_set('co',original.ravel())
    attr=ob.data.attributes.get('Knight varnish coverage')
    if attr is None:
        assert ob.hide_render,ob.name
        ob.data.update()
        return {'vertices':len(old),'changed_1e-6':int((np.linalg.norm(dif,axis=1)>1e-6).sum()),
                'max_shift':float(np.linalg.norm(dif,axis=1).max())}
    before=np.empty(len(old),np.float32);attr.data.foreach_get('value',before)
    if insert:
        # Satin floor and burnished central facet. A continuous gain along
        # the actual lower cutting edge lets it catch a moving softbox.
        finish=.055+.09*face+.29*fold+.06*g*bell(h-(arc+.48),.14)
        if len(design)>8:
            finish=.07+.12*face+.15*fold+.053*face*np.sin(103*v+1.3*np.sin(21*u))
        if len(design)>9:
            finish+=.12*slope_weight*bell(cross,.024)
        if len(design)>10:
            finish+=design[10]*(.114*grain-.075)*face
        finish+=central_finish*face
        after=before+gate*ease((.39-abs(u))/.10)*(finish-before)
    else:
        mat=ease((.38-abs(u-.034))/.11)*bell(v-lo+.002,.062)
        after=before*(1-.40*gate*mat*ease((u-.108)/.116))
        if len(design)>10:
            diffuse=bell(u-.018,.24)*bell(v-lo+.130,.071)*ease((lo-v-.071)/.046)
            after*=1-.65*gate*diffuse
    attr.data.foreach_set('value',np.clip(after,0,1).astype(np.float32));ob.data.update()
    return {'vertices':len(old),'changed_1e-6':int((np.linalg.norm(dif,axis=1)>1e-6).sum()),
        'rest_depth_min_max':[float(y_delta.min()),float(y_delta.max())],
        'max_shift':float(np.linalg.norm(dif,axis=1).max()),'finish_min_max':[float(after.min()),float(after.max())]}

def sculpt(scene,design):
    result={}
    for part in ['near eye','far eye','continuous horse head and neck','coherent skull cheek and conical muzzle']:
        result[part]=change(scene,scene.objects['Knight | '+part],design,part.endswith('eye'))
    if len(design)>9:install_atlas(scene)
    bpy.context.view_layer.update()
    return {'parts':result,'parameters':dict(zip(['axis_rotation','inner_mound','inner_lower_ridge','incision',
        'tear_corner_return','lower_ridge_normalized_height','lower_ridge_span','central_polish','inner_arc_radius_factor','lower_return_slope','physical_grain_factor'],design))}

def install_atlas(scene):
    node=scene.objects['Knight | near eye'].active_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node
    old=node.image
    assert hashlib.sha256(bytes(old.packed_file.data)).hexdigest()==PIGMENT
    new=bpy.data.images.load(str(D/'pigment.png'),check_existing=False)
    new.name='Knight walnut | orbital grain 011-B'
    new.colorspace_settings.name='sRGB';new.pack()
    assert hashlib.sha256(bytes(new.packed_file.data)).hexdigest()==EYE_PIGMENT
    new.filepath='//../../assets/knight/wood-atlas-improvement-011-B.png'
    for m in bpy.data.materials:
        if not m.node_tree:continue
        for texture in m.node_tree.nodes:
            if texture.type=='TEX_IMAGE' and texture.image==old:texture.image=new
    if old.users==0:bpy.data.images.remove(old)

def border(scene,b):
    x,y,a,c=b;scene.render.use_border=scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x+.05)/1254;scene.render.border_max_x=(a+.05)/1254
    scene.render.border_min_y=(1254-c+.05)/1254;scene.render.border_max_y=(1254-y+.05)/1254

def portrait_setup(s):
    yaw=math.radians(pose(s)[2]);ax=Vector((math.cos(yaw),math.sin(yaw),0))
    ac=Vector((-ax.y,ax.x,0));up=Vector((0,0,1))
    eyes=[s.objects['Knight | '+n+' eye'].matrix_world.translation.copy() for n in ['near','far']]
    center=.5*(eyes[0]+eyes[1])
    for o in s.objects:
        if o.type=='LIGHT':o.hide_render=True
    for side in [-1,1]:
        for loc,power,size in [(center-1.8*ax+side*3.4*ac+4.*up,250,2.6),(center+2.2*ax+side*2.8*ac+1.2*up,75,3.5)]:
            l=bpy.data.lights.new('Portrait bank','AREA');l.energy=power;l.shape='DISK';l.size=size
            ob=bpy.data.objects.new(l.name,l);s.collection.objects.link(ob);ob.location=loc
            ob.rotation_euler=(center-loc).to_track_quat('-Z','Y').to_euler()
    s.world=bpy.data.worlds.new('Portrait');s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.24
    s.render.use_border=s.render.use_crop_to_border=False
    s.render.resolution_x=400;s.render.resolution_y=282
    cam=s.camera;cam.data.ortho_scale=1.42;cam.data.shift_x=cam.data.shift_y=0
    cam.location=eyes[0]+7*(-ac+.09*ax+.12*up)
    cam.rotation_euler=(eyes[0]-cam.location).to_track_quat('-Z','Y').to_euler()

def do_study(i):
    s=load('parent.blend')
    if i>=0:sculpt(s,DESIGNS[i])
    configure_render(s,72);border(s,(448,444,565,524))
    render(s,D/f'trial-{i}-fixed.png')
    portrait_setup(s)
    render(s,D/f'trial-{i}-walnut-side.png')
    mat=bpy.data.materials.new('Portrait clay');mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.4,.42,.43,1);bs.inputs['Roughness'].default_value=.62
    for ob in s.objects:
        if ob.type=='MESH' and not ob.hide_render:
            for slot in ob.material_slots:slot.material=mat
    render(s,D/f'trial-{i}-clay-side.png')

def build(i,card_index):
    s=load('parent.blend');config=sculpt(s,DESIGNS[i])
    from mesh_check import inspect
    qa=inspect(s)
    assert max(v['nonadjacent_crossings'] for v in qa['nonadjacent_intersections'].values())==0
    assert qa['mirrored_exposure_iou']>.97
    from cards import measured,apply
    config['native_checks']=qa;config['card_configuration']=card_index
    config['physical_softboxes']=apply(s,measured(s),card_index)
    config.update({'parent_sha256':PARENT,'pigment_sha256':EYE_PIGMENT,'design':i})
    im=s.objects['Knight | near eye'].active_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image
    assert hashlib.sha256(bytes(im.packed_file.data)).hexdigest()==sha(D/'pigment.png')==EYE_PIGMENT
    config['release_texture']='wood-atlas-improvement-011-B.png';s['knight_atlas_sha256']=EYE_PIGMENT
    s['knight_improvement_011_B']=json.dumps(config)
    configure_render(s,144);save_model(s,D/'knight.blend')
    config['model_sha256']=sha(D/'knight.blend');(D/'parameters.json').write_text(json.dumps(config,indent=2)+'\n')
if __name__=='__main__':
    assert sha(D/'parent.blend')==PARENT
    if '--test' in sys.argv:
        for i in sys.argv[sys.argv.index('--test')+1:]:do_study(int(i))
    if '--build' in sys.argv:
        start=sys.argv.index('--build');build(int(sys.argv[start+1]),int(sys.argv[start+2]))
    if '--studio' in sys.argv:studio()
    if '--orbit' in sys.argv:
        flat_views('knight.blend','');s=load('knight.blend');configure_render(s,32);diagnostics(s,'',True)

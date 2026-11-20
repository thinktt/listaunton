"""Shape both eye openings as one continuous displacement through the native relief."""
from pathlib import Path
import json,math,sys
import numpy as np,bpy
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from orbital import pose,chart,rest_coords,world_vertices,posed,AX,UP,O as CENTER,HEAD,BUILD
from evidence import load,configure_render,render,flat,flat_views,studio
from mission_scene import save_model,sha
from diagnostics import diagnostics
PARENT='c404e26928309df6233e2e7b3595d5d10025632a18e61e635294eb08b411f33e'
PIGMENT='f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8'
# Crown strength, forward return, lower crescent, crown lift and tangent gradient.
DESIGNS=[(.76,.69,.48,.009,-.04,-.47),(1.0,.87,.70,.011,-.04,-.47),(.93,.82,.36,.004,-.09,-.46)]
DESIGNS += [(1.,.85,.84,.006,.018,-.356,.30,.68),
            (1.,.82,1.07,.002,.04,-.34,.47,.77),
            (.90,.82,.82,.004,-.018,-.39,.63,.83)]
DESIGNS += [(1.,.82,1.10,.003,.050,-.33,.26,.56,.042,.029,.022,.66),
            (1.,.78,1.27,.005,.045,-.325,.29,.63,.048,.035,.026,.40),
            (1.,.73,1.14,.003,.041,-.348,.25,.51,.055,.040,.029,.76)]
DESIGNS += [(1.,.82,.92,.006,.018,-.356,.31,.61,.026,.032,.025,1.38,.43),
            (1.,.84,1.18,.004,.030,-.343,.36,.66,.035,.034,.031,1.58,.56),
            (1.,.84,.95,.005,.020,-.350,.30,.63,.030,.040,.034,1.22,.65)]
DESIGNS += [(1.,.84,1.03,.004,.030,-.343,.32,.65,.025,.027,.028,1.48,.50,.022),
            (1.,.84,1.03,.004,.030,-.343,.32,.65,.025,.027,.028,1.48,.50,.037),
            (1.,.84,1.03,.004,.030,-.343,.32,.65,.025,.027,.028,1.48,.50,.048)]
def ease(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)
def bell(x,w):return np.exp(-.5*(x/w)**2)
def soften(a,sx,sy,du):
    def smooth(v,width):
        k=np.arange(-math.ceil(3.5*width/du),math.ceil(3.5*width/du)+1);w=bell(k*du,width);w/=w.sum()
        return np.apply_along_axis(lambda row:np.convolve(np.pad(row,k[-1],mode='edge'),w,'valid'),-1,v)
    return smooth(smooth(a,sx).T,sy).T
def lookup(a,u,v,x,y):
    xx=np.clip((x-u[0])/(u[1]-u[0]),0,len(u)-1.001);yy=np.clip((y-v[0])/(v[1]-v[0]),0,len(v)-1.001)
    i=xx.astype(int);j=yy.astype(int);dx=xx-i;dy=yy-j
    return (1-dy)*((1-dx)*a[j,i]+dx*a[j,i+1])+dy*((1-dx)*a[j+1,i]+dx*a[j+1,i+1])
def field(design):
    archive=np.load(D/'field-parent.npz');u,v,a=(archive[k] for k in ('u','v','surfaces'))
    x,y=np.meshgrid(u,v);pitch=u[1]-u[0]
    near,far=(np.fmax(h,e) for h,e in a);native=.5*(near+far);native=np.nan_to_num(native)
    strength,front,low,lift,gu,gv=design[:6]
    # Soften the enclosed rim and the angular return across the entire forward third.
    loose=soften(native,.057,.031,pitch)
    forward=front*bell(x-.185,.112)*bell(y-.050,.057)
    rear=.49*bell(x+.195,.063)*bell(y-.048,.063)
    plane=native+np.minimum(.94,forward+rear)*(loose-native)
    if len(design)>12:
        rim=design[12]*bell(y+.023-.084*x,.031)*bell(x-.072,.133)
        plane+=rim*(loose-plane)
    # One broad oblique crown. The shoulder runs diagonally towards the lower nose corner.
    center=(-.066,.096);xx=x-center[0];yy=y-center[1];across=yy+.27*xx
    height=lookup(native,u,v,np.array([center[0]]),np.array([center[1]]))[0]
    long_curve=1.38 if len(design)<9 else design[11]
    crown=height+lift+gu*xx+gv*yy-long_curve*xx**2-4.6*across**2-.60*xx*yy
    w=strength*bell(xx,.112)*bell(across,.047)
    plane+=w*(crown-plane)
    # A thin cut and its softly rounded lower lip, strongest at the rear-middle.
    lower=-.015+.13*(x+.005)+.70*(x+.01)**2
    lip=low*bell(x-.012,.130)*(.009*bell(y-lower,.020)-.007*bell(y-lower-.032,.016))
    plane+=lip
    # Carry the upper crease through each corner with a raised brow and a shallow cut.
    path=np.interp(x,[-.43,-.31,-.23,-.14,-.055,.018,.119,.223,.37,.54],
                    [.049,.074,.096,.124,.144,.145,.127,.097,.066,.048])
    channel=.0065*(.77*bell(x+.21,.073)+bell(x-.235,.094))
    plane+=channel*(.6*bell(y-path-.030,.022)-bell(y-path,.021))
    if len(design)>13:
        # Quiet swelling under the front lower lip. The anterior flank turns back into the brow.
        plane+=design[13]*bell(x-.230,.072)*bell(y-.065+.20*(x-.18),.050)
    # Compact support protects ear, muzzle, outline and the cheek beneath the lower lid.
    fade=ease((x+.41)/.08)*ease((.46-x)/.10)*ease((y+.13)/.06)*ease((.24-y)/.055)
    return u,v,(plane-native)*fade
def sculpt(s,design):
    u,v,delta=field(design);p=pose(s);stats={}
    for name in [HEAD,BUILD,'near eye','far eye']:
        ob=s.objects['Knight | '+name];a=rest_coords(world_vertices(ob),p);x,y=chart(a)
        dy=lookup(delta,u,v,x,y)*ease((abs(a[:,1])-.09)/.14)*np.sign(a[:,1])
        dst=a.copy();dst[:,1]+=dy
        if len(design)>8:
            # Turn the anterior lip and tear corner together, closing the cut on the skull.
            gate=ease((abs(a[:,1])-.10)/.14)*ease((x+.415)/.065)*ease((.46-x)/.075)*ease((y+.14)/.055)*ease((.24-y)/.045)
            forward=bell(x-.235,.115)*bell(y-.073,.092)*gate
            aft=bell(x+.217,.082)*bell(y-.089,.066)*gate
            if len(design)>12:
                forward=bell(x-.245,.076)*bell(y-.082,.057)*gate
                aft=bell(x+.245,.061)*bell(y-.09,.055)*gate
            du=design[8]*forward
            dv=design[9]*forward-design[10]*aft
            dst[:,0]+=AX[0]*du+UP[0]*dv
            dst[:,2]+=AX[1]*du+UP[1]*dv
        if name=='near eye':near=dst.copy()
        if name=='far eye':
            from seat import opposite
            ids=opposite(s.objects['Knight | near eye'].data,ob.data)
            mirrored=near[ids].copy();mirrored[:,1]*=-1
            # Maintain the far socket's inherited seating outside the hidden near-tangent return.
            distance=np.hypot(x+.165,y-.165)
            weight=1-ease((distance-.037)/.041)
            dst+=weight[:,None]*(mirrored-dst)
        local=(posed(dst,*p)-posed(a,*p))@np.linalg.inv(np.asarray(ob.matrix_world)[:3,:3]).T
        c=np.empty((len(a),3),np.float32);ob.data.vertices.foreach_get('co',c.ravel());c+=local
        ob.data.vertices.foreach_set('co',c.ravel());ob.data.update()
        tessellation=[]
        if name=='far eye':
            from seat import triangles
            tessellation=triangles(ob)
        magnitude=np.linalg.norm(dst-a,axis=1)
        stats[name]={'max_displacement':float(magnitude.max()),'moved_vertices':int((magnitude>1e-6).sum())}
        if tessellation:stats[name]['hidden_return_triangulation']=tessellation
        if len(design)>6 and name.endswith('eye'):
            attr=ob.data.attributes['Knight varnish coverage']
            old=np.empty(len(a),np.float32);attr.data.foreach_get('value',old)
            # Polish follows the broad convex cut. The shallower forward return retains open grain.
            seat=bell(x+.069,.082)*bell(y-.091+.20*(x+.069),.038)
            forward=bell(x-.170,.074)*bell(y-.035,.054)
            polish=old*(1-design[7]*forward)+design[6]*seat*(1-old)
            attr.data.foreach_set('value',np.float32(polish))
            stats[name]['varnish_delta_max']=float(np.max(np.abs(polish-old)))
    bpy.context.view_layer.update()
    return stats
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
    from orbital import mesh_tree
    head=mesh_tree(s,HEAD)
    for name in ['near eye','far eye']:
        seated=len(head.overlap(mesh_tree(s,name)));assert seated>0
        details[name]['intersecting_head_triangles']=seated
    config={'design':i,'parameters':DESIGNS[i],'parent_sha256':PARENT,'pigment_sha256':s['knight_atlas_sha256'],'parts':details,'native':checks}
    s['knight_improvement_015_B']=json.dumps(config)
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

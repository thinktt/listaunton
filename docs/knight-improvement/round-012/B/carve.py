"""Redraw the two native mane/neck flanks in a shared anatomical frame."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
from mathutils import Vector
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
R=D.parents[2]
sys.path[:0]=[str(D),str(R/'scripts/knight')]
from section_grid import pose,rest_coords,posed,world_vertices,MANE,HEAD,BUILD,NECK
from evidence import load,flat,studio,flat_views
from diagnostics import camera,diagnostics
from mission_scene import configure_render,render,save_model,sha,use_side_camera
PARENT='c4e629d930d907d77885c01dd430cab58e99e26a26e04b63d2a36b373ecdac58'
PIGMENT='beee98c4ee1af2c55823485a4c0149dea5332c7eaeaa07e06d82ae7022918fe7'
GRID=np.load(D/'parent-sections.npz')
GX,GZ,G=[GRID[k] for k in ('x','z','sides')]

def ease(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

def pchip(x,y,q):
    """Shape-preserving cubic interpolation without optional binary dependencies."""
    x=np.asarray(x);y=np.asarray(y)
    dx=np.diff(x);s=np.diff(y)/dx
    d=np.zeros_like(y,dtype=float);d[0]=s[0];d[-1]=s[-1]
    good=s[1:]*s[:-1]>0
    w1=2*dx[1:]+dx[:-1];w2=2*dx[:-1]+dx[1:]
    ix=np.flatnonzero(good)
    d[ix+1]=(w1[ix]+w2[ix])/(w1[ix]/s[ix]+w2[ix]/s[ix+1])
    q=np.clip(q,x[0],x[-1]);i=np.clip(np.searchsorted(x,q)-1,0,len(x)-2)
    t=(q-x[i])/dx[i]
    return (2*t**3-3*t**2+1)*y[i]+(t**3-2*t**2+t)*dx[i]*d[i]+(-2*t**3+3*t**2)*y[i+1]+(t**3-t**2)*dx[i]*d[i+1]

def prepare():
    stations=np.arange(1.985,4.811,.075)
    posterior=[];edge=[];centre=[]
    for z in stations:
        j=np.abs(GZ-z).argmin()
        # Interpolate the actual crossing between the exterior of the
        # hanging blade and the native neck hull. Average both true flanks.
        crosses=[];mids=[]
        for side in range(2):
            m,h=G[:,side,j]
            d=np.nan_to_num(m,nan=-3.)-np.nan_to_num(h,nan=-3.)
            use=np.where((d[:-1]>=0)&(d[1:]<0)&np.isfinite(m[:-1])&(GX[:-1]<-.15))[0]
            if len(use):
                i=use[-1];w=d[i]/(d[i]-d[i+1])
                crosses.append(GX[i]+w*(GX[i+1]-GX[i]))
                mids.append(np.interp(crosses[-1],GX[np.isfinite(m)],m[np.isfinite(m)]))
        edge.append(np.mean(crosses) if crosses else -.23)
        centre.append((mids[1]-mids[0])/2 if len(mids)==2 else 0)
        good=np.isfinite(G[0,0,j])
        posterior.append(GX[good].min() if np.any(good) else -1.18)
    return stations,np.array(posterior),np.array(edge),np.array(centre)
ST,POST,ED,CENTER=prepare()
# The old physical join is carried toward the rear on both flanks, and the
# removed width is given to the actual neck section. End stations preserve
# the base attachment and the upper shoulder directly below the ear.
HE=[2.28,2.47,2.59,2.80,3.02,3.23,3.41,3.58,3.74,3.90,4.05,4.20,4.37,4.54,4.70]
PULL=[0.,0.,.015,.076,.168,.253,.292,.317,.333,.341,.317,.284,.201,.079,0.]
# Physical pull, convexity of distal blade, depth under its edge, fullness
# of the neck toward the breast, width of the neck roll.
DESIGNS=[(1.00,0.,0.,0.,.28), (1.015,.024,.020,.036,.36),
         (1.04,.047,.046,.063,.35),(.98,.039,.032,.073,.42),
         (1.055,.014,.090,.080,.30,.145,.062,.86),
         (1.06,.025,.145,.105,.29,.182,.051,.96),
         (1.075,.039,.175,.094,.28,.183,.049,.96),
         (1.05,.005,.111,.087,.28,.143,.045,1.),
         (1.06,.020,.147,.097,.29,.175,.051,1.,.82),
         (1.065,.024,.158,.101,.31,.180,.051,1.,1.),
         (1.06,.024,.155,.097,.31,.185,.052,1.,.60),
         (1.065,.024,.156,.102,.30,.180,.051,1.42,1.,.44,2.30,1.,'parent'),
         (1.066,.024,.151,.100,.30,.180,.051,1.28,.0,.47,2.20,1.,'satin'),
         (1.07,.024,.166,.100,.30,.180,.051,1.55,.38,.42,2.05,1.,'light'),
         (1.066,.024,.151,.100,.30,.180,.051,1.36,.0,.47,2.20,1.,'satin',0.),
         (1.066,.024,.151,.100,.30,.180,.051,1.36,.0,.47,2.20,1.,'satin',.63),
         (1.066,.024,.151,.100,.30,.180,.051,1.36,.0,.47,2.20,1.,'satin',0.,1.)]

def pull_curve(z,design):
    pull=design[0]*pchip(HE,PULL,z)
    if len(design)>13:
        zc=[2.48,2.68,2.79,2.89,2.99,3.10,3.20,3.31,3.42,3.53,3.63,3.75,3.84,3.95,4.11,4.32,4.65]
        length=[0,.003,.008,.018,.030,.036,.030,.014,.004,-.003,-.009,-.017,-.032,-.049,-.041,-.015,0]
        pull+=pchip(zc,length,z)
    return pull

def tip_fields():
    fields=np.fmax(G[0],G[1]);out=np.zeros_like(fields)
    kernel=np.exp(-.5*(np.arange(-38,39)/13.)**2);kernel/=kernel.sum()
    for si in [0,1]:
        for j in range(len(GZ)):
            y=fields[si,j];ok=np.isfinite(y)
            if not ok.any():continue
            y=np.interp(GX,GX[ok],y[ok])
            full=np.convolve(np.pad(y,38,mode='edge'),kernel,mode='valid')
            out[si,j]=full-y
    return out
TIP=tip_fields()
SKIN=np.fmax(G[0],G[1]).copy()
for bank in SKIN:
    for row in bank:
        valid=np.isfinite(row)
        if valid.any():row[:]=np.interp(GX,GX[valid],row[valid])
        else:row[:]=0

def sample_grid(field,x,z):
    u=np.clip((x-GX[0])/(GX[1]-GX[0]),0,len(GX)-1.01)
    v=np.clip((z-GZ[0])/(GZ[1]-GZ[0]),0,len(GZ)-1.01)
    i=u.astype(int);j=v.astype(int);tx=u-i;tz=v-j
    return (1-tz)*((1-tx)*field[j,i]+tx*field[j,i+1])+tz*((1-tx)*field[j+1,i]+tx*field[j+1,i+1])

def fair_face(a,xx,back,edge,pull,mid,dr,design):
    """One convex face with a continuously changing normal to the edge."""
    x,y,z=a.T;crest,power,amount=design[9:12]
    rear=edge-pull-back
    r=(xx-back)/np.maximum(rear,.19)
    strength=np.clip(pull/.29,0,1)
    # Parameterize each anatomical section in its actual new lateral span.
    # The starting and peak widths come from the uncut bilateral billet.
    # A parabola returns continuously to a gently domed maximum, then
    # falls in a single smooth arc all the way to the cut.
    stats=[]
    for si in [0,1]:
        rows=[]
        for j,h in enumerate(GZ):
            b=pchip(ST,POST,h)+.021;e=pchip(ST,ED,h);span=e-b
            n=GX[(GX>=b)&(GX<=e)]
            if len(n)<2:rows.append([0.,0.,0.]);continue
            v=np.interp(n,GX,SKIN[si,j]);length=pull_curve(h,design)
            ux=n-length*ease((n-b)/span)
            rr=(ux-b)/max(.19,e-length-b)
            w0=np.interp(.095,rr,v)
            wm=(v.max()*.965+w0*.035)
            we=np.interp(e,GX,SKIN[si,j])
            rows.append([w0,wm,we])
        stats.append(np.array(rows))
    raw=np.where(y<mid,sample_grid(SKIN[0],x,z),sample_grid(SKIN[1],x,z))
    base,peak,end=[np.where(y<mid,np.interp(z,GZ,stats[0][:,k]),np.interp(z,GZ,stats[1][:,k])) for k in range(3)]
    cut_scale=(1-.14*ease((z-3.73)/.41)) if len(design)>13 else 1.
    end-=design[2]*.98*strength*cut_scale
    left=np.clip((crest-r)/(crest-.095),0,1.25)
    right=np.clip((r-crest)/(1-crest),0,1.15)
    desired=np.where(r<crest,peak-(peak-base)*left**2.05,peak-(peak-end)*right**power)
    w=amount*ease((z-2.37)/.64)*(1-ease((z-4.21)/.46))*ease((r-.075)/.14)*(1-ease((r-.993)/.075))
    if len(design)==14:
        # Anchor the shoulder of the lower billet that meets the turning
        # silhouette in three-quarter view. The fairing remains continuous.
        keep=(1-ease((z-3.34)/.32))*(1-ease((r-.44)/.22))
        w*=1-keep
    return dr+w*(desired-raw-dr)

def move(obj,p,design):
    factor,ridge,cut,neck_bulge,neck_width=design[:5]
    if obj.name=='Knight | '+MANE:
        # Apply the accepted subdivision before cutting so the inherited
        # centered upper bevel, smooth normals and packed UVs are retained.
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    a=rest_coords(world_vertices(obj),p)
    x,y,z=a.T
    back=pchip(ST,POST,z)+.021
    edge=pchip(ST,ED,z)
    mid=pchip(ST,CENTER,z)
    front=-.145-.125*ease((z-3.82)/.55)
    pull=pull_curve(z,design)
    # Back and breast are tangent anchors. Between them the blade narrows
    # while the neck comes up beneath it without breaking native overlap.
    w=np.where(x<edge,ease((x-back)/np.maximum(.2,edge-back)),ease((front-x)/np.maximum(.17,front-edge)))
    xx=x-pull*w
    off=xx-(edge-pull)
    strength=np.clip(pull/.29,0,1)
    rear=np.exp(-((off+.098)/.088)**2)
    groove=np.exp(-((off-.003)/.043)**2)
    t=np.maximum(off,0.)/neck_width
    rounded=t*np.exp(1-t)*ease(off/.095)*ease((front-xx)/.23)
    dr=strength*(ridge*rear-cut*groove+neck_bulge*rounded)
    if len(design)>5:
        back_width,front_width,tip_fair=design[5:8]
        # Carry a continuous facing plane all the way into the leading cut.
        # The section opens more gently on the blade side and rolls rapidly
        # out of the valley onto the front of the actual neck.
        mouth=np.where(off<0,back_width,front_width)
        valley=np.exp(-((off+.004)/mouth)**2)
        blade=ease((xx-back)/.20)*(1-ease((off+.055)/.09))
        blade*=np.exp(-((off+.23)/.23)**2)
        t=np.maximum(off,0.)/neck_width
        neck=t*np.exp(1-t)*ease((front-xx)/.19)
        cut_scale=(1-.14*ease((z-3.73)/.41)) if len(design)>13 else 1.
        dr=strength*(-ridge*blade-cut*valley*cut_scale+neck_bulge*neck)
        # At the foot, the real two-piece surfaces roll into a single
        # envelope. Fair the existing exterior without moving the outline.
        foot=ease((z-1.78)/.19)*(1-ease((z-2.78)/.39))
        weight=foot*np.exp(-((x-edge)/.23)**2)*ease((x-back)/.128)
        correction=np.where(y<mid,sample_grid(TIP[0],x,z),sample_grid(TIP[1],x,z))
        dr+=tip_fair*weight*correction
    dr*=ease((xx-back)/.15)*ease((front-xx)/.14)
    if len(design)>9:dr=fair_face(a,xx,back,edge,pull,mid,dr,design)
    breadth=y-mid
    # The displacement grows monotonically through the thick substrate.
    # Interior vertices near its center keep their original ordering even
    # where a very deep cut lies against a thin, buried neck section.
    radius=np.maximum(.127,(-dr)*1.68+.014) if len(design)>8 else .127
    y2=y+dr*np.tanh(breadth/radius)
    if len(design)>14:
        # Translate the broad lateral shoulder toward the neck by up to
        # 0.035 units. Keep the back midline, front cheek and bottom seat
        # anchored, preserving a smoothly convex face on the whole blade.
        span=np.maximum(.19,edge-pull-back);r=(xx-back)/span
        shift=pchip([2.53,2.73,2.89,3.04,3.19,3.31,3.42,3.58,3.72],
                    [0.,.008,.022,.033,.034,.024,.015,.005,0.],z)
        lateral=ease((abs(breadth)-.116)/.17)*np.exp(-((r-.33)/.34)**2)
        xx=xx+shift*lateral*design[14]
    new=a.copy();new[:,0]=xx;new[:,1]=y2
    delta=posed(new,*p)-posed(a,*p)
    verts=obj.data.vertices;c=np.empty((len(verts),3),np.float32)
    verts.foreach_get('co',c.ravel())
    c+=delta@np.linalg.inv(np.asarray(obj.matrix_world)[:3,:3]).T
    if len(design)>8 and design[8]>0 and obj.name=='Knight | '+MANE:
        from grain import reroute
        reroute(obj,a,new,mid,back,front,edge,pull,design[8])
    if len(design)>13 and design[13] and obj.name=='Knight | '+HEAD:
        from grain import reroute
        # Retain the size of the grain in the newly exposed outer neck by
        # measuring physical distance forward from the original blade.
        shift=xx+pull-x
        w=ease((front-x)/.30)*ease((xx-edge+pull-.012)/.15)*ease((4.42-z)/.26)
        query=x+design[13]*w*np.maximum(0.,shift)
        reroute(obj,a,new,mid,back,front,edge,pull,1.,query=query)
    verts.foreach_set('co',c.ravel());obj.data.update()
    return {'max_dx':float(abs(xx-x).max()),'max_dy':float(abs(y2-y).max()),
            'max_dz':float(abs(delta[:,2]).max()),'changed_vertices':int((np.linalg.norm(delta,axis=1)>1e-6).sum())}

def sculpt(s,index):
    design=DESIGNS[index]
    result={name:move(s.objects['Knight | '+name],pose(s),design) for name in [MANE,HEAD,NECK,BUILD]}
    if len(design)>12 and design[12]!='parent':install_atlas(s,D/f'pigment-{design[12]}.png')
    return result

def install_atlas(s,path):
    mat=s.objects['Knight | '+MANE].active_material
    old=mat.node_tree.nodes['Knight delivered albedo'].image
    assert hashlib.sha256(bytes(old.packed_file.data)).hexdigest()==PIGMENT
    new=bpy.data.images.load(str(path),check_existing=False)
    new.name='Knight walnut | descending blade 012-B';new.colorspace_settings.name='sRGB';new.pack()
    new.filepath='//../../assets/knight/wood-atlas-improvement-012-B.png'
    for m in bpy.data.materials:
        if m.node_tree:
            for n in m.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image==old:n.image=new
    if old.users==0:bpy.data.images.remove(old)

def crop(s,box):
    W,H=s.render.resolution_x,s.render.resolution_y
    x,y,x1,y1=box
    s.render.use_border=s.render.use_crop_to_border=True
    s.render.border_min_x=(x+.1)/W;s.render.border_max_x=(x1+.1)/W
    s.render.border_min_y=(H-y1+.1)/H;s.render.border_max_y=(H-y+.1)/H

def trial(i):
    s=load('parent.blend')
    if i>=0:sculpt(s,i)
    configure_render(s,32)
    s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=8
    crop(s,(175,374,436,716))
    render(s,D/f'study-{i}-walnut.png')
    flat(s);render(s,D/f'study-{i}-clay.png')
    s.render.use_border=s.render.use_crop_to_border=False
    s.render.resolution_x=s.render.resolution_y=520
    angle=pose(s)[2]
    camera(s,angle)
    crop(s,(72,42,317,352));render(s,D/f'study-{i}-side.png')
    camera(s,angle+180)
    crop(s,(218,42,459,352));render(s,D/f'study-{i}-far.png')

def build(i):
    s=load('parent.blend');details=sculpt(s,i)
    from qa_geometry import inspect
    checks=inspect(s)
    assert all(q['folds']==0 for q in checks.values()),checks
    im=s.objects['Knight | '+MANE].active_material.node_tree.nodes['Knight delivered albedo'].image
    physical=bytes(im.packed_file.data);(D/'pigment.png').write_bytes(physical)
    config={'parent_sha256':PARENT,'parent_pigment_sha256':PIGMENT,'pigment_sha256':sha(D/'pigment.png'),'design':i,
            'parameters':DESIGNS[i],'parts':details,'release_texture':Path(im.filepath).name,'native_checks':checks}
    s['knight_atlas_sha256']=config['pigment_sha256']
    s['knight_improvement_012_B']=json.dumps(config)
    configure_render(s,144);save_model(s,D/'knight.blend');config['model_sha256']=sha(D/'knight.blend')
    (D/'parameters.json').write_text(json.dumps(config,indent=2)+'\n')

if __name__=='__main__':
    assert sha(D/'parent.blend')==PARENT and sha(D/'parent-pigment.png')==PIGMENT
    args=sys.argv[sys.argv.index('--')+1:]
    if args[0]=='trial':
        for i in map(int,args[1:]):trial(i)
    if args[0]=='build':build(int(args[1]))
    if 'studio' in args:studio()
    if 'orbit' in args:
        flat_views('knight.blend','')
        s=load('knight.blend');configure_render(s,32);diagnostics(s,'',True)

"""Refine the bilateral crest bevel, burnish its cut face and light the forward shoulder."""
from pathlib import Path
import json,sys,hashlib,shutil
import numpy as np,bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
from survey import MANE,pose,rest_coords,world_vertices
from evidence import load,studio,flat_views
from mission_scene import configure_render,render,save_model,sha
from mission_pose import posed
from diagnostics import diagnostics
PARENT='e865a0c635e99bb07a5262a48499140dc34b0e61c757d1e362913fa1c12aef6a'
PIGMENT='f6e6b26fad1baf22bbf7dd0eb0427cb61b9064245af6acbd268d31068502f4c8'
OVAL='Walnut | poll rear oval'
# Inward bevel roll, undercut, crown polish, arris polish, rear amber strip
# power, strip width, forward window power, window distance, aperture size.
DESIGNS=[(.010,.006,.14,.50,46,.088,10.,.92,.34),
         (.017,.010,.22,.60,51,.070,13.,.92,.30),
         (.021,.013,.26,.50,40,.065,18.,.77,.32),
         (.014,.010,.20,.51,48,.078,16.,1.12,.40)]
DESIGNS += [(.012,.008,.31,.50,72,.078,14.,.80,.22,.11,.36,.7),
            (.014,.009,.35,.59,79,.075,19.,.74,.24,.17,.28,.7),
            (.010,.006,.32,.54,66,.083,20.,.67,.23,.125,.26,.55),
            (.010,.007,.29,.60,74,.083,13.,.61,.20,.19,.20,.85)]
DESIGNS += [(.012,.008,.27,.52,75,.078,2.2,.83,.125,.08,.36,.65,72.,1),
            (.012,.009,.28,.54,81,.075,2.5,.82,.115,.11,.36,.62,58.,1),
            (.009,.007,.24,.52,76,.078,3.4,.85,.145,.10,.32,.7,65.,1),
            (.010,.008,.29,.56,81,.076,2.0,.84,.13,.04,.34,.71,67.,0)]
DESIGNS += [(.012,.010,.25,.61,62,.087,1.85,.78,.122,.103,.29,.68,76.,1,-.004),
            (.013,.012,.27,.56,66,.072,2.45,.81,.141,.095,.32,.69,77.,1,.000),
            (.016,.012,.28,.55,72,.082,2.10,.79,.135,.101,.31,.62,78.,1,.006),
            (.010,.010,.23,.56,58,.090,1.9,.82,.124,.110,.30,.70,80.,1,.011)]
DESIGNS += [(.012,.012,.22,.70,92,.144,2.5,.78,.117,.105,.30,.75,65.,1,-.006,1),
            (.012,.012,.22,.77,101,.169,3.0,.74,.130,.125,.30,.80,70.,1,-.004,1),
            (.012,.012,.20,.75,103,.145,2.9,.77,.117,.070,.30,.71,65.,1,-.003,1),
            (.014,.014,.25,.76,89,.145,3.2,.84,.110,.128,.30,.77,71.,1,-.004,1)]
DESIGNS += [(.008,.026,.205,.73,93,.137,3.35,.78,.115,.107,.30,.75,65.,1,-.005,1),
            (.007,.035,.21,.74,101,.157,3.2,.81,.125,.104,.30,.75,67.,1,-.006,1),
            (.010,.024,.23,.78,98,.151,3.5,.82,.137,.085,.30,.76,65.,1,-.009,1)]
DESIGNS += [(.010,.025,.22,.72,95,.149,3.10,.79,.129,.099,.30,.74,67.,1,-.005,1,1),
            (.010,.034,.21,.74,108,.147,3.05,.80,.121,.095,.30,.76,68.,1,-.005,1,1),
            (.008,.028,.25,.74,104,.155,3.5,.79,.143,.079,.32,.75,66.,1,-.009,1,1)]
DESIGNS += [(.009,.027,.22,.73,105,.148,3.40,.79,.125,.105,.30,.75,66.,1,-.005,1,1,.57),
            (.011,.029,.24,.76,110,.146,3.65,.80,.121,.096,.30,.79,66.,1,-.005,1,1,.88),
            (.008,.022,.22,.73,103,.152,3.15,.77,.117,.112,.30,.77,68.,1,-.005,1,1,1.18)]
DESIGNS += [(.010,.030,.23,.75,101,.141,3.60,.75,.118,.060,.30,.77,70.,1,-.005,1,1,.45,.012,.010,.038,.031),
            (.010,.032,.26,.75,105,.145,3.55,.77,.114,.034,.30,.77,67.,1,-.005,1,1,.45,.017,.014,.047,.042),
            (.010,.028,.25,.74,103,.149,3.70,.76,.128,.031,.30,.76,71.,1,-.006,1,1,.55,.016,.017,.047,.044)]
DESIGNS += [(.010,.031,.25,.75,108,.145,3.55,.77,.071,.115,.30,.77,68.,1,-.005,1,1,.46,.016,.014,.051,.047,.163),
            (.010,.030,.25,.75,108,.145,4.25,.76,.065,.148,.30,.77,68.,1,-.006,1,1,.47,.016,.015,.057,.053,.170)]
def ease(a):
    a=np.clip(a,0,1);return a*a*(3-2*a)
def bell(q,w):return np.exp(-.5*(q/w)**2)
def fiber(obj):
    fine=np.load(D/'wood-grain.npy',mmap_mode='r');h,w=fine.shape;m=obj.data
    vi=np.empty(len(m.loops),np.int32);m.loops.foreach_get('vertex_index',vi)
    uv=np.empty((len(vi),2),np.float32);m.uv_layers['Knight wood atlas'].data.foreach_get('uv',uv.ravel())
    x=np.clip(uv[:,0]*w-.5,0,w-1.001);y=np.clip((1-uv[:,1])*h-.5,0,h-1.001)
    i=x.astype(int);j=y.astype(int);tx=x-i;ty=y-j
    val=(1-ty)*((1-tx)*fine[j,i]+tx*fine[j,i+1])+ty*((1-tx)*fine[j+1,i]+tx*fine[j+1,i+1])
    return np.clip(np.bincount(vi,weights=val)/np.maximum(1,np.bincount(vi))/12.,-1,1)
def roof(a,mesh):
    mesh.calc_loop_triangles();f=np.empty((len(mesh.loop_triangles),3),np.int32);mesh.loop_triangles.foreach_get('vertices',f.ravel())
    tree=BVHTree.FromPolygons(a.tolist(),f.tolist(),all_triangles=True)
    out=np.full(len(a),9.)
    for i,(x,y,z) in enumerate(a):
        if z<4.7 or abs(y)>.40:continue
        q=tree.ray_cast((x,y,6.),(0,0,-1))[0]
        if q:out[i]=max(0,q.z-z)
    return out
def sculpt(s,v):
    p=pose(s);o=s.objects[MANE];m=o.data;a=rest_coords(world_vertices(o),p);x,y,z=a.T;ay=abs(y)
    W=np.interp(x,[-1.,-.78,-.62,-.40,-.20,-.04,.09,.18,.29],[.077,.093,.101,.106,.113,.118,.122,.102,.060])
    dist=roof(a,m);crown=ease((x+1.10)/.32)*ease((.285-x)/.135)*ease((z-4.76)/.15)*ease((.075-dist)/.063)
    # Bring the paired outer knees toward the section midpoint; leave the medial high point in place.
    # The underside returns into a thin native lip at the forehead. Seat that whole lip together.
    shape=crown*ease((.201-ay)/.037)*ease((z-4.873)/.073)
    if len(v)>16:
        # Sweep the whole outer cheek of the cap down the same distance.
        # Both skins of its thin return travel together, leaving one supported edge.
        shape=ease((x+1.085)/.28)*ease((.258-x)/.115)*ease((z-4.57)/.24)
    new=a.copy();nw=shape*bell(ay-W,.045)*ease(ay/.075)
    new[:,1]-=np.sign(y)*v[0]*nw
    new[:,2]-=v[1]*shape*ease((ay-W+.005)/.046)*bell(ay-W-.047,.081)
    if len(v)>16:new[:,2]=z-v[1]*shape*ease((ay-W+.003)/.055)
    if len(v)>17:
        # Carry the outside mass laterally as the face rolls down, while keeping the paired ears seated.
        flank=ease((ay-W-.010)/.096)*shape
        new[:,1]+=np.sign(y)*v[1]*v[17]*flank
    if len(v)>18:
        # Give the broad upper face a little body above the seated ears.
        # One convex return runs noseward and down, carrying the whole terminal shell with it.
        lift=v[18]*shape
        new[:,2]+=lift+v[19]*bell(x+.015,.092)*shape*(1-ease((ay-.09)/.115))
        turnout=ease((x-.046)/.185)*ease((z-4.73)/.18)
        new[:,0]+=v[20]*turnout
        new[:,2]-=v[21]*turnout
    world_delta=posed(new,*p)-posed(a,*p)
    co=np.empty((len(a),3),np.float32);m.vertices.foreach_get('co',co.ravel())
    co+=world_delta@np.linalg.inv(np.asarray(o.matrix_world)[:3,:3]).T;m.vertices.foreach_set('co',co.ravel());m.update()
    coat=m.attributes['Knight varnish coverage'];old=np.empty(len(a),np.float32);coat.data.foreach_get('value',old)
    grain=fiber(o);cap=(1-ease((ay-W+.012)/.037))
    cut=bell(ay-W,.014);shoulder=.80+.20*ease((x+.42)/.46)
    if len(v)>9:shoulder=.14+.86*ease((x+.27)/.40)
    if len(v)>15:shoulder=.035+.73*ease((x+.090)/.26)
    finish=.018+v[2]*cap*(.78+.55*grain)*shoulder+v[3]*cut*(.85+.21*grain)
    if len(v)>9:
        finish+=v[11]*ease((old-.10)/.48)*bell(ay-W,.045)*(.22+.24*grain)
    weight=crown*ease((.29-ay)/.09)
    o.data.attributes['Knight varnish coverage'].data.foreach_set('value',np.float32(np.clip(old+(finish-old)*weight,0,1)))
    m.update();bpy.context.view_layer.update()
    return {'max_displacement':float(np.linalg.norm(new-a,axis=1).max()),'moved_vertices_gt_1e-6':int((np.linalg.norm(new-a,axis=1)>1e-6).sum()),
            'max_abs_varnish_change':float(abs((finish-old)*weight).max())}
def lighting(s,v):
    oval=s.objects[OVAL];oval.data.energy=v[4];oval.data.color=(1.,.45,.16)
    oval.data.size_y=v[5];oval.data.size*=.94;oval.location.x+=.13
    # A real warm window above and forward of the poll lets the curved face catch a separate, broader reflection.
    source=s.objects['Poll flag | Walnut upper strip'];light=source.copy();light.data=source.data.copy()
    light.name='Walnut | forward poll window';s.collection.objects.link(light)
    light.light_linking.receiver_collection=oval.light_linking.receiver_collection
    target=Vector((-.281,-.082,5.104))
    normal=Vector((.235,.215,.947)).normalized();light.location=target+v[7]*normal
    if len(v)>9:
        light.location.x+=v[9];target.x+=.021
        normal=(light.location-target).normalized()
    light.rotation_euler=(-normal).to_track_quat('-Z','Y').to_euler()
    lamp=light.data;lamp.shape='DISK';lamp.size=v[8];lamp.energy=v[6];lamp.color=(1.,.78,.56)
    if len(v)>22:
        transverse=Vector((0,1,0));across=(transverse-normal*transverse.dot(normal)).normalized()
        along=across.cross(normal).normalized()
        light.rotation_euler=Matrix(np.column_stack([along,across,normal])).to_euler()
        lamp.shape='ELLIPSE';lamp.size=v[8];lamp.size_y=v[22];lamp.color=(1.,.81,.60)
    if len(v)>9:
        lamp.spread=np.deg2rad(v[12] if len(v)>12 else 37.)
        oval.data.color=(1.,.42,.145)
    if len(v)>14:
        from reflector import fit
        fit(s,oval,v)
    return {o.name:{'energy':o.data.energy,'size':o.data.size,'size_y':o.data.size_y,'color':list(o.data.color),'world_position':list(o.location)} for o in [light,oval]}
def border(s):
    x,y,a,b=240,278,508,414;s.render.use_border=s.render.use_crop_to_border=True
    s.render.border_min_x=(x+.1)/1254;s.render.border_max_x=(a+.1)/1254;s.render.border_min_y=(1254-b+.1)/1254;s.render.border_max_y=(1254-y+.1)/1254
def proposal(s,i):
    v=DESIGNS[i];stats={'shape':sculpt(s,v),'studio':lighting(s,v)}
    if len(v)>13 and v[13]:
        material=s.objects[MANE].active_material;old=material.node_tree.nodes['Knight delivered albedo'].image
        assert sha(D/'parent-pigment.png')==PIGMENT
        im=bpy.data.images.load(str(D/'crown-walnut.png'),check_existing=False);im.name='Knight walnut | worked crown 016-B'
        im.colorspace_settings.name='sRGB';im.pack();im.filepath='//../../assets/knight/wood-atlas-improvement-016-B.png'
        for mat in bpy.data.materials:
            if mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.type=='TEX_IMAGE' and node.image==old:node.image=im
        if old.users==0:bpy.data.images.remove(old)
        s['knight_atlas_sha256']=sha(D/'crown-walnut.png')
    return stats
def trial(i):
    s=load('parent.blend')
    if i>=0:proposal(s,i)
    configure_render(s,64);s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=6
    border(s);render(s,D/f'trial-{i}.png')
def build(i):
    s=load('parent.blend');stats=proposal(s,i)
    from sections import sections
    stats['sections']=sections(s)
    assert stats['sections']['max_mirror_abs']<.004
    from native import verify_mane
    stats['geometry']=verify_mane(s)
    image=s.objects[MANE].active_material.node_tree.nodes['Knight delivered albedo'].image
    source=D/('crown-walnut.png' if len(DESIGNS[i])>13 and DESIGNS[i][13] else 'parent-pigment.png')
    pigment=hashlib.sha256(bytes(image.packed_file.data)).hexdigest()
    assert sha(source)==s['knight_atlas_sha256']==pigment
    shutil.copyfile(source,D/'pigment.png')
    stats.update({'design':i,'parameters':DESIGNS[i],'parent_sha256':PARENT,'pigment_sha256':pigment,
                  'parent_pigment_sha256':PIGMENT,'pigment_filename':Path(image.filepath).name})
    s['knight_improvement_016_B']=json.dumps(stats);configure_render(s,144);save_model(s,D/'knight.blend')
    stats['model_sha256']=sha(D/'knight.blend');(D/'parameters.json').write_text(json.dumps(stats,indent=2)+'\n')
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];assert sha(D/'parent.blend')==PARENT
    if args[0]=='trial':
        for i in map(int,args[1:]):trial(i)
    if args[0]=='build':build(int(args[1]))
    if 'studio' in args:studio()
    if 'orbit' in args:
        flat_views('knight.blend','');s=load('knight.blend');configure_render(s,32);diagnostics(s,'',True)

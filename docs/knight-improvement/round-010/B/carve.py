"""Carve a centered convex poll, two supported shoulder bevels, and seat the ears."""
from pathlib import Path
import hashlib,json,sys
import bpy,numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(ROOT/'scripts/knight')]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,json_file,render,save_model,sha,use_side_camera,world_vertices
from evidence import load,flat,flat_views,studio
from diagnostics import diagnostics,camera

PARENT='8e015620e552bda2c1e67866da8a7a3ba0e671c16deb22d93c07fb6c7859121d'
PIGMENT='86debdcce4b5b6075ae7510cb25f77066ae912cfb8e1a0c4a49101ed43b79978'
# Depth and width of crown, physical bevel width/slope, seating of the
# paired ear roots, dorsal satin weight, and the original mane card energy.
DESIGNS=[(.27,1.04,.023,.63,.025,.84,105.),
         (.33,1.10,.030,.70,.045,.93,100.),
         (.22,.97,.027,.58,.036,.95,115.),
         (.28,1.04,.027,.64,.065,.94,105.),
         (.25,1.17,.028,.64,.055,.98,86.,.070,18.),
         (.24,1.30,.026,.60,.055,.98,92.,.110,21.),
         (.25,1.21,.026,.61,.044,.99,85.,.130,23.),
         (.28,1.10,.025,.62,.051,.98,82.,.043,18.,.65),
         (.28,1.10,.024,.62,.050,.98,86.,.047,18.,1.12),
         (.29,1.10,.024,.64,.053,.99,87.,.040,18.,1.50),
         (.28,1.10,.024,.62,.050,.98,85.,.043,19.,1.00,.034),
         (.28,1.10,.024,.62,.051,.99,84.,.037,19.,.90,.052),
         (.28,1.10,.024,.62,.051,.99,84.,.037,19.,.90,.052,.073),
         (.28,1.10,.024,.62,.051,.99,84.,.037,19.,.83,.049,.090)]

def pose(scene):
    d=json.loads(scene['knight_mission_pose'])
    return [d[k] for k in ('dx','dy','twist_degrees')]

def apply_rest(obj,old,new,p):
    delta=posed(new.reshape(-1,3),*p)-posed(old.reshape(-1,3),*p)
    a=np.empty((len(delta),3),np.float32)
    obj.data.vertices.foreach_get('co',a.ravel())
    a+=delta@np.linalg.inv(np.asarray(obj.matrix_world)[:3,:3]).T
    obj.data.vertices.foreach_set('co',a.ravel());obj.data.update()
    return np.linalg.norm(delta,axis=1)

def ears(scene,amount,finish,p,side_seat=0.,side_width=11.):
    result={}
    # The upper inside face is row 62 relative to a dorsal center at row 0.
    # Roll the same material and small geometric cut onto both physical ears.
    station=np.array([0.,.28,.99,1.,.68,.11,0.])[:,None]
    angle=(np.arange(64)-62+32)%64-32
    smooth_top=np.exp(-(angle/11.)**2)[None,:]
    face=station*smooth_top
    for side,sign in [('near',-1),('far',1)]:
        ob=scene.objects['Knight | '+side+' swept ear']
        old=rest_coords(world_vertices(ob),p).reshape(7,64,3)
        new=old.copy()
        new[:,:,1]-=sign*amount*.66*face
        new[:,:,2]-=amount*face
        # Seat the convex side of the ear against the poll. The slanted
        # trailing tip and the foremost end retain their parent coordinates.
        side_face=station*np.exp(-(((np.arange(64)-4+32)%64-32)/side_width)**2)[None,:]
        new[:,:,1]-=sign*side_seat*side_face
        move=apply_rest(ob,old,new,p)
        attr=ob.data.attributes['Knight varnish coverage']
        var=np.empty(len(attr.data),np.float32);attr.data.foreach_get('value',var)
        satin=np.maximum(face,side_face if side_seat else 0.)
        changed=var.reshape(7,64)+(0.019-var.reshape(7,64))*finish*satin
        attr.data.foreach_set('value',changed.astype(np.float32).ravel())
        ob.data.update()
        result[side]={'max_displacement':float(move.max()),'end_ring_displacement':float(move.reshape(7,64)[[0,6]].max())}
    return result

def sculpt(scene,design):
    drop,spread,bevel,slope,seat,ear_finish,_=design[:7]
    ob=scene.objects['Knight | swept rounded mane'];p=pose(scene)
    old=rest_coords(world_vertices(ob),p).reshape(13,64,3)
    new=old.copy()
    for i,weight in enumerate([1.,1.,1.,1.,.98,.70,.24]):
        ring=old[i]
        repaired=i==0 and len(design)>11
        if repaired:
            # Seat the whole forehead cap under the brow along with the
            # outer bevel. The buried lower ring otherwise crosses the
            # steepened upper bevel where the first section turns down.
            ring=ring.copy();ring[:,2]-=design[11]*design[9];new[i]=ring
        canonical=(ring[:33]+ring[(-np.arange(33))%64]*[1,-1,1])*.5
        center=canonical[32,[0,2]]
        axis=center-canonical[0,[0,2]]
        axis/=np.linalg.norm(axis)
        # All new dome and bevel points share a transverse plane. The smooth
        # crest is a parabola between shoulders, with a single medial peak.
        peak=center+axis*[.005,.012,.013,.012,.009,.004,0.,0.][i]
        peak=peak+np.array([[.061,-.021],[.020,.002],[.003,0.],[0.,0.],[0.,0.],[0.,0.],[0.,0.],[0.,0.]])[i]
        W=canonical[25,1]*spread*[1.19,.85,1.0,1.08,1.12,1.08,1.,1.][i]
        if i<2 and len(design)>9:
            # Turn the two bevels around the forehead in three dimensions.
            # The first transverse ring tucks into the skull as the edge
            # widens; the second stays close to the crest of the brow.
            bend=design[9]
            peak+=bend*np.array([[-.043,-.052],[.005,.011]])[i]
            W+=bend*[.028,-.003][i]
            if repaired:
                peak[1]+=design[11]*bend
                W=min(W,.82*canonical[17,1])
        width=bevel*[.86,.96,1.,1.,.88,.77,.68,.64][i]
        inner=W-.5*width;outer=W+.5*width
        cap_drop=drop*inner
        def dome(y):return -cap_drop*(y/inner)**2
        def arris(y):return -cap_drop-slope*(y-inner)
        y=np.zeros(33);r=np.zeros(33)
        y[24:27]=[outer,W,inner];r[24:27]=arris(y[24:27])
        y[27:]=inner*np.array([.973,.81,.60,.39,.19,0.])
        r[27:]=dome(y[27:])
        y[23]=outer+.0024
        r[23]=arris(outer)-.0024*1.70
        # Rejoin the parent flank below the cut with a cubic that is tangent
        # to the parent near station 17 and to the steep face at station 23.
        a=np.array([canonical[17,1],(canonical[17,[0,2]]-peak)@axis])
        z=np.array([y[23],r[23]])
        dr=z[1]-a[1];dw=a[0]-z[0]
        c1=a+np.array([-.06*dw,.39*dr]);c2=z+np.array([.32*dw,-.32*dw*1.70])
        t=np.array([.16,.36,.56,.76,.91])
        curve=(1-t[:,None])**3*a+3*((1-t)**2*t)[:,None]*c1+3*((1-t)*t*t)[:,None]*c2+t[:,None]**3*z
        y[18:23]=curve[:,0];r[18:23]=curve[:,1]
        dst=canonical.copy();dst[18:,1]=y[18:]
        dst[18:,[0,2]]=peak+r[18:,None]*axis
        blend=np.ones((33,1));blend[:18]=0;blend[18:23,0]=[.22,.49,.74,.91,.98]
        if len(design)>10:
            # Gently fill the hollow under the free ear end on both flanks.
            # Keep the arris and entire medial parabola at their measured
            # positions so the extra shoulder cannot widen the crown top.
            flank=design[10]*[0.,0.,.18,.91,1.,.28,0.][i]
            mask=np.array([.29,.66,1.,.78,.38])
            dst[18:23,1]+=flank*mask
            dst[18:23,[0,2]]+=.45*flank*mask[:,None]*axis
        dst=canonical+weight*blend*(dst-canonical)
        # Write the very same section on each side of the unposed midplane.
        new[i,18:33]=dst[18:]
        new[i,33:47]=dst[31:17:-1]*[1,-1,1]
        if repaired:
            # A planar end loop makes the closed subdivided end face
            # robust even where it is fully embedded in the forehead.
            radius=(new[i][:,[0,2]]-peak)@axis
            new[i][:,[0,2]]=peak+radius[:,None]*axis
    moves=apply_rest(ob,old,new,p)
    ear=ears(scene,seat,ear_finish,p,*design[7:9])
    bpy.context.view_layer.update()
    return {'parent_sha256':PARENT,'pigment_sha256':PIGMENT,
            'parameters':dict(zip(['dome_drop_over_width','shoulder_spread','bevel_width','bevel_slope','ear_inset','dorsal_satin','card_watts','additional_ear_side_seating','ear_side_width','forehead_bend','rear_shoulder_fill','forehead_cap_seat'],design)),
            'mane_changed_points':int((moves>1e-6).sum()),'maximum_mane_displacement':float(moves.max()),
            'maximum_lower_six_rings_displacement':float(moves.reshape(13,64)[7:].max()),'ears':ear}

def card(scene,design):
    from poll_card import fitted,meter
    return fitted(scene,meter(scene),0.,design[6],.105)

def border(scene,coords):
    a,b,c,d=coords;scene.render.use_border=scene.render.use_crop_to_border=True
    scene.render.border_min_x=(a+.05)/1254;scene.render.border_max_x=(c+.05)/1254
    scene.render.border_min_y=(1254-d+.05)/1254;scene.render.border_max_y=(1254-b+.05)/1254

def preview(idx):
    scene=load('parent.blend');des=DESIGNS[idx]
    sculpt(scene,des)
    configure_render(scene,72);border(scene,(245,281,524,434))
    render(scene,OUT/f'common-{idx}-crest.png')
    card(scene,des);render(scene,OUT/f'trial-{idx}-crest.png')
    flat(scene);render(scene,OUT/f'trial-{idx}-clay-crest.png')
    use_side_camera(scene);border(scene,(220,92,819,410));scene.render.resolution_percentage=70
    render(scene,OUT/f'trial-{idx}-clay-side.png')

def build(index):
    scene=load('parent.blend');design=DESIGNS[index]
    atlas=scene.objects['Knight | swept rounded mane'].active_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image
    assert hashlib.sha256(bytes(atlas.packed_file.data)).hexdigest()==sha(OUT/'pigment.png')==PIGMENT
    info=sculpt(scene,design);info['design_index']=index
    from check_final import self_cross
    assert all(self_cross(scene,name)==0 for name in ['swept rounded mane','near swept ear','far swept ear'])
    info['pigment_datablock']=atlas.name;info['existing_poll_card']=card(scene,design)
    scene['knight_improvement_010_B']=json.dumps(info)
    configure_render(scene,144);save_model(scene,OUT/'knight.blend')
    info['model_sha256']=sha(OUT/'knight.blend')
    json_file(OUT/'parameters.json',info)
if __name__=='__main__':
    assert sha(OUT/'parent.blend')==PARENT
    if '--test' in sys.argv:
        for v in sys.argv[sys.argv.index('--test')+1:]:preview(int(v))
    if '--build' in sys.argv:build(int(sys.argv[sys.argv.index('--build')+1]))
    if '--studio' in sys.argv:studio()
    if '--parent-flat' in sys.argv:flat_views('parent.blend','parent-')
    if '--orbit' in sys.argv:
        flat_views('knight.blend','');scene=load('knight.blend');configure_render(scene,32);diagnostics(scene,'',True)

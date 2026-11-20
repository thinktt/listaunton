"""Carry the hanging blade and its neck seat through a common bilateral carving-space warp."""
from pathlib import Path
import hashlib, json, sys
import bpy
import numpy as np

sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
ROOT=D.parents[2]
sys.path.insert(0,str(ROOT/'scripts/knight'))
from lower_carving_fit import rest_coords, ease
from mission_pose import posed
from mission_scene import world_vertices, sha, save_model, json_file, configure_render
from refine_eye import apply_world

PARENT='c4e629d930d907d77885c01dd430cab58e99e26a26e04b63d2a36b373ecdac58'
# Rest height, inherited seam x, desired x displacement, outward reach, rise.
# Each station is a cross-section of the paired join. The end stations recede
# under the ear and lower neck seat, outside the exposed middle of the blade.
STATIONS=np.array([
 [2.39,-.925, .000,.000,.000], [2.58,-.899,-.019,.005,.007],
 [2.80,-.839,-.070,.035,.047], [3.02,-.752,-.168,.073,.098],
 [3.23,-.675,-.251,.096,.126], [3.41,-.662,-.282,.105,.136],
 [3.58,-.653,-.315,.112,.141], [3.74,-.644,-.332,.118,.148],
 [3.90,-.628,-.337,.134,.170], [4.05,-.595,-.308,.156,.202],
 [4.18,-.565,-.225,.128,.161], [4.32,-.530,-.112,.072,.078],
 [4.53,-.470, .000,.000,.000]])

def profile(z, values):
    zs=STATIONS[:,0]
    slopes=np.diff(values)/np.diff(zs)
    tangent=np.zeros(len(values))
    good=slopes[:-1]*slopes[1:]>0
    tangent[1:-1][good]=2/(1/slopes[:-1][good]+1/slopes[1:][good])
    j=np.clip(np.searchsorted(zs,z,side='right')-1,0,len(zs)-2)
    width=zs[j+1]-zs[j]; t=np.clip((z-zs[j])/width,0,1)
    return ((2*t**3-3*t**2+1)*values[j]+(t**3-2*t**2+t)*width*tangent[j]
            +(-2*t**3+3*t**2)*values[j+1]+(t**3-t**2)*width*tangent[j+1])

def reshape(rest):
    x,y,z=rest.T
    xjoin,dx,dy,dz=[profile(z,STATIONS[:,k]) for k in (1,2,3,4)]
    u=x-xjoin
    # The compressing half is a monotone cubic with a fixed heel and a
    # nonzero derivative, including at the station with the longest reach.
    left=ease(u,-.66,.0)
    right=1-ease(u,.0,.76)
    lateral=ease(abs(y),.018,.215)
    reach=np.where(u<0,left,right)*lateral
    # A narrow convex bronze-tool turn behind the carving and a deeper trough
    # under its inner edge run all the way to the seat, in native bilateral Y.
    weight=ease(-dx,0,.240)
    roll=.015*np.exp(-((u+.130)/.104)**2)
    hollow=-.127*np.exp(-((u+.010)/.086)**2)
    cheek=.063*np.exp(-((u-.100)/.078)**2)
    out=rest.copy()
    out[:,0]+=(dx-.045*weight)*reach
    out[:,1]+=np.sign(y)*.48*dy*reach+np.tanh(y/.18)*(roll+hollow+cheek)*weight
    out[:,2]+=.48*dz*reach
    return rest+(out-rest)*(1-ease(x,-.16,.08))[:,None]

def broad_face_delta(rest):
    """Blend the old secondary shoulder into one convex transverse section."""
    a=rest.reshape(-1,64,3)
    b=reshape(rest).reshape(a.shape)
    correction=np.zeros(a.shape[:2],np.float32)
    for i,row in enumerate(b):
        for side in (-1,1):
            ids=np.arange(10,26)*side%64
            samples=row[ids]
            chord=samples[-1,[0,2]]-samples[0,[0,2]]
            t=np.clip(((samples[:,[0,2]]-samples[0,[0,2]])@chord)/(chord@chord),0,1)
            d=abs(samples[:,1]);bow=.077*np.linalg.norm(chord)/.42
            desired=(1-t)*d[0]+t*d[-1]+4*bow*t*(1-t)
            active=ease(a[i,ids,2],2.20,2.77)*(1-ease(a[i,ids,2],4.13,4.53))
            active*=ease(t,0,.13)*(1-ease(t,.95,1))
            correction[i,ids]=(desired-d)*np.sign(samples[:,1])*active*.95
    return correction.ravel()

def refine_cage(obj):
    bpy.context.view_layer.objects.active=obj
    m=next(m for m in obj.modifiers if m.type=='SUBSURF')
    assert (m.levels,m.render_levels)==(2,2)
    m.levels=m.render_levels=1
    m.use_limit_surface=False
    bpy.ops.object.modifier_apply(modifier=m.name)
    m=obj.modifiers.new('Carved blade finish','SUBSURF')
    m.levels=m.render_levels=1

def main():
    assert sha(D/'parent.blend')==PARENT
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False)
    scene=bpy.context.scene
    cfg=json.loads(scene['knight_mission_pose'])
    pose=[cfg[k] for k in ('dx','dy','twist_degrees')]
    stats={}
    for name in ['swept rounded mane','continuous horse head and neck','curved neck and chest','coherent skull cheek and conical muzzle']:
        obj=scene.objects['Knight | '+name]
        if name=='swept rounded mane':
            smooth=broad_face_delta(rest_coords(world_vertices(obj),pose))
            band=obj.data.attributes.new('Work | convex broad face','FLOAT','POINT')
            band.data.foreach_set('value',smooth);refine_cage(obj)
        world=world_vertices(obj)
        rest=rest_coords(world,pose);out=reshape(rest)
        if name=='swept rounded mane':
            band=obj.data.attributes['Work | convex broad face'];smooth=np.empty(len(rest),np.float32)
            band.data.foreach_get('value',smooth);out[:,1]+=smooth;obj.data.attributes.remove(band)
        delta=posed(out,*pose)-posed(rest,*pose)
        apply_world(obj,world+delta)
        stats[name]={'vertices':len(rest),'moved':int(np.count_nonzero(np.linalg.norm(delta,axis=1)>1e-7)), 'max_displacement':float(np.linalg.norm(delta,axis=1).max())}
    scene['knight_round_012_a']='Bilateral curved maneuver and seated neck, worked in rest space'
    bpy.context.view_layer.update()
    img=scene.objects['Knight | continuous horse head and neck'].active_material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.image
    original_atlas=hashlib.sha256(bytes(img.packed_file.data)).hexdigest()
    assert original_atlas==sha(D/'source-atlas.png')
    replacement=bpy.data.images.load(str(D/'pigment.png'),check_existing=False)
    replacement.name='Knight walnut | hanging blade 012-A'
    replacement.pack()
    img.user_remap(replacement)
    img=replacement
    pigment=hashlib.sha256(bytes(img.packed_file.data)).hexdigest()
    configure_render(scene,144)
    save_model(scene,D/'knight.blend')
    json_file(D/'parameters.json',{'parent_sha256':PARENT,'model_sha256':sha(D/'knight.blend'),'pose':pose,'stations':STATIONS.tolist(),'packed_atlas_sha256':pigment,'parent_atlas_sha256':original_atlas,'sculpted_objects':stats})
    print('CANDIDATE',sha(D/'knight.blend'),stats,flush=True)
if __name__=='__main__':main()

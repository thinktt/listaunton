"""Evaluate the inherited physical eyelid reflection without changing the eye carving."""
from pathlib import Path
import sys
import bpy
import numpy as np
from mathutils import Matrix

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(ROOT/'scripts/knight')]
from evidence import load
from mission_scene import configure_render,json_file,render

PARENT="1837b02f0c472044a8e86ffd112d15dbe007eb70d9a4330d86f8f073b7440208"
TRIALS=[
    (None,0.,0.,0.),
    (None,0.,0.,.16),
    ((481,519),-1,.48,.10),
    ((481,519),-1,.48,.45),
    ((482,509),0,.46,.28),
    ((487,518),-3,.40,.24),
    ((481,516),0,.43,.048),
    ((482,507),1,.41,.060),
    ((487,517),0,.44,.064),
    ((482,510),-.5,.36,.082),
    ((482,508),1,.38,.085),
    ((481,516),0,.43,.009),
    ((487,517),0,.44,.010),
    ((481,519),-1,.48,.045),
    ((481,516),0,.43,.014),
]

def feather_finish(scene,amount):
    from lower_carving_fit import rest_coords
    from mission_scene import world_vertices
    import json
    posea=json.loads(scene['knight_mission_pose'])
    pose=[posea[k] for k in ('dx','dy','twist_degrees')]
    obj=bpy.data.objects['Knight | continuous horse head and neck']
    rest=rest_coords(world_vertices(obj),pose)
    along=np.array([1.,-.76])
    along/=np.linalg.norm(along)
    across=np.array([-along[1],along[0]])
    diff=rest[:,[0,2]]-np.array([.412,4.158])
    u,v=diff@along,diff@across
    # Grain facing across the convex cheek takes a softer finish; the lower
    # ledge keeps most of its buffed finish through the middle and loses
    # sheen at the fine earward and noseward ends.
    cheek=np.exp(-((u-.066)/.242)**2-((v+.176)/.074)**2)
    tips=(np.exp(-((u+.157)/.082)**2)+np.exp(-((u-.181)/.080)**2))*np.exp(-((v+.070)/.045)**2)
    trim=np.clip((.72*cheek+.52*tips)*amount,0,.87)
    trim[(np.abs(rest[:,1])<.14)|(abs(u)>.49)|(v>.00)|(v<-.38)]=0
    attr=obj.data.attributes['Knight varnish coverage']
    before=np.empty(len(rest),np.float32)
    attr.data.foreach_get('value',before)
    after=before*(1-trim)
    attr.data.foreach_set('value',after.astype(np.float32))
    obj.data.update()
    return int(((before-after)>.001).sum())

def fit(scene,index):
    span,dy,distance,energy=TRIALS[index]
    lamp=bpy.data.objects['Eye reflection lower']
    if span:
        import json
        rays=json.loads((OUT/'parent-eyelid-rays.json').read_text())
        assert rays['source_sha256']==PARENT
        points=[]
        directions=[]
        for x in np.linspace(*span,10):
            y=np.interp(x,[476,488,504,518,530],[488,495,499,500,499])+dy
            hit=rays['hits'][f'{round(x)},{round(y)}']
            if hit['part']!='Knight | continuous horse head and neck':continue
            points.append(hit['position'])
            directions.append(hit['mirror'])
        points=np.asarray(points)
        directions=np.asarray(directions)
        normal=directions.mean(axis=0)
        normal/=np.linalg.norm(normal)
        plane=points.mean(0)+distance*normal
        intersect=points+directions*(((plane-points)@normal)/(directions@normal))[:,None]
        center=intersect.mean(0)
        _,_,axis=np.linalg.svd(intersect-center,full_matrices=False)
        long=axis[0]-axis[0].dot(normal)*normal
        long/=np.linalg.norm(long)
        short=np.cross(normal,long)
        vectors=np.column_stack([long,short,normal])
        spread=(intersect-center)@vectors[:,:2]
        low,high=np.quantile(spread,[.035,.965],axis=0)
        lamp.location=center+vectors[:,:2]@((low+high)/2)
        lamp.rotation_euler=Matrix(vectors.tolist()).to_euler()
        lamp.data.shape='ELLIPSE'
        lamp.data.size,lamp.data.size_y=high-low+[.055,.045]
        lamp.data.spread=np.radians(42)
        if 6<=index<=10 or index in (11,12,14):
            optical={11:6,12:8,14:6}.get(index,index)
            long_scale,short_scale,angle=[(1.05,1.9,20),(.88,2.5,16),
                    (1.05,2.4,22),(.82,2.7,13),(.72,3.8,17)][optical-6]
            lamp.data.size*=long_scale
            lamp.data.size_y*=short_scale
            lamp.data.spread=np.radians(angle)
    finish=feather_finish(scene,{11:.58,12:.70,13:.80,14:.85}[index]) if index>=11 else 0
    if index:lamp.data.energy=energy
    bpy.context.view_layer.update()
    return {'lamp':lamp.name,'position':list(lamp.location),'axes':[lamp.data.size,lamp.data.size_y],
            'energy':lamp.data.energy,'rotation':list(lamp.rotation_euler),'spread_rad':lamp.data.spread,
            'refinished_cheek_vertices':finish}

if __name__=='__main__':
    from carve import crop
    from mission_scene import use_side_camera
    data={}
    side='--side' in sys.argv
    indices=([0,11,12,14] if side else range(11,len(TRIALS)) if '--feather' in sys.argv else range(6,11) if '--soft' in sys.argv else range(6))
    for i in indices:
        sc=load('parent.blend')
        data[i]=fit(sc,i)
        configure_render(sc,112)
        if side:use_side_camera(sc)
        crop(sc,(590,283,735,371) if side else (452,449,554,522))
        render(sc,OUT/(f'eye-side-{i}.png' if side else f'eyelid-{i}.png'))
    json_file(OUT/(f'eye-side-samples.json' if side else 'eyelid-samples.json'),data)

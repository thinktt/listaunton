"""Cut a narrow bilateral arris around a single domed poll and seat its brow end."""
from pathlib import Path
import json
import sys
import bpy
import numpy as np
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(ROOT/'scripts/knight')]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,json_file,render,save_model,sha,use_side_camera,world_vertices
from evidence import flat,flat_views,load,studio
from diagnostics import diagnostics

PARENT='53ca17473c08fc898e6c29bd5189e4188b3573e003719362cabb102ab621f757'
# Dome's edge slope, its lateral width relative to the old edge, outer face
# control, downward turn into the poll, forward insertion and additional width.
DESIGNS=[(.45,1.03,.78,.048,.093,.034,0.,0.),(.67,1.12,.91,.075,.131,.049,0.,0.),
         (.32,.98,1.02,.057,.132,.042,0.,0.),(.51,1.18,1.15,.072,.151,.067,0.,0.),
         (.39,1.07,.88,.067,.143,.052,.125,.18),
         (.34,1.10,.94,.077,.167,.069,.198,.32),
         (.29,1.04,.89,.076,.154,.067,.248,.27),
         (.35,1.04,.86,.064,.151,.056,.108,.10,.135),
         (.31,1.04,.86,.063,.151,.056,.118,.10,.190),
         (.34,1.04,.86,.052,.142,.051,.125,.08,.100),
         (.38,1.04,.88,.051,.126,.042,.113,.10,.088,1.),
         (.34,1.04,.86,.051,.128,.054,.104,.09,.120,1.),
         (.38,1.04,.87,.051,.126,.052,.102,.12,.080,1.),
         (.39,1.04,.83,.056,.124,.045,.047,.16,.164,1.),
         (.42,1.04,.84,.056,.124,.045,.056,.16,.149,1.),
         (.39,1.04,.83,.056,.124,.045,.055,.16,.146,1.,.035,.52),
         (.39,1.04,.83,.056,.124,.045,.055,.16,.146,1.,.0245,.52),
         (.39,1.04,.83,.056,.124,.045,.055,.16,.146,1.,.0245,.52,.64),
         (.39,1.04,.83,.056,.124,.045,.054,.16,.131,1.,.0245,.52,.79),
         (.39,1.04,.83,.056,.124,.045,.050,.16,.121,1.,.0245,.52,.87),
         (.39,1.04,.83,.056,.124,.045,.052,.16,.130,1.,.0245,.52,.79,.076)]

def smooth(v):
    t=np.clip(v,0,1)
    return t*t*(3-2*t)

def pose(scene):
    p=json.loads(scene['knight_mission_pose'])
    return [p[k] for k in ('dx','dy','twist_degrees')]

def sculpt(scene,design):
    slope,width_ratio,fall,turn,insert,extra,dome_lift,shoulder_lift=design[:8]
    lean=design[8] if len(design)>8 else 0
    arched=design[9] if len(design)>9 else 0
    bevel=design[10] if len(design)>10 else 0
    obj=scene.objects['Knight | swept rounded mane']
    source=world_vertices(obj)
    p=pose(scene)
    c=rest_coords(source,p).reshape(13,64,3)
    out=c.copy()
    for i,weight in enumerate([1.,1.,1.,1.,.93,.63,.20,0.]):
        old=c[i]
        mid=.5*(old[0]+old[32])
        axis=old[32,[0,2]]-old[0,[0,2]]
        axis/=np.linalg.norm(axis)
        peak=np.linalg.norm(old[32,[0,2]]-mid[[0,2]])
        tip=[1.,.54,.07,0.,0.,0.,0.,0.][i]
        if arched:tip=[1.,.24,.008,0.,0.,0.,0.,0.][i]
        for half in (1,-1):
            indices=np.array([half*k%64 for k in range(33)])
            rows=old[indices]
            breadth=half*(rows[:,1]-mid[1])
            radial=(rows[:,[0,2]]-mid[[0,2]])@axis
            span=np.max(breadth)
            edge_width=breadth[25]*width_ratio+extra*tip
            end=np.array([edge_width,peak-.5*slope*edge_width-turn*tip])
            start=np.array([breadth[4],radial[4]])
            ctrl1=np.array([1.42*span,radial[4]+.040*peak])
            ctrl2=end+np.array([.49*span,-fall*peak])
            # One continuous flank from the inner root to the sharp cut.
            # Place a close support line either side of the arris, so only
            # a narrow physical bevel survives subdivision.
            t=np.linspace(0,1,22)
            t[-3:]=[.941,.981,1.]
            delta=1-t
            side=(delta[:,None]**3*start+3*(delta*delta*t)[:,None]*ctrl1+
                  3*(delta*t*t)[:,None]*ctrl2+t[:,None]**3*end)
            # A single convex cap crosses the medial crest with a horizontal
            # tangent. This removes the old flat shelves and dorsal crease.
            u=np.array([1,.966,.798,.637,.472,.309,.148,0.])
            cap=np.column_stack((edge_width*u,peak+(end[1]-peak)*u*u))
            new=np.vstack((np.column_stack((breadth[:4],radial[:4])),side,cap[1:]))
            dst=rows.copy()
            dst[:,1]=mid[1]+half*new[:,0]
            dst[:,[0,2]]+=(new[:,1]-radial)[:,None]*axis
            # Carry the crest higher through the saddle visible beneath the
            # far ear, with a continuous tangent at the medial line. The
            # station envelope disappears before the forehead and lower neck.
            bell=[.13,.45,.94,1.,.69,.22,.0,.0][i]
            if lean:bell=[.38,.83,1.,.93,.63,.24,0.,0.][i]
            lifted=np.r_[np.zeros(4),shoulder_lift*t**2,
                         shoulder_lift+(1-shoulder_lift)*(1-u[1:]**2)**1.45]
            dst[:,2]+=dome_lift*bell*lifted
            if arched:
                # Carry the arris over the brow before it returns into the
                # forehead, avoiding a straight diagonal cut into the tip.
                rise=[.009,.067,.044,.022,.013,0.,0.,0.][i]
                dst[:,2]+=rise*np.r_[np.zeros(4),t**2,.14+.86*u[1:]**2]
            dst[:,1]+=half*dome_lift*bell*.31*np.r_[np.zeros(4),t**2,u[1:]]
            if lean:
                # The crest falls toward one side of the poll. A small
                # lateral roll covers the root of the rear ear without a
                # tall hump in the side profile. Both side bevels stay put.
                across=1-u[1:]**2
                roll=np.r_[np.zeros(26),across**1.45]
                if half==1 and len(design)>12:
                    far_roll=design[12]
                    roll=np.r_[np.zeros(4),far_roll*t**2,far_roll+(1-far_roll)*across]
                    if len(design)>13:
                        # Turn the far cheek of the crest back down into
                        # the ear root as it broadens. This maintains the
                        # actual dome in side profile and its fixed outline.
                        dst[:,2]-=design[13]*bell*np.r_[np.zeros(4),t**2,u[1:]**1.7]
                dst[:,1]+=lean*bell*roll
            # A real downward/forward run into the forehead keeps the line
            # from ending against the side of the brow in a hard point.
            rim=np.sin(np.linspace(0,np.pi*.52,33))**1.4
            dst[:,0]+=insert*tip*(.38+.62*rim)
            dst[:,2]-=.30*turn*tip*rim
            if bevel:
                # Give the cut a real chamfer with tightly supported ends.
                # The section has its own finite width under a glancing light.
                q=dst[25].copy()
                width=bevel*(.76+.24*bell)
                q[2]+=[0.,.035,.004,.003,0.,0.,0.,0.][i]
                for k,f in zip(range(23,28),[.54,.48,0.,-.48,-.54]):
                    dst[k]=q
                    dst[k,1]+=half*width*f
                    dst[k,[0,2]]-=design[11]*width*f*axis
            out[i,indices]=rows+weight*(dst-rows)
    difference=posed(out.reshape(-1,3),*p)-posed(c.reshape(-1,3),*p)
    local=np.empty((len(source),3),np.float32)
    obj.data.vertices.foreach_get('co',local.ravel())
    local+=difference@np.linalg.inv(np.asarray(obj.matrix_world)[:3,:3]).T
    obj.data.vertices.foreach_set('co',local.ravel())
    obj.data.update()
    bpy.context.view_layer.update()
    return {'parent_sha256':PARENT,'shape':dict(zip(('dome_edge_slope','edge_width_factor','side_face_fall','poll_drop','poll_insertion','poll_width_addition','medial_lift','edge_lift_ratio','crown_roll','arched_tip','chamfer_width','chamfer_radial_slope','far_edge_roll','far_edge_fall'),design)),
            'cage_vertices_changed':int((np.linalg.norm(difference,axis=1)>1e-6).sum()),
            'max_displacement':float(np.linalg.norm(difference,axis=1).max()),
            'maximum_lower_six_ring_shift':float(abs(difference.reshape(13,64,3)[7:]).max())}

def border(scene,coords):
    a,b,c,d=coords
    scene.render.use_border=scene.render.use_crop_to_border=True
    scene.render.border_min_x=(a+.05)/1254
    scene.render.border_max_x=(c+.05)/1254
    scene.render.border_min_y=(1254-d+.05)/1254
    scene.render.border_max_y=(1254-b+.05)/1254

def preview(indices):
    for i in indices:
        sc=load('parent.blend')
        if i>=0:sculpt(sc,DESIGNS[i])
        label='parent' if i<0 else f'trial-{i}'
        configure_render(sc,72)
        border(sc,(245,281,524,434))
        render(sc,OUT/f'{label}-crest.png')
        flat(sc)
        render(sc,OUT/f'{label}-clay-crest.png')
        use_side_camera(sc)
        border(sc,(220,92,819,410))
        sc.render.resolution_percentage=70
        render(sc,OUT/f'{label}-clay-side.png')

def build(index):
    scene=load('parent.blend')
    data=sculpt(scene,DESIGNS[index])
    data['design_index']=index
    if index>=16:
        from poll_card import fitted,meter
        data['existing_poll_card']=fitted(scene,meter(scene),0.,105. if index>=20 else 62.,.105)
    scene['knight_improvement_009_B']=json.dumps(data)
    configure_render(scene,144)
    save_model(scene,OUT/'knight.blend')
    data['model_sha256']=sha(OUT/'knight.blend')
    json_file(OUT/'parameters.json',data)

if __name__=='__main__':
    assert sha(OUT/'parent.blend')==PARENT
    if '--tests' in sys.argv:preview(range(-1,4))
    if '--tests2' in sys.argv:preview(range(4,7))
    if '--tests3' in sys.argv:preview(range(7,10))
    if '--build' in sys.argv:build(int(sys.argv[sys.argv.index('--build')+1]))
    if '--studio' in sys.argv:studio()
    if '--parent-flat' in sys.argv:flat_views('parent.blend','parent-')
    if '--orbit' in sys.argv:
        flat_views('knight.blend','')
        scene=load('knight.blend')
        configure_render(scene,32)
        diagnostics(scene,'',True)

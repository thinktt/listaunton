"""Redraw the anterior chest arcs as longitudinally scaled horizontal sections."""
from pathlib import Path
import json
import sys
import bpy
import numpy as np
from mathutils.bvhtree import BVHTree
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(ROOT/'scripts/knight')]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,json_file,render,save_model,sha,world_vertices
from refine_eye import apply_world
from evidence import flat,flat_views,load,studio
from diagnostics import camera,diagnostics

PARENT='8d984d59beea0f86d69bbb5b8f5dc57becf7e707e576412eb8eda4503e81a948'
# Collar and upper-chest displacements at x1.24, hinge and hinge blend width.
# Moving the hinge forwards carries less of the chest accents along with the cut.
DESIGNS=[(.065,.163,-1.05,.47,1.),(.087,.194,-.76,.46,1.),
         (.093,.211,-.53,.51,1.),(.079,.187,-.92,.46,1.),
         (.083,.257,-.31,.33,1.65),(.087,.312,-.36,.33,2.2),(.087,.344,-.35,.33,2.65),
         (.086,.425,-.35,.33,2.65),(.082,.515,-.33,.32,3.35),(.083,.565,-.12,.26,3.15),
         (.086,.345,-.35,.33,2.65,.087),(.083,.371,-.28,.30,2.95,.11)]
ANCHORED=[(.066,.163,-.55,.35,2.0),(.067,.174,-.47,.34,2.8),
          (.075,.194,-.38,.33,3.4),(.067,.182,-.27,.30,3.8),
          (.068,.230,-.44,.30,2.1),(.067,.256,-.41,.30,2.65),(.068,.263,-.53,.32,3.2)]
DESIGNS+=ANCHORED

def smooth(x):
    t=np.clip(x,0,1)
    return t*t*(3-2*t)

def ramp(x,width):
    # Integral of smoothstep. First derivative rises to one then remains there.
    s=np.clip(x/width,0,1)
    return width*(s**3-.5*s**4)+np.maximum(x-width,0)

def shape(rest,design,guide=None):
    low,high,hinge,width,power,*extra=design
    x,y,z=rest.T
    # The complete anterior section uses one x transform. Both lateral
    # bevels therefore follow the same surface as the center of the breast.
    # A positive power increases the cut towards the sternum and carries the
    # side ornament by a smaller amount. The anterior map stays increasing
    # and concave, preserving convex input arcs at every constant height.
    if guide is not None:
        # Measure anterior distance relative to each parent horizontal
        # section. At its sagittal crown the displacement is a simple linear
        # function of height, so the old round belly keeps its curvature.
        gz,gx=guide.T
        front=np.interp(z,gz,gx)
        denom=np.maximum(ramp(front-hinge,width),.15)
        normalized=ramp(x-hinge,width)/denom
        fraction=np.minimum(normalized,1.)**power+power*np.maximum(normalized-1.,0.)
        offset=(low+(high-low)*(z-1.69)/1.04)*smooth((3.36-z)/.48)
        out=rest.copy()
        out[:,0]-=offset*fraction
        return out
    fraction=(ramp(x-hinge,width)/ramp(1.24-hinge,width))**power
    # Carry some recession all the way into the collar. The transition to
    # the deeper cut begins at the height of the old broadest chest ring.
    offset=low+(high-low)*smooth((z-1.89)/.84)
    if extra:
        # Additional throat clearance dissipates before the low return.
        offset+=extra[0]*np.exp(-((z-2.71)/.26)**2)
    offset*=smooth((3.36-z)/.49)
    out=rest.copy()
    out[:,0]-=offset*fraction
    return out

def pose(scene):
    cfg=json.loads(scene['knight_mission_pose'])
    return [cfg[k] for k in ('dx','dy','twist_degrees')]

def modify(scene,design):
    p=pose(scene)
    guide=np.array(json.loads((OUT/'section-guide.json').read_text())['sagittal_zx']) if design in ANCHORED else None
    metrics={}
    for name in ('continuous horse head and neck','curved neck and chest'):
        obj=bpy.data.objects['Knight | '+name]
        w=world_vertices(obj)
        r=rest_coords(w,p)
        dst=shape(r,design,guide)
        change=posed(dst,*p)-posed(r,*p)
        apply_world(obj,w+change)
        length=np.linalg.norm(change,axis=1)
        offset=np.array([.0008,0,0])
        derivative=(shape(r+offset,design,guide)[:,0]-shape(r-offset,design,guide)[:,0])/(2*offset[0])
        metrics[name]={'changed_vertices':int((length>.00001).sum()),'largest_displacement':float(length.max()),
             'minimum_anterior_derivative':float(derivative.min()),'sagittal_profile_anchored':guide is not None,
             'max_above_3_36':float(length[r[:,2]>=3.36].max()),'max_lateral_displacement_in_rest':float(abs((r-dst)[:,1]).max())}
    bpy.context.view_layer.update()
    return {'parent_sha256':PARENT,'design':dict(zip(('collar_recession','chest_recession','posterior_hinge_x','hinge_blend_width','anterior_power','upper_chest_extra_recession'),design)),
            'components':metrics}

def tree(scene,name='continuous horse head and neck'):
    obj=scene.objects['Knight | '+name]
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=ev.to_mesh()
    try:
        v=np.zeros((len(mesh.vertices),3),np.float32)
        mesh.vertices.foreach_get('co',v.ravel())
        m=np.asarray(ev.matrix_world)
        xyz=rest_coords(v@m[:3,:3].T+m[:3,3],pose(scene))
        mesh.calc_loop_triangles()
        face=np.empty((len(mesh.loop_triangles),3),np.int32)
        mesh.loop_triangles.foreach_get('vertices',face.ravel())
        return BVHTree.FromPolygons(xyz.tolist(),face.tolist(),all_triangles=True)
    finally:
        ev.to_mesh_clear()

def sections(scene,tag):
    mesh=tree(scene)
    def probe(y,z):
        hit=mesh.ray_cast((4,y,z),(-1,0,0),7)[0]
        return round(float(hit.x),6) if hit and hit.x>-.45 else None
    sections={}
    for z in (1.92,2.12,2.36,2.58,2.84):
        rows=[]
        for y in np.arange(-.85,.851,.01):
            x=probe(float(y),z)
            if x is not None:rows.append([round(float(y),2),x])
        sections[f'{z:.2f}']=rows
    center=[]
    for z in np.arange(1.64,3.061,.01):
        x=probe(0,float(z))
        if x is not None:center.append([round(float(z),2),x])
    collar=tree(scene,'turned pedestal')
    overlaps=[]
    for z in np.arange(1.62,1.733,.002):
        breast=probe(0,z)
        rim=collar.ray_cast((4,0,z),(-1,0,0),7)[0]
        if breast is not None and rim:overlaps.append([round(float(z),3),breast,round(float(rim.x),6)])
    data={'source':tag,'source_sha256':sha(OUT/'knight.blend') if tag=='B' else PARENT,
          'midline_collar_section_z_breast_x_collar_x':overlaps,
          'horizontal':sections,'center':center}
    json_file(OUT/f'chest-{tag}.json',data)

def guide_from_parent():
    scene=load('parent.blend')
    mesh=tree(scene)
    z=np.arange(1.616,3.112,.009)
    points=[]
    for h in z:
        hit=mesh.ray_cast((4,0,float(h)),(-1,0,0),7)[0]
        if hit is not None:points.append((h,float(hit.x)))
    raw=np.asarray(points)
    low=raw[(raw[:,0]>1.64)&(raw[:,0]<1.70)]
    slope,intercept=np.polyfit(low[:,0],low[:,1],1)
    raw[raw[:,0]<1.64,1]=slope*raw[raw[:,0]<1.64,0]+intercept
    # The upper trunk is briefly hidden behind the muzzle in a +X ray.
    # Continue the final measured tangent as the deformation fades to zero.
    sub=raw[raw[:,0]>3.01]
    slope=np.polyfit(sub[:,0],sub[:,1],1)[0]
    ext=np.arange(raw[-1,0]+.009,3.51,.009)
    line=np.vstack((raw,np.column_stack((ext,raw[-1,1]+(ext-raw[-1,0])*slope))))
    json_file(OUT/'section-guide.json',{'parent_sha256':PARENT,'sagittal_zx':line.tolist()})

def crop(scene,box):
    scene.render.use_border=True
    scene.render.use_crop_to_border=True
    a,b,c,d=box
    scene.render.border_min_x=(a+.05)/1254
    scene.render.border_max_x=(c+.05)/1254
    scene.render.border_min_y=(1254-d+.05)/1254
    scene.render.border_max_y=(1254-b+.05)/1254

def quick_clay(scene,tag):
    configure_render(scene,36)
    flat(scene)
    scene.render.resolution_x=scene.render.resolution_y=640
    yaw=pose(scene)[2]
    for name,angle in [('near',0),('far',180)]:
        camera(scene,yaw+angle,8)
        render(scene,OUT/f'{tag}-clay-{name}.png')

def tests(group=0):
    for index in [range(-1,4),range(4,7),range(7,10),range(10,12),range(12,16),range(16,len(DESIGNS))][group]:
        scene=load('parent.blend')
        tag=f'trial-{index}' if index>=0 else 'parent'
        if index>=0:modify(scene,DESIGNS[index])
        sections(scene,tag)
        if index>=0:
            configure_render(scene,72)
            crop(scene,(290,530,725,765))
            render(scene,OUT/f'{tag}-chest.png')
            scene.render.use_border=False
            scene.render.use_crop_to_border=False
        quick_clay(scene,tag)

def build(index):
    scene=load('parent.blend')
    data=modify(scene,DESIGNS[index])
    data['selected_cross_section_study']=index
    scene['knight_improvement_008_B']=json.dumps(data)
    configure_render(scene,144)
    save_model(scene,OUT/'knight.blend')
    data['model_sha256']=sha(OUT/'knight.blend')
    json_file(OUT/'parameters.json',data)
    scene=load('knight.blend')
    sections(scene,'B')

if __name__=='__main__':
    assert sha(OUT/'parent.blend')==PARENT
    if '--tests' in sys.argv:tests()
    if '--front-tests' in sys.argv:tests(1)
    if '--upper-tests' in sys.argv:tests(2)
    if '--throat-tests' in sys.argv:tests(3)
    if '--guide' in sys.argv:guide_from_parent()
    if '--anchored-tests' in sys.argv:tests(4)
    if '--round-tests' in sys.argv:tests(5)
    if '--parent-sections' in sys.argv:sections(load('parent.blend'),'parent')
    if '--parent-flat' in sys.argv:
        flat_views('parent.blend','parent-')
        sc=load('parent.blend')
        sections(sc,'parent')
        quick_clay(sc,'parent')
    if '--build' in sys.argv:build(int(sys.argv[sys.argv.index('--build')+1]))
    if '--studio' in sys.argv:studio()
    if '--orbit' in sys.argv:
        flat_views('knight.blend','')
        quick_clay(load('knight.blend'),'B')
        scene=load('knight.blend')
        configure_render(scene,32)
        diagnostics(scene,'',True)

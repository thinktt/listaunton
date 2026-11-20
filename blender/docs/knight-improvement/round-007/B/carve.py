"""Re-cut the breast plane on the accepted round-six-A geometry."""
from pathlib import Path
import json
import sys
import bpy
import numpy as np

sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(ROOT/'scripts/knight')]
from evidence import load,flat_views,studio
from diagnostics import diagnostics
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,json_file,render,save_model,sha,world_vertices
from refine_eye import apply_world

PARENT="1837b02f0c472044a8e86ffd112d15dbe007eb70d9a4330d86f8f073b7440208"
DESIGNS=[
    (.157,0.,.18,+.000),   # Earlier upper-chest cut applied to the new parent.
    (.165,.064,.30,+.012),
    (.168,.086,.39,+.005),
    (.172,.079,.345,+.036),
    (.190,.109,.245,-.084),
    (.194,.113,.245,-.104),
    (.189,.113,.280,-.086),
    (.173,.098,.124,-.073),
    (.187,.108,.151,-.069),
    (.174,.107,.158,-.081),
    (.177,.105,.33,+.032),
    (.186,.109,.30,+.018),
    (.190,.110,.29,+.011),
    (.188,.106,.249,-.034),
    (.181,.103,.217,-.047),
]

def ease(t):
    t=np.clip(t,0,1)
    return t*t*(3-2*t)

def chest(rest,design):
    extent,deep,width,offset=design
    x,y,z=rest.T
    anterior=ease((x+.13)/.77)*ease((1.75-x)/.36)
    cap=extent*ease((z-1.80)/.95)*ease((3.36-z)/.47)
    # Return the underside to the accepted seat with zero first derivative.
    # Above this the added return gives the lower breast a continuous convex arc.
    belly=deep*np.exp(-.5*((z-2.25)/.29)**2)*ease((z-1.74)/.33)*ease((3.11-z)/.32)
    # Move the sternum under its intact lateral ridges. A broad transition
    # avoids concentrating a specular highlight where the shoulder cut ends.
    limit=.635-.245*(z-2.75)+offset
    if offset==-.081:
        limit+=.057*ease((z-2.48)/.28)
    medial=ease((limit-np.abs(y))/width)
    if offset<-.095:
        # The flanks retain the native carved surface out to the end of the
        # reflection. Carry the front retreat at the point of the sternum.
        front=ease((x-(.906-.65*(z-2.45)))/.22)
        medial=medial+(1-medial)*front
    w=anterior*medial
    result=rest.copy()
    result[:,0]-=(cap+belly)*w
    base_weight=cap*w/extent
    result[:,1]-=.028*base_weight*y
    result[:,2]-=.017*base_weight
    tangent={.032:.63,.018:.80,.011:.53,-.034:.43,-.047:.30}.get(offset,0.)
    if tangent:
        # The flank normal turns increasingly lateral round the breast.
        # Slide the cut with that plane to avoid a different surface angle
        # interrupting the reflection at the small end of the second bevel.
        angle_weight=ease((np.abs(y)-.49)/.13) if offset<0 else ease((np.abs(y)-.30)/.29)
        result[:,1]+=np.sign(y)*tangent*(cap+belly)*w*angle_weight
    return result

def modify(scene,design):
    pose0=json.loads(scene['knight_mission_pose'])
    pose=[pose0[k] for k in ('dx','dy','twist_degrees')]
    measurements={}
    for name in ['continuous horse head and neck','curved neck and chest']:
        obj=bpy.data.objects['Knight | '+name]
        world=world_vertices(obj)
        rest=rest_coords(world,pose)
        dst=chest(rest,design)
        moved=posed(dst,*pose)-posed(rest,*pose)
        apply_world(obj,world+moved)
        dist=np.linalg.norm(moved,axis=1)
        measurements[name]={'changed_vertices_over_1e-5':int(np.count_nonzero(dist>1e-5)),
             'max_displacement':float(dist.max()),
             'max_above_z_3_36':float(dist[rest[:,2]>=3.36].max()),
             'max_below_z_1_74':float(dist[rest[:,2]<=1.74].max())}
    bpy.context.view_layer.update()
    return {'parent_sha256':PARENT,'design':dict(zip(['upper_recession','lower_recession','flank_transition_width','flank_transition_shift'],design)),
            'components':measurements}

def crop(scene,box):
    x0,y0,x1,y1=box
    scene.render.use_border=True
    scene.render.use_crop_to_border=True
    scene.render.border_min_x=(x0+.05)/1254
    scene.render.border_max_x=(x1+.05)/1254
    scene.render.border_min_y=(1254-y1+.05)/1254
    scene.render.border_max_y=(1254-y0+.05)/1254

def experiments(group=0):
    for index in [range(4),range(4,7),range(7,10),range(10,13),range(13,len(DESIGNS))][group]:
        design=DESIGNS[index]
        scene=load('parent.blend')
        data=modify(scene,design)
        configure_render(scene,80)
        crop(scene,(290,530,725,765))
        render(scene,OUT/f'accents-{index}.png')
        json_file(OUT/f'design-{index}.json',data)

def build(index,eye):
    from eyelid import fit
    scene=load('parent.blend')
    params=modify(scene,DESIGNS[index])
    params['lower_eyelid_reflection']=fit(scene,eye)
    params['selected_eye_study']=eye
    scene['knight_improvement_007_B']=json.dumps(params)
    configure_render(scene,144)
    save_model(scene,OUT/'knight.blend')
    params['model_sha256']=sha(OUT/'knight.blend')
    json_file(OUT/'parameters.json',params)

if __name__=='__main__':
    assert sha(OUT/'parent.blend')==PARENT
    if '--experiments' in sys.argv: experiments()
    if '--flank-tests' in sys.argv: experiments(1)
    if '--facet-tests' in sys.argv: experiments(2)
    if '--tangent-tests' in sys.argv: experiments(3)
    if '--transition-tests' in sys.argv: experiments(4)
    if '--parent-flat' in sys.argv: flat_views('parent.blend','parent-')
    if '--build' in sys.argv:
        index=sys.argv.index('--build')
        build(*map(int,sys.argv[index+1:index+3]))
    if '--studio' in sys.argv: studio()
    if '--orbit' in sys.argv:
        flat_views('knight.blend','')
        scene=load('knight.blend')
        configure_render(scene,32)
        diagnostics(scene,'',True)

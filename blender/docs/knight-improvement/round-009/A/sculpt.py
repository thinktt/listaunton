"""Carve a folded lower lid and cheek plane, and install the UV-mapped walnut."""
from pathlib import Path
import sys,json
import bpy
import numpy as np
D=Path(__file__).resolve().parent;ROOT=D.parents[2];sys.dont_write_bytecode=True
sys.path[:0]=[str(D),str(ROOT/'scripts/knight')]
from surface import chart,ease,bell,margins,relief,skirt,orbit_shape,AXIS,UP
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,save_model,render,json_file,sha,use_side_camera,world_vertices
from diagnostic_views import pictures,clay_studio
from lid_card import focus

PARENT='53ca17473c08fc898e6c29bd5189e4188b3573e003719362cabb102ab621f757'
def apply_y(obj,pose,rest,dist,warp,extension):
    updated=rest.copy();updated[:,1]+=np.sign(rest[:,1])*dist
    updated[:,0]+=warp*UP[0]+extension*AXIS[0];updated[:,2]+=warp*UP[1]+extension*AXIS[1]
    d=posed(updated,*pose)-posed(rest,*pose)
    mat=np.asarray(obj.matrix_world)
    native=np.empty((len(rest),3),np.float32);obj.data.vertices.foreach_get('co',native.ravel())
    native+=(d@np.linalg.inv(mat[:3,:3]).T).astype(np.float32)
    obj.data.vertices.foreach_set('co',native.ravel());obj.data.update()

def carve(obj,pose,eye=False):
    rest=rest_coords(world_vertices(obj),pose);u,v=chart(rest)
    dist=relief(rest,eye)
    top,lower=margins(u)
    extension,warp=orbit_shape(rest)
    if not eye:warp+=skirt(rest)
    apply_y(obj,pose,rest,dist,warp,extension)
    attr=obj.data.attributes.get('Knight varnish coverage')
    if attr is not None:
        old=np.array([p.value for p in attr.data])
        if eye:
            coverage=old*(1-.12*bell(u+.017,.197)*bell(v+.004,.059))
            coverage+=(1-coverage)*.20*bell(u+.015,.144)*bell(v+.022,.032)
        else:
            # The heart of the nonuniform chamfer is burnished, and the flank
            # leading out towards either corner carries a softer surface.
            flank=ease((abs(rest[:,1])-.12)/.16)
            h=v-lower
            seat=flank*ease((.33-abs(u))/.082)*np.exp(-((h+.032)/.083)**4)
            nose=ease((u-.11)/.12)*bell(v+.047,.080)*ease((.38-abs(u))/.09)*flank
            coverage=old*(1-.97*seat)*(1-.79*nose)
            finish=bell(u-.020,.084)*bell(h+.024,.028)
            coverage+=(1-coverage)*.55*finish*flank
        attr.data.foreach_set('value',np.asarray(coverage,np.float32));obj.data.update()
    return {'changed_vertices_1e-5':int((np.hypot(np.hypot(dist,warp),extension)>1e-5).sum()),
            'rest_depth_extremes':[float(dist.min()),float(dist.max())],
            'normal_to_axis_extremes':[float(warp.min()),float(warp.max())],
            'along_axis_extremes':[float(extension.min()),float(extension.max())]}

def texture():
    target=bpy.data.objects['Knight | continuous horse head and neck'].active_material
    node=target.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node
    old=node.image
    assert bytes(old.packed_file.data)==(D/'source-atlas.png').read_bytes()
    image=bpy.data.images.load(str(D/'pigment.png'),check_existing=False)
    image.name='Knight walnut | figured cheek pigment 008-A';image.colorspace_settings.name='sRGB'
    image.pack();assert bytes(image.packed_file.data)==(D/'pigment.png').read_bytes()
    image.filepath='//../../assets/knight/wood-atlas-improvement-008-A.png'
    for material in bpy.data.materials:
        if not material.node_tree:continue
        for texture_node in material.node_tree.nodes:
            if texture_node.type=='TEX_IMAGE' and texture_node.image==old:texture_node.image=image
    if old.users==0:bpy.data.images.remove(old)
    return sha(D/'pigment.png')
def build():
    assert sha(D/'parent.blend')==PARENT
    bpy.ops.wm.open_mainfile(filepath=str(D/'parent.blend'),load_ui=False);s=bpy.context.scene
    p=json.loads(s['knight_mission_pose']);pose=[p[k] for k in ('dx','dy','twist_degrees')]
    cfg={'parent_sha256':PARENT,'pose':pose,'carvings':{}}
    for name in ['continuous horse head and neck','coherent skull cheek and conical muzzle','near eye','far eye']:
        cfg['carvings'][name]=carve(bpy.data.objects['Knight | '+name],pose,name.endswith('eye'))
    cfg['atlas_sha256']=texture();cfg['release_texture']='wood-atlas-improvement-008-A.png'
    bpy.context.view_layer.update();cfg['lower_lid_card']=focus(s)
    s['knight_atlas_sha256']=cfg['atlas_sha256'];s['knight_improvement_009_A']=json.dumps(cfg)
    configure_render(s,144);save_model(s,D/'knight.blend')
    cfg['model_sha256']=sha(D/'knight.blend');json_file(D/'parameters.json',cfg)
    print('ROUND_9A',cfg['model_sha256'],cfg['atlas_sha256'],flush=True)
def preview():
    bpy.ops.wm.open_mainfile(filepath=str(D/'knight.blend'),load_ui=False);scene=bpy.context.scene
    configure_render(scene,80)
    for camera,box in [('fixed',(342,395,613,561)),('side',(496,215,816,464))]:
        if camera=='side':use_side_camera(scene)
        x,y,a,b=box;scene.render.use_border=scene.render.use_crop_to_border=True
        scene.render.border_min_x=(x+.01)/1254;scene.render.border_max_x=(a+.01)/1254
        scene.render.border_min_y=(1254-b+.01)/1254;scene.render.border_max_y=(1254-y+.01)/1254
        render(scene,D/f'preview-{camera}.png')
    clay_studio(scene,10.3);render(scene,D/'preview-side-clay.png')

if __name__=='__main__':
    if '--render-only' not in sys.argv:build()
    if '--preview' in sys.argv:preview()
    elif '--build-only' not in sys.argv:pictures()

"""Carve a folded lower lid and cheek plane, and install the UV-mapped walnut."""
from pathlib import Path
import sys,json
import bpy
import numpy as np
D=Path(__file__).resolve().parent;ROOT=D.parents[2];sys.dont_write_bytecode=True
sys.path[:0]=[str(D),str(ROOT/'scripts/knight')]
from surface import chart,ease,bell,orbit
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render,save_model,render,json_file,sha,use_side_camera,world_vertices
from diagnostic_views import pictures,clay_studio
from lid_card import focus

PARENT='8d984d59beea0f86d69bbb5b8f5dc57becf7e707e576412eb8eda4503e81a948'
def apply_y(obj,pose,rest,dist):
    updated=rest.copy();updated[:,1]+=np.sign(rest[:,1])*dist
    d=posed(updated,*pose)-posed(rest,*pose)
    mat=np.asarray(obj.matrix_world)
    native=np.empty((len(rest),3),np.float32);obj.data.vertices.foreach_get('co',native.ravel())
    native+=(d@np.linalg.inv(mat[:3,:3]).T).astype(np.float32)
    obj.data.vertices.foreach_set('co',native.ravel());obj.data.update()

def carve(obj,pose,eye=False):
    rest=rest_coords(world_vertices(obj),pose);u,v=chart(rest)
    dist,crest,lower=orbit(rest)
    compact=ease((.57-abs(u))/.13)*ease((.41-abs(v+.13))/.11)
    dist*=compact
    if eye:
        # The floor flattens slightly towards the lower shelf while its
        # perimeter and visibility through the canthi are preserved.
        length=bell(u+.018,.191)*ease((.236-abs(u))/.058)
        dist=length*(-.0165-.006*ease((v+.016)/.052)+.015*bell(v+.034,.032))
    apply_y(obj,pose,rest,dist)
    attr=obj.data.attributes.get('Knight varnish coverage')
    if attr is not None:
        old=np.array([p.value for p in attr.data])
        if eye:
            coverage=old*(1-.48*bell(u,.20)*bell(v+.010,.068))
        else:
            flank=ease((abs(rest[:,1])-.12)/.16);length=bell(u+.016,.231)*compact*flank
            through_end=1-ease((abs(u)-.17)/.07)*ease((v+.083)/.046)
            narrow=length*through_end*bell(v-lower+.010,.040)
            cheek=length*through_end*bell(v-crest+.018,.042)
            nose=compact*flank*ease((u-.085)/.112)*bell(v+.038,.078)
            under=flank*ease((.335-abs(u))/.085)*np.exp(-((v-lower+.034)/.086)**4)
            coverage=old*(1-.94*under)*(1-.87*nose)
            center=bell(u-.015,.099)*bell(v-crest-.004,.059)
            coverage+=(1-coverage)*.34*center*flank*(1-.90*nose)
        attr.data.foreach_set('value',np.asarray(coverage,np.float32));obj.data.update()
    return {'changed_vertices_1e-5':int((abs(dist)>1e-5).sum()),'rest_depth_extremes':[float(dist.min()),float(dist.max())]}

def texture():
    target=bpy.data.objects['Knight | continuous horse head and neck'].active_material
    node=target.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node
    old=node.image
    assert bytes(old.packed_file.data)==(D/'source-atlas.png').read_bytes()
    image=bpy.data.images.load(str(D/'pigment.png'),check_existing=False)
    image.name='Knight walnut | figured orbital carving 008-A';image.colorspace_settings.name='sRGB'
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
    s['knight_atlas_sha256']=cfg['atlas_sha256'];s['knight_improvement_008_A']=json.dumps(cfg)
    configure_render(s,144);save_model(s,D/'knight.blend')
    cfg['model_sha256']=sha(D/'knight.blend');json_file(D/'parameters.json',cfg)
    print('ROUND_8A',cfg['model_sha256'],cfg['atlas_sha256'],flush=True)
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

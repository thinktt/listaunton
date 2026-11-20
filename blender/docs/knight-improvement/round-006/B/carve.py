"""Ease the paired canthi and undercut the chest below the jaw in rest coordinates."""
from pathlib import Path
import json
import sys
import bpy
import numpy as np
from mathutils import Vector

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path[:0] = [str(ROOT/'scripts/knight'), str(OUT)]
from lower_carving_fit import rest_coords
from mission_pose import posed
from mission_scene import configure_render, json_file, render, save_model, sha, use_side_camera, visible_meshes, world_vertices
from refine_eye import apply_world
from diagnostics import diagnostics

PARENT = '8a53403942a3e5bea1df92e3f28c9bfd5d80c61a1026a03549f1c21fd4c96cb6'
AXIS = np.array([1., -.76])
AXIS /= np.linalg.norm(AXIS)
UP = np.array([-AXIS[1], AXIS[0]])
CENTER = np.array([.412, 4.158])

def ease(x):
    x = np.clip(x, 0, 1)
    return x*x*(3-2*x)

def bell(x):
    return np.exp(-x*x)

def load(name):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/name), load_ui=False)
    return bpy.context.scene

def eye_axes(rest):
    p = rest[:, [0,2]] - CENTER
    return p@AXIS, p@UP

def cheek(u,v,coefs):
    terms = np.column_stack((np.ones_like(u),u,v,u*u,u*v,v*v,u**3,u*u*v,u*v*v,v**3))
    return terms@coefs

def fair_eye(rest, cheeks, strength):
    # Tangent roll-off through the approaching ends of both lids. The skull
    # continues in one cheek plane beyond them, without a separately punched
    # canthus at either end. Preserve the central upper-lid plane.
    u,v = eye_axes(rest)
    n = u/.267
    dome = np.maximum(0, 1-n*n)
    old_lower = -.105*u+.008*dome-.052*dome*(1+.08*n)
    nasal = ease((u-.045)/.19)
    tail = ease((-u-.080)/.17)
    axis = -.105*u+.008*dome-.008*nasal*bell((u-.203)/.114)
    upper = axis+.067*dome*(1-.16*n)
    lower = axis-.052*dome*(1+.08*n)
    # Counter-curve the lower lip towards the nose, merging it into the cheek.
    lower += .009*bell((u-.142)/.084)-.0036*bell((u+.087)/.096)
    fade = ease((.295-np.abs(u)) / (.143+.027*nasal))
    cavity = ease((upper-v+.004)/.034)*ease((v-lower+.018)/.050)
    arch = .030*bell((v-upper-.009)/.043)+.019*bell((v-upper-.052)/.083)
    rim = .018*bell((v-lower+.014)/.042)+.008*bell((v-lower+.053)/.073)
    floor = -(.060+.012*ease((v-lower)/.095))*cavity
    cut = -.011*bell((v-upper+.020)/.017)
    surface = fade*(arch+rim+floor+cut)
    # The progressive blend relieves both corner depressions while leaving
    # the parent floor, facets and paint intact over the center of the eye.
    corners = np.maximum(nasal, tail)
    rim_weight = .57*bell((u-.010)/.175)*bell((v-old_lower)/.064)
    blend = strength*np.maximum(corners, rim_weight)*ease((.38-abs(u))/.060)*ease((.20-abs(v))/.055)
    output = rest.copy()
    for side,coefs in cheeks.items():
        use = (side*rest[:,1]>.15)&(blend>0)
        desired = cheek(u[use],v[use],coefs)+surface[use]
        output[use,1] += side*blend[use]*(desired-side*rest[use,1])
    return output

def chest(rest, extent, keep_bevels):
    x,y,z = rest.T
    # Wane to zero below the shoulder and over the underside of the muzzle.
    # The broad anterior half of each shoulder moves with the breastbone.
    support = ease((x+.13)/.77)*ease((z-1.80)/.95)*ease((3.36-z)/.47)
    support *= ease((1.75-x)/.36)
    # The diagonally carved ridges lie farther out on the flanks than the
    # front breast. Fade the retreat away there so those facets retain the
    # orientations that pick out both lines under the inherited broad cards.
    lateral_limit = .635-.245*(z-2.75)
    medial = ease((lateral_limit-abs(y))/.18)
    if keep_bevels>1:
        # Alternative transition leading forwards from the bevel in profile.
        # It takes the load over the broad chest panel, away from the crest.
        crest=.387-.75*(z-2.75)
        medial=ease((x-crest-.035)/.29)
        keep_bevels=1.
    support *= 1.-keep_bevels*(1.-medial)
    out = rest.copy()
    out[:,0] -= extent*support
    out[:,1] -= .028*support*y
    out[:,2] -= .017*support
    return out

def modify(scene, strength=1., extent=.157, keep_bevels=0.):
    pose_dict = json.loads(scene['knight_mission_pose'])
    pose = [pose_dict[k] for k in ('dx','dy','twist_degrees')]
    cheeks = {int(k):np.asarray(v) for k,v in json.loads(scene['knight_improvement_005_A'])['cheek_polynomial'].items()}
    parts = {}
    for name,do_eye,do_chest in [
        ('continuous horse head and neck',True,True),('coherent skull cheek and conical muzzle',True,False),
        ('curved neck and chest',False,True)]:
        obj = bpy.data.objects['Knight | '+name]
        w = world_vertices(obj)
        old = rest_coords(w,pose)
        out = fair_eye(old,cheeks,strength) if do_eye else old.copy()
        out = chest(out,extent,keep_bevels) if do_chest else out
        move = posed(out,*pose)-posed(old,*pose)
        moved = np.linalg.norm(move,axis=1)
        apply_world(obj,w+move)
        parts[name] = {'vertices_changed_over_1e-5':int(np.sum(moved>1.e-5)),
                       'maximum_world_displacement':float(moved.max())}
    bpy.context.view_layer.update()
    return {'parent_sha256':PARENT,'canthus_fairing':strength,'chest_recession':extent,
            'lateral_bevel_preservation':keep_bevels,'parts':parts}

def flat(scene):
    for obj in visible_meshes(scene):
        for slot in obj.material_slots:
            slot.material=bpy.data.materials['Neutral satin clay']
    for obj in scene.objects:
        if obj.type=='LIGHT':
            obj.hide_render=True
    for i,loc in enumerate([(4,5,8),(4,-5,8),(-4,5,8),(-4,-5,8)]):
        lamp=bpy.data.lights.new('Clay bank '+str(i),'AREA')
        lamp.energy=440
        lamp.shape='DISK'
        lamp.size=4.5
        obj=bpy.data.objects.new(lamp.name,lamp)
        scene.collection.objects.link(obj)
        obj.location=loc
        obj.rotation_euler=(Vector((0,0,2.8))-obj.location).to_track_quat('-Z','Y').to_euler()

def flat_views(name,prefix):
    scene=load(name)
    configure_render(scene,40)
    scene.render.resolution_percentage=64
    flat(scene)
    render(scene,OUT/(prefix+'clay-fixed.png'))
    use_side_camera(scene)
    render(scene,OUT/(prefix+'clay-side.png'))

def build(strength,extent,keep_bevels):
    scene=load('parent.blend')
    data=modify(scene,strength,extent,keep_bevels)
    scene['knight_improvement_006_B']=json.dumps(data)
    configure_render(scene,144)
    save_model(scene,OUT/'knight.blend')
    data['model_sha256']=sha(OUT/'knight.blend')
    json_file(OUT/'parameters.json',data)

def studio():
    scene=load('knight.blend')
    configure_render(scene,144)
    render(scene,OUT/'wood.png')
    use_side_camera(scene)
    render(scene,OUT/'wood-side.png')
    data=json.loads((OUT/'parameters.json').read_text())
    data.update({'fixed_sha256':sha(OUT/'wood.png'),'side_sha256':sha(OUT/'wood-side.png'),'samples':144})
    json_file(OUT/'parameters.json',data)

if __name__=='__main__':
    assert sha(OUT/'parent.blend')==PARENT
    if '--build' in sys.argv:
        p=sys.argv.index('--build')
        build(*map(float,sys.argv[p+1:p+4]))
    if '--accents-test' in sys.argv or '--anterior-test' in sys.argv:
        variants = [(3,2.)] if '--anterior-test' in sys.argv else [(0,0.),(1,.55),(2,1.)]
        for i,k in variants:
            scene=load('parent.blend')
            modify(scene,1.,.157,k)
            configure_render(scene,80)
            scene.render.use_border=True
            scene.render.use_crop_to_border=True
            scene.render.border_min_x=(290+.05)/1254
            scene.render.border_max_x=(725+.05)/1254
            scene.render.border_min_y=(1254-765+.05)/1254
            scene.render.border_max_y=(1254-530+.05)/1254
            render(scene,OUT/f'accents-{i}.png')
    if '--studio' in sys.argv: studio()
    if '--parent-flat' in sys.argv: flat_views('parent.blend','parent-')
    if '--orbit' in sys.argv:
        flat_views('knight.blend','')
        scene=load('knight.blend')
        configure_render(scene,32)
        diagnostics(scene,'',True)

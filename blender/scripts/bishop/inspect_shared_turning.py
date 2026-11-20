"""Measure actual turned sections and render level profiles under identical light."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).parent))
from shared_turning import ROOT, CONFIG, BODY, digest, read_source, setup_device


def open_piece(label, spec):
    if label in ('queen', 'king', 'bishop'):
        path = read_source(spec, label)
    else:
        path = ROOT/'build/bishop-mission'/('turning-'+label)/'bishop.blend'
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    scene = bpy.context.scene
    prefix = {'queen':'01 Queen - continuous body', 'king':'King - continuous turned body'}.get(label, BODY)
    body, = [o for o in scene.objects if o.name.startswith(prefix)]
    for m in body.modifiers:
        if m.type=='SUBSURF':
            m.levels = m.render_levels
    bpy.context.view_layer.update()
    return path, scene, body


def measure(scene, body, is_bishop):
    graph = bpy.context.evaluated_depsgraph_get()
    obj = body.evaluated_get(graph)
    tree = BVHTree.FromObject(body, graph)
    # Positive-X exterior on the unaffected meridian, including actual
    # subdivision. Tiny spacing resolves a narrow groove and the socket cap.
    zs = np.arange(.0005, 1.6001, .0005)
    profile = []
    for z in zs:
        location, _, _, _ = tree.ray_cast(Vector((3,0,z)), Vector((-1,0,0)), 3)
        if location is not None:
            profile.append([float(location.x), float(z)])
    profile = np.array(profile)
    foot = 2 * profile[profile[:,1]<.21, 0].max()
    scale = foot / 2.0893
    report = {'foot_diameter':float(foot)}
    for name, greatest in [('groove',False), ('flare',True)]:
        # Old bishop groove is above the donor flare crest. Separate its bands
        # using the actual transition ring in the source cage.
        mesh = body.data
        n = 128 if is_bishop else int(body.get('ring_segments', 96))
        zgroove = mesh.vertices[(10 if is_bishop and len(mesh.vertices)==107*128 else 11)*n].co.z
        zcrest = mesh.vertices[(13 if is_bishop and len(mesh.vertices)==107*128 else 17)*n].co.z
        mid=(zgroove+zcrest)/2
        low,high=(zgroove-.045,mid) if name=='groove' else (mid,zcrest+.07)
        band = profile[(profile[:,1]>=low)&(profile[:,1]<=high)]
        point=band[band[:,0].argmax() if greatest else band[:,0].argmin()]
        report[name]={'radius':float(point[0]), 'height':float(point[1])}
    report['socket_diameter_at_scaled_z1']=float(2*np.interp(scale, profile[:,1],profile[:,0]))
    if is_bishop:
        # Find each physical rim on the evaluated front surface. The camera
        # projects its largest downward excursion over the corresponding band.
        from bpy_extras.object_utils import world_to_camera_view
        shifted = 7 if len(body.data.vertices)==114*128 else 0
        crests = {}
        for name,low,high in [('upper',59,65),('middle',50,57),('lower',41,48)]:
            cage = body.data.vertices
            limits = sorted([cage[(low+shifted)*128].co.z, cage[(high+shifted)*128].co.z])
            pixels=[]
            for z in np.linspace(*limits, 220):
                point,_,_,_=tree.ray_cast(Vector((0,-3,z)),Vector((0,1,0)),3)
                if point is not None:
                    uv=world_to_camera_view(scene,scene.camera,point)
                    pixels.append((1-uv.y)*scene.render.resolution_y)
            crests[name]=max(pixels)
        report['front_collar_rim_rows']=crests
        groove = report['groove']
        groove_uv=world_to_camera_view(scene,scene.camera,Vector((0,-groove['radius'],groove['height'])))
        report['front_groove_row']=(1-groove_uv.y)*scene.render.resolution_y
        zs = []
        for ob in [body, bpy.data.objects['Bishop - domed button finial']]:
            ev = ob.evaluated_get(graph)
            mesh = ev.to_mesh()
            coords=np.empty((len(mesh.vertices),3),np.float32)
            mesh.vertices.foreach_get('co',coords.ravel())
            zs.extend([float(coords[:,2].min()),float(coords[:,2].max())])
            ev.to_mesh_clear()
        report.update(floor=min(zs), height=max(zs)-min(zs))
    return report, profile


def render_level(source_scene, body, is_bishop, out):
    graph = bpy.context.evaluated_depsgraph_get()
    controls=[body]
    if is_bishop:
        controls.append(bpy.data.objects['Bishop - domed button finial'])
    # The donor panels show only the base. Build a neutral scene from evaluated
    # meshes, leaving all authored material, lamp and camera data in the source.
    scene = bpy.data.scenes.new('Level geometry comparison')
    scene.render.engine='CYCLES'
    mat=bpy.data.materials.new('Neutral turned wood study')
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(.48,.48,.48,1)
    bs.inputs['Roughness'].default_value=.50
    for control in controls:
        ev=control.evaluated_get(graph)
        mesh=bpy.data.meshes.new_from_object(ev, depsgraph=graph)
        mesh.materials.clear()
        mesh.materials.append(mat)
        copy=bpy.data.objects.new('Section '+control.name,mesh)
        scene.collection.objects.link(copy)
        copy.matrix_world=control.matrix_world.copy()
    world=bpy.data.worlds.new('Neutral studio')
    world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
    scene.world=world
    for name,loc,power,size in [('Key',(-3,-5,6),760,4),('Fill',(4,-2,3),340,3)]:
        lamp=bpy.data.lights.new(name,'AREA')
        lamp.energy=power
        lamp.shape='DISK'
        lamp.size=size
        obj=bpy.data.objects.new(name,lamp)
        scene.collection.objects.link(obj)
        obj.location=loc
        obj.rotation_euler=(Vector((0,0,1.4))-obj.location).to_track_quat('-Z','Y').to_euler()
    cam=bpy.data.cameras.new('Level camera')
    camera=bpy.data.objects.new('Level camera',cam)
    scene.collection.objects.link(camera)
    scene.camera=camera
    cam.type='ORTHO'
    cam.ortho_scale=4.9
    camera.location=(0,-10,2.3)
    camera.rotation_euler=(math.pi/2,0,0)
    scene.render.resolution_x=600
    scene.render.resolution_y=1000
    scene.render.resolution_percentage=100
    scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGBA'
    scene.view_settings.view_transform='AgX'
    scene.cycles.samples=24
    scene.cycles.use_denoising=True
    setup_device(scene)
    scene.render.filepath=str(out/'level.png')
    bpy.ops.render.render(write_still=True,scene=scene.name)
    return {'elevation_degrees':0,'width':600,'height':1000,'pixels_per_unit':1000/4.9,'z_target':2.3,
            'floor_row':500+2.3*1000/4.9,'ortho_scale':4.9}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pieces',nargs='+')
    p.add_argument('--config',default=CONFIG)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    spec=json.loads((ROOT/args.config).read_text())
    for label in args.pieces:
        path,scene,body=open_piece(label,spec)
        is_bishop=label not in ('queen','king')
        out=ROOT/'build/bishop-mission/turning-sections'/label
        out.mkdir(parents=True,exist_ok=True)
        report, profile=measure(scene,body,is_bishop)
        np.save(out/'meridian.npy',profile)
        report.update(source_sha256=digest(path), side=render_level(scene,body,is_bishop,out))
        (out/'measures.json').write_text(json.dumps(report,indent=2)+'\n')
        print('TURNING_SECTION_COMPLETE',label,report['foot_diameter'],flush=True)

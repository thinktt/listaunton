"""Test two real, shadowed reflection lights on the finial/bowl contact curve."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from queen_scene import editable_mesh
from render_regions import link
p=argparse.ArgumentParser();p.add_argument('config',type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
config=json.loads(a.config.read_text(encoding='utf-8'));source=ROOT/config['source'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
capture=ROOT/config['capture'];manifest=json.loads((capture/'manifest.json').read_text())
positions=np.load(capture/'position.npy');normals=np.load(capture/'normal.npy');x1,y1,x2,y2=manifest['crop']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.context.scene;o=editable_mesh(s);settings=json.loads(s['mission_material_config'])
assert manifest['source_sha256'] in (digest,settings.get('finial_reflector_aim',{}).get('source_sha256'))
view=(s.camera.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
levels=[(m,m.levels) for m in o.modifiers if m.type=='SUBSURF']
for m,_ in levels:m.levels=m.render_levels
bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();mesh.calc_loop_triangles()
tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in mesh.vertices],[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
ev.to_mesh_clear()
for m,level in levels:m.levels=level
parts=[part for part in s.objects if part.get('mission_render_region') in ['finial','turned-body']]
records=[]
for item in config['lights']:
    x,y=item['pixel'];ix,iy=x-x1,y-y1;position=Vector(positions[iy,ix,:3]);assert positions[iy,ix,3]>.999
    near=[]
    for yy in range(iy-1,iy+2):
        for xx in range(ix-1,ix+2):
            if positions[yy,xx,3]>.999 and np.linalg.norm(positions[yy,xx,:3]-np.asarray(position))<.025:near.append(normals[yy,xx,:3])
    normal=Vector(np.mean(near,axis=0)).normalized();direction=(2*normal.dot(view)*normal-view).normalized()
    distance=6.;location=position+distance*direction
    hit=tree.ray_cast(position+direction*.001,direction,distance-.001)
    light_data=bpy.data.lights.new(item['name'],'SPOT');light_data.energy=item['energy'];light_data.color=(1,.7,.5)
    light_data.shadow_soft_size=item['radius'];light_data.spot_size=math.radians(item['cone']);light_data.spot_blend=.9;light_data.use_shadow=True
    lamp=bpy.data.objects.new(item['name'],light_data);s.collection.objects.link(lamp)
    lamp.location=location;lamp.rotation_euler=(position-location).to_track_quat('-Z','Y').to_euler()
    lamp.visible_diffuse=False;lamp.visible_glossy=True;link(lamp,parts,'finial-contact')
    spec={'name':lamp.name,'type':'SPOT','energy':light_data.energy,'color':list(light_data.color),'position':list(location),'target':list(position),
          'target_pixel':[x,y],'size':item['radius']*2,'shadow_soft_size':item['radius'],'spot_degrees':item['cone'],'spot_blend':.9,
          'rotation_euler':list(lamp.rotation_euler),'diffuse_factor':0,'receiver_parts':['finial','turned-body'],'use_shadow':True}
    settings['lights'].append(spec)
    records.append({'spec':spec,'normal':list(normal),'center_ray_blocked':hit[0] is not None,'block_distance':hit[3]})
settings['variant']=config['variant'];settings['contact_reflection_study']={'source_sha256':digest,'capture':config['capture'],'capture_sha256':manifest['source_sha256'],'config':config,'lights':records,'shadows_enabled':True}
s['mission_material_config']=json.dumps(settings);s['mission_variant']=config['variant']
out=ROOT/'build/queen-mission'/config['variant'];out.mkdir(parents=True,exist_ok=True)
s.render.use_border=False;s.render.use_crop_to_border=False;s.cycles.samples=256;s.cycles.use_adaptive_sampling=False;s.cycles.use_light_tree=False;s.cycles.use_denoising=True;s.render.use_persistent_data=True
s.render.filepath=str(out/'wood.png');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'queen.blend'),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(out/'queen.blend'),load_ui=False);s=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
if any(device.use for device in prefs.devices):s.cycles.device='GPU'
bpy.ops.render.render(write_still=True)
(out/'parameters.json').write_text(json.dumps(settings,indent=2)+'\n',encoding='utf-8');print('CONTACT_REFLECTION_TRIAL',json.dumps(records),flush=True)

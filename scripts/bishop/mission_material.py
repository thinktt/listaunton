"""Reproducible bishop pigment/lighting trial; never overwrite accepted assets.

The image supplies inferred pigment only. Visibility-weighted projection blends
into continuous object-space wood on unseen surfaces. Output is a real BSDF.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('config');p.add_argument('--no-render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
cfg=json.loads(Path(a.config).read_text());source=ROOT/cfg['source']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene;objects=[o for o in scene.objects if o.type=='MESH' and not o.hide_render]
assert len(objects)==2
camera_before=[float(x) for row in scene.camera.matrix_world for x in row]
view=scene.camera.matrix_world.to_3x3()@Vector((0,0,1));view.normalize()
bpy.context.view_layer.update();graph=bpy.context.evaluated_depsgraph_get()
trees=[BVHTree.FromObject(o,graph) for o in objects]
coverage_stats={}
for ob in objects:
    uv=ob.data.uv_layers.get('Pigment projection') or ob.data.uv_layers.new(name='Pigment projection')
    weights=[];coords=[]
    for v in ob.data.vertices:
        co=ob.matrix_world@v.co;screen=world_to_camera_view(scene,scene.camera,co);coords.append((screen.x,screen.y))
        nearest=100
        for tree in trees:
            loc,normal,face,distance=tree.ray_cast(co+view*12,-view,24)
            if loc is not None:nearest=min(nearest,distance)
        facing=max(0,min(1,(v.normal.dot(view)-.06)/.38))
        weights.append(facing if abs(nearest-12)<.065 else 0)
    for loop in ob.data.loops:uv.data[loop.index].uv=coords[loop.vertex_index]
    att=ob.data.attributes.get('Pigment coverage') or ob.data.attributes.new(name='Pigment coverage',type='FLOAT',domain='POINT')
    att.data.foreach_set('value',weights)
    coverage_stats[ob.name]={'mean':float(np.mean(weights)),'covered_vertices':int(np.count_nonzero(np.array(weights)>.5))}
    # Unfold each original lathe by meridian arc length; reserve two atlas bands.
    co=np.array([tuple(v.co) for v in ob.data.vertices]);rings=co.reshape(-1,128,3)
    r=np.linalg.norm(rings[:,:,:2],axis=2).mean(1);z=rings[:,:,2].mean(1)
    arc=np.r_[0,np.cumsum(np.hypot(np.diff(r),np.diff(z)))];arc/=arc[-1]
    atlas=ob.data.uv_layers.get('Wood atlas') or ob.data.uv_layers.new(name='Wood atlas')
    button='finial' in ob.name;v0,v1=(.73,.88) if button else (.01,.70)
    for face in ob.data.polygons:
        us=[((ob.data.loops[i].vertex_index%128)/128-.25)%1 for i in face.loop_indices]
        seam=max(us)-min(us)>.5
        for li,u in zip(face.loop_indices,us):
            vi=ob.data.loops[li].vertex_index
            if len(face.vertices)>4:
                top=vi//128==len(rings)-1
                center=(.6 if button else .1)+(.25 if top else 0)
                theta=(vi%128)*math.tau/128
                atlas.data[li].uv=(center+.045*math.cos(theta),.94+.045*math.sin(theta))
            else:atlas.data[li].uv=(.01+.98*(u+(1 if seam and u<.5 else 0)),v0+(v1-v0)*arc[vi//128])
    ob.data.uv_layers.active=atlas;atlas.active_render=True

mat=bpy.data.materials.new('Bishop — inferred boxwood pigment and varnish');mat.use_nodes=True
n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear()
def node(t,name):
    o=n.new(t);o.name=name;o.label=name;return o
def connect(a,sa,b,sb):l.new(a.outputs[sa],b.inputs[sb])
coord=node('ShaderNodeTexCoord','Continuous wood coordinates')
stretch=node('ShaderNodeVectorMath','Fine horizontal fibres');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(3,3,44);connect(coord,'Object',stretch,0)
noise=node('ShaderNodeTexNoise','Fine wavy wood');noise.inputs['Scale'].default_value=4;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.65;connect(stretch,0,noise,'Vector')
ramp=node('ShaderNodeValToRGB','Hidden boxwood pigment');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*cfg.get('wood_dark',[.27,.105,.023]),1);ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(*cfg.get('wood_light',[.65,.35,.115]),1);connect(noise,'Fac',ramp,0)
uv=node('ShaderNodeUVMap','Fixed pigment registration');uv.uv_map='Pigment projection'
image=bpy.data.images.load(str(ROOT/cfg['pigment']),check_existing=False);image.pack()
tex=node('ShaderNodeTexImage','Inferred diffuse pigment');tex.image=image;tex.extension='EXTEND';connect(uv,'UV',tex,'Vector')
cover=node('ShaderNodeAttribute','Visible pigment confidence');cover.attribute_name='Pigment coverage'
weight=node('ShaderNodeMath','Pigment weight');weight.operation='MULTIPLY';connect(cover,'Fac',weight,0);connect(tex,'Alpha',weight,1)
grade=node('ShaderNodeHueSaturation','Pigment gain');grade.inputs['Saturation'].default_value=cfg.get('saturation',1);grade.inputs['Value'].default_value=cfg.get('gain',1);connect(tex,'Color',grade,'Color')
mix=node('ShaderNodeMixRGB','Visible and hidden wood');connect(weight,0,mix,0);connect(ramp,'Color',mix,1);connect(grade,'Color',mix,2)
bs=node('ShaderNodeBsdfPrincipled','Principled BSDF');connect(mix,0,bs,'Base Color');bs.inputs['Roughness'].default_value=cfg['roughness'];bs.inputs['IOR'].default_value=1.46;bs.inputs['Coat Weight'].default_value=cfg['coat'];bs.inputs['Coat Roughness'].default_value=cfg['coat_roughness']
gray=node('ShaderNodeRGBToBW','Pigment relief');connect(mix,0,gray,0)
pores=node('ShaderNodeTexNoise','Fine wood pores');pores.inputs['Scale'].default_value=cfg.get('pore_scale',160);pores.inputs['Detail'].default_value=2;connect(coord,'Object',pores,'Vector')
height=node('ShaderNodeMixRGB','Subtle pigment and pores');height.inputs[0].default_value=cfg.get('pore_mix',.18);connect(gray,0,height,1);connect(pores,'Fac',height,2)
bump=node('ShaderNodeBump','Wood micro relief');bump.inputs['Strength'].default_value=cfg['bump_strength'];bump.inputs['Distance'].default_value=cfg['bump_distance'];connect(height,0,bump,'Height');connect(bump,'Normal',bs,'Normal');connect(bump,'Normal',bs,'Coat Normal')
out=node('ShaderNodeOutputMaterial','Material Output');connect(bs,'BSDF',out,'Surface')
for ob in objects:ob.data.materials.clear();ob.data.materials.append(mat)
for ob in list(scene.objects):
    if ob.type=='LIGHT':bpy.data.objects.remove(ob,do_unlink=True)
for spec in cfg['lights']:
    d=bpy.data.lights.new(spec['name'],'AREA');d.energy=spec['energy'];d.shape=spec.get('shape','DISK');d.size=spec['size']
    if d.shape=='RECTANGLE':d.size_y=spec.get('size_y',d.size)
    d.spread=math.radians(spec.get('spread_degrees',180))
    ob=bpy.data.objects.new(spec['name'],d);scene.collection.objects.link(ob);ob.location=spec['position'];ob.rotation_euler=(Vector(spec.get('target',[0,0,2.3]))-ob.location).to_track_quat('-Z','Y').to_euler()
    ob.visible_diffuse=spec.get('diffuse',True);ob.visible_glossy=spec.get('glossy',True)
    if spec.get('receiver'):
        label='Bishop light receiver '+spec['receiver'];collection=bpy.data.collections.get(label) or bpy.data.collections.new(label)
        for receiver in objects:
            selected=('finial' in receiver.name)==(spec['receiver']=='button')
            if selected and receiver.name not in collection.objects:collection.objects.link(receiver)
        ob.light_linking.receiver_collection=collection
scene.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=cfg['world']
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=cfg.get('exposure',0)
scene.render.engine='CYCLES';scene.cycles.samples=cfg.get('samples',32);scene.cycles.use_denoising=True;scene.render.resolution_percentage=cfg.get('resolution_percent',100);scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
scene['bishop_mission_material']=json.dumps(cfg,sort_keys=True);scene['reconstruction']='Actual bishop with inferred diffuse pigment, procedural hidden wood, and physical varnish. Camera fixed at 54 degrees.'
assert camera_before==[float(x) for row in scene.camera.matrix_world for x in row]
outdir=ROOT/'build/bishop-mission'/cfg['variant'];outdir.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(outdir/'wood.png')
cfg['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest();cfg['pigment_sha256']=hashlib.sha256((ROOT/cfg['pigment']).read_bytes()).hexdigest();cfg['coverage']=coverage_stats
(outdir/'parameters.json').write_text(json.dumps(cfg,indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(outdir/'bishop.blend'))
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type=='OPTIX'
    if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as e:print('CPU fallback',e)
if not a.no_render:bpy.ops.render.render(write_still=True)
print('BISHOP_MATERIAL_TRIAL_COMPLETE',cfg['variant'],flush=True)

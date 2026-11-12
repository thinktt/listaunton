"""Fit real rook spot reflectors from surface normals and isolated responses."""
from pathlib import Path
import sys,json,hashlib,math
import bpy,numpy as np,PyOpenColorIO as ocio
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/king'))
from mission_trial import gpu
from focused_reflections import target
source=ROOT/'models/rook/rook-rebuilt.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='9eaaaaadfd2195591508cda798d56c27aa263ee3baa9424ded8acf76d6e4349c'
out=ROOT/'build/rook-mission/005-highlight-fit';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene;gpu(s)
s.cycles.samples=32;s.cycles.use_denoising=False;s.cycles.use_adaptive_sampling=False;s.render.resolution_percentage=50;s.render.use_persistent_data=True
def pixels(im):
    w,h=im.size;a=np.empty(w*h*4,np.float32);im.pixels.foreach_get(a);return a.reshape(h,w,4)[::-1].copy()
ref=bpy.data.images.load(str(ROOT/'assets/rook/ref.png'),check_existing=False);raw=pixels(ref);W,H=ref.size
seeds=[('rim-left-upper',370,310),('rim-left-peak',433,280),('rim-right-peak',543,290),('rim-right-upper',615,337),('rim-right-side',648,440),('rim-front-left',375,515),('rim-front-middle-left',430,545),('rim-front-middle-right',551,536),('rim-front-right',604,504),('notch-front',485,576),('shoulder-left',359,866),('shoulder-middle-left',435,889),('shoulder-middle-right',540,884),('shoulder-right',607,853),('foot-left',338,999),('foot-middle-left',431,1035),('foot-middle-right',550,1027),('foot-right',650,985)]
created=[];probes=[]
for name,x,y in seeds:
    yy,xx=np.mgrid[max(0,y-12):min(H,y+13),max(0,x-12):min(W,x+13)]
    rgb=raw[yy,xx,:3];score=rgb.min(2)*1.5+rgb.mean(2)-.0008*((xx-x)**2+(yy-y)**2)
    idx=np.argmax(score);px=int(xx.flat[idx]);py=int(yy.flat[idx])
    try:ob,point,direction,normal=target(s,px+.5,py+.5)
    except AssertionError:
        ob,point,direction,normal=target(s,x+.5,y+.5);px=x;py=y
    data=bpy.data.lights.new('Rook fit '+name,'SPOT');data.energy=0;data.color=(1,.87,.72);data.shadow_soft_size=.025;data.spot_size=math.radians(7);data.spot_blend=.8
    light=bpy.data.objects.new(data.name,data);s.collection.objects.link(light);light.location=point+direction*4;light.rotation_euler=(point-light.location).to_track_quat('-Z','Y').to_euler();light.visible_diffuse=False;light.visible_glossy=True
    created.append(light);probes.append({'name':light.name,'seed':[x,y],'pixel':[px,py],'point':list(point),'normal':list(normal),'position':list(light.location)})
old_lights=[o for o in s.objects if o.type=='LIGHT' and o not in created];powers={o.name:o.data.energy for o in old_lights}
for ob in old_lights:
    if ob.name.startswith('Rook '):ob.data.energy=0
world=s.world.node_tree.nodes['Background'];worldpower=world.inputs[1].default_value
def capture(name):
    s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(out/(name+'.exr'));bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(s.render.filepath,check_existing=False);a=pixels(im);bpy.data.images.remove(im);return a
fixed=capture('fixed')
for ob in old_lights:ob.data.energy=0
world.inputs[1].default_value=0
responses=[]
for i,light in enumerate(created):
    light.data.energy=5;responses.append(capture('response-%02d'%i)[:,:,:3]);light.data.energy=0
for ob in old_lights:ob.data.energy=0 if ob.name.startswith('Rook ') else powers[ob.name]
world.inputs[1].default_value=worldpower
# Fit in display space through the same AgX transform used by the final render.
rawsmall=(raw[0::2,0::2]+raw[1::2,0::2]+raw[0::2,1::2]+raw[1::2,1::2])*.25
mask=(fixed[:,:,3]>.99)&(rawsmall[:,:,3]>.8)&(rawsmall[:,:,:3].max(2)>.05)
base=fixed[:,:,:3][mask];X=np.stack([a[mask] for a in responses],axis=-1);desired=rawsmall[:,:,:3][mask]
color=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
processor=color.getProcessor(ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display='sRGB',view='AgX')).getDefaultCPUProcessor()
def display(a):
    a=np.ascontiguousarray(a,dtype=np.float32);processor.applyRGB(a);return a
weights=.2+np.clip((desired.min(1)-.16)*4,0,2);gain=np.ones(len(created));history=[]
def loss(g):
    pred=display(base+X@g);return float(np.mean(weights[:,None]*(pred-desired)**2)),pred
for iteration in range(20):
    error,pred=loss(gain);linear=base+X@gain
    J=np.stack([(display(linear+X[:,:,i]*.02)-display(np.maximum(linear-X[:,:,i]*.02,0)))/.04 for i in range(len(created))],axis=-1)
    A=J.reshape(-1,len(created)).astype(float);ww=np.repeat(weights,3);rhs=(desired-pred).reshape(-1)+A@gain
    G=A.T@(A*ww[:,None])+np.eye(len(created))*.0001;b=A.T@(rhs*ww);proposal=gain.copy()
    for step in range(100):
        before=proposal.copy()
        for i in range(len(created)):proposal[i]=np.clip(proposal[i]+(b[i]-G[i]@proposal)/max(G[i,i],1e-10),0,40)
        if max(abs(before-proposal))<1e-6:break
    best=gain;bestloss=error
    for rate in [1,.5,.25,.125]:
        test=gain+(proposal-gain)*rate;err,_=loss(test)
        if err<bestloss:best=test;bestloss=err;break
    gain=best;history.append({'iteration':iteration,'loss':bestloss})
    if error-bestloss<1e-8:break
for light,g in zip(created,gain):light.data.energy=float(g*5)
report={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reflectors':probes,'powers':{o.name:o.data.energy for o in created},'disabled_old_reflectors':[name for name in powers if name.startswith('Rook ')],'fit_history':history,'method':'Real glossy spot reflectors, target smooth normals, isolated BSDF responses fitted through AgX. No geometry/material changes; numerical loss is not an acceptance criterion.'}
(out/'fit.json').write_text(json.dumps(report,indent=2)+'\n')
s.cycles.samples=96;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';s.render.filepath=str(out/'wood.png')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'rook.blend'))
bpy.ops.wm.open_mainfile(filepath=str(out/'rook.blend'),load_ui=False);s=bpy.context.scene;gpu(s);bpy.ops.render.render(write_still=True)
cam=s.camera;cam.data.shift_x=0;cam.data.shift_y=0;cam.data.sensor_fit='VERTICAL';cam.data.ortho_scale=4.3;cam.location=(0,-12,1.4);cam.rotation_euler=(Vector((0,0,1.4))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.resolution_x=600;s.render.resolution_y=900;s.render.filepath=str(out/'side.png');bpy.ops.render.render(write_still=True)
print('ROOK_HIGHLIGHT_STUDY_COMPLETE')

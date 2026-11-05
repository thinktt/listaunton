"""Check OCIO view/Look against Blender's own PNG export before inverse fitting."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np,PyOpenColorIO as ocio

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--source',default='history/bishop-mission-002/bishop-rebuilt.blend');p.add_argument('--out',default='build/bishop-mission/color-pipeline')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
source=ROOT/a.source
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.context.scene
out=ROOT/a.out;out.mkdir(parents=True,exist_ok=True)
config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL'))/'datafiles/colormanagement/config.ocio'))
view=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,display=s.display_settings.display_device,view=s.view_settings.view_transform)
print('SCENE_COLOR_SETTINGS',s.display_settings.display_device,s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma,flush=True)
print('OCIO_LOOKS',list(config.getLookNames()),flush=True)
intensity=np.geomspace(.0001,32,128).astype(np.float32)
colors=np.array([[1,1,1],[1,.5,.1],[.3,1,.1],[.2,.4,1],[1,.2,.2],[.8,.6,.25]],dtype=np.float32)
linear=(colors[:,None,:]*intensity[None,:,None]).copy()
h,w=linear.shape[:2];pixels=np.dstack([linear,np.ones((h,w),dtype=np.float32)])
im=bpy.data.images.new('Color pipeline diagnostic',width=w,height=h,float_buffer=True,alpha=False)
im.colorspace_settings.name='Linear Rec.709';im.pixels.foreach_set(pixels.reshape(-1))
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.dither_intensity=0
im.save_render(str(out/'blender-swatches.png'),scene=s)
read=bpy.data.images.load(str(out/'blender-swatches.png'),check_existing=False);read.colorspace_settings.name='Non-Color'
actual=np.array(read.pixels[:],dtype=np.float32).reshape(h,w,4)[:,:,:3]
results={}
for label,override in [('view_only',False),('view_and_look',True)]:
 pipeline=ocio.LegacyViewingPipeline();pipeline.setDisplayViewTransform(view)
 if override:pipeline.setLooksOverride('' if s.view_settings.look=='None' else s.view_settings.look);pipeline.setLooksOverrideEnabled(True)
 processor=pipeline.getProcessor(config);cpu=processor.getDefaultCPUProcessor()
 predicted=linear.copy();cpu.applyRGB(predicted)
 encoded=np.rint(np.clip(predicted,0,1)*255)/255
 group=processor.createGroupTransform();group.setDirection(ocio.TRANSFORM_DIR_INVERSE)
 inv=config.getProcessor(group).getDefaultCPUProcessor();back=predicted.copy();inv.applyRGB(back)
 results[label]={'mean_8bit_error':float(np.abs(encoded-actual).mean()*255),'max_8bit_error':float(np.abs(encoded-actual).max()*255),'roundtrip_max_relative_error':float(np.max(np.abs(back-linear)/np.maximum(linear,.001)))}
 print(label,results[label],flush=True)
(out/'validation.json').write_text(json.dumps({'settings':{'display':s.display_settings.display_device,'view':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma},'comparisons':results,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},indent=2)+'\n')

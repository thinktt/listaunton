"""Prepare the unchanged selected image for linear-light fitting, without rendering."""
import argparse,json,sys
from pathlib import Path
import bpy
import numpy as np
import PyOpenColorIO as ocio
sys.path.insert(0,str(Path(__file__).parent))
from mission_scene import ASSETS,BUILD,MODEL,json_file,sha

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--scene",type=Path,default=MODEL)
    p.add_argument("--out",type=Path,default=BUILD/"material-observations")
    a=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    a.out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(a.scene),load_ui=False)
    scene=bpy.context.scene
    assert scene.view_settings.look=="None" and scene.view_settings.gamma==1 and scene.view_settings.exposure==0
    image=bpy.data.images.load(str(ASSETS/"ref.png"),check_existing=False)
    image.colorspace_settings.name="Non-Color"
    w,h=image.size;assert (w,h)==(1254,1254)
    values=np.empty(w*h*4,np.float32);image.pixels.foreach_get(values)
    display=values.reshape(h,w,4)[::-1].copy()
    # Match the exact uint8/255 normalization used by the original Pillow input.
    # Blender's image decoder can differ by one float32 ULP; inverse AgX expands it.
    display=np.rint(display*255).astype(np.float32)/np.float32(255)
    linear=display[:,:,:3].copy()
    config=ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path("LOCAL"))/"datafiles/colormanagement/config.ocio"))
    view=ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,
        display=scene.display_settings.display_device,view=scene.view_settings.view_transform)
    view.setDirection(ocio.TRANSFORM_DIR_INVERSE)
    config.getProcessor(view).getDefaultCPUProcessor().applyRGB(linear)
    np.save(a.out/"reference-display.npy",display)
    np.save(a.out/"reference-linear.npy",linear)
    json_file(a.out/"reference-values.json",{"source_sha256":sha(ASSETS/"ref.png"),
        "scene_sha256":sha(a.scene),"view":scene.view_settings.view_transform,
        "display":scene.display_settings.display_device,"size":[w,h],
        "method":"Unchanged display RGB transformed through the saved scene's inverse OCIO display/view transform. Fitting input only; no image edits."})
    print("KNIGHT_REFERENCE_VALUES_READY",w,h,scene.view_settings.view_transform)

if __name__=="__main__":main()

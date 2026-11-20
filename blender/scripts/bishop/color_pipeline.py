"""The verified Blender AgX view plus Look, for scene-linear fitting only."""
from pathlib import Path
import bpy
import PyOpenColorIO as ocio

def processors(scene):
    assert scene.view_settings.exposure == 0 and scene.view_settings.gamma == 1
    assert not scene.view_settings.use_curve_mapping
    config = ocio.Config.CreateFromFile(str(Path(bpy.utils.resource_path('LOCAL')) / 'datafiles/colormanagement/config.ocio'))
    view = ocio.DisplayViewTransform(src=ocio.ROLE_SCENE_LINEAR,
        display=scene.display_settings.display_device, view=scene.view_settings.view_transform)
    pipeline = ocio.LegacyViewingPipeline()
    pipeline.setDisplayViewTransform(view)
    pipeline.setLooksOverride('' if scene.view_settings.look=='None' else scene.view_settings.look)
    pipeline.setLooksOverrideEnabled(True)
    forward = pipeline.getProcessor(config)
    inverse = forward.createGroupTransform()
    inverse.setDirection(ocio.TRANSFORM_DIR_INVERSE)
    return forward.getDefaultCPUProcessor(), config.getProcessor(inverse).getDefaultCPUProcessor()

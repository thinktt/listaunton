"""Inspect the installed OCIO display pipeline API for material-response diagnostics."""
import PyOpenColorIO as ocio
for name in ['LegacyViewingPipeline','DisplayViewTransform','LookTransform']:
    cls=getattr(ocio,name)
    print(name,[method for method in dir(cls) if not method.startswith('_')])
for name in ['getProcessor','setLooksOverride','setLooksOverrideEnabled','setDisplayViewTransform']:
    print('LegacyViewingPipeline.'+name,getattr(ocio.LegacyViewingPipeline,name).__doc__)

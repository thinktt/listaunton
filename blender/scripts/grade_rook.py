"""Apply only a smooth RGB color curve; preserve alpha and pixel coordinates."""
from pathlib import Path
import numpy as np
from PIL import Image
import json,shutil,hashlib
root=Path(__file__).resolve().parents[1]
src=root/'assets/candidates/rook/candidate-6.png'
dest=root/'assets/candidates/rook/color-tests';dest.mkdir(exist_ok=True)
im=Image.open(src).convert('RGBA');a=np.array(im);rgb=a[:,:,:3].astype(float)/255
# Darken midtones and reduce yellow/orange by attenuating green more than red.
# Fade the tint at highlights to keep reflections relatively neutral.
curved=rgb**1.16
weight=1-np.clip((rgb.max(2)-.60)/.35,0,1)
gains=np.array([.98,.86,.90])
graded=curved*(1+weight[:,:,None]*(gains-1))
out=a.copy();out[:,:,:3]=np.round(np.clip(graded,0,1)*255).astype('uint8')
Image.fromarray(out).save(dest/'candidate-6-direct-grade.png')
assert np.array_equal(np.array(Image.open(dest/'candidate-6-direct-grade.png'))[:,:,3],a[:,:,3])
print('Saved direct grade; alpha verified unchanged.')

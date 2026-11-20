"""Read the fine contrast in the released walnut for use in its physical finish."""
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np
D=Path(__file__).resolve().parent
im=Image.open(D/'parent-pigment.png').convert('L')
fine=np.asarray(im,dtype=np.float32)-np.asarray(im.filter(ImageFilter.GaussianBlur(3.2)),dtype=np.float32)
np.save(D/'wood-grain.npy',np.int8(np.clip(fine,-120,120)))

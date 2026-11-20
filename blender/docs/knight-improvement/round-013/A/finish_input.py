"""Extract fine walnut figure from the inherited packed albedo."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
D=Path(__file__).resolve().parent
im=Image.open(D/'pigment.png').convert('L')
fine=np.asarray(im,float)-np.asarray(im.filter(ImageFilter.GaussianBlur(2.2)),float)
level=np.asarray(im.filter(ImageFilter.GaussianBlur(5.2)),float)
normalized=np.clip(fine/np.maximum(5,.110*level),-1.6,1.6)
np.save(D/'grain-response.npy',np.rint(normalized*65).astype(np.int8))

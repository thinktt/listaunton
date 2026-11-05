"""Prepare an unchanged-coordinate draft target for linear lighting analysis."""
from pathlib import Path
import argparse
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--size',type=int,default=418);p.add_argument('--directory',default='build/queen-mission/light-fit');args=p.parse_args()
out=ROOT/args.directory;out.mkdir(parents=True,exist_ok=True)
im=Image.open(ROOT/'assets/queen/reference.png').convert('RGB').resize((args.size,args.size),Image.Resampling.LANCZOS)
np.save(out/'reference-srgb.npy',np.array(im,dtype=np.float32)/255)
print('Prepared',args.size,'square analysis target; source file unchanged.')

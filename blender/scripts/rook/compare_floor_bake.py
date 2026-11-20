from pathlib import Path
from PIL import Image
import numpy as np,json
root=Path(__file__).resolve().parents[2];a=np.array(Image.open(root/'build/rook-mission/046-floor-annulus/wood.png').convert('RGBA')).astype(float);b=np.array(Image.open(root/'build/rook-mission/047-floor-atlas/wood.png').convert('RGBA')).astype(float);mask=(a[:,:,3]>127)&(b[:,:,3]>127);delta=np.abs(a[:,:,:3]-b[:,:,:3]);report={'foreground_mean_absolute_rgb_8bit':float(delta[mask].mean()),'p99_absolute_channel_error':float(np.percentile(delta[mask],99)),'alpha_byte_identical':bool(np.array_equal(a[:,:,3],b[:,:,3])),'lower_body_mean_absolute_rgb_8bit':float(delta[600:][mask[600:]].mean())};(root/'build/rook-mission/047-floor-atlas/bake-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

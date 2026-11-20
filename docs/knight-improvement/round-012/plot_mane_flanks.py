"""Draw opposed native surfaces under the same virtual raking light."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(sys.argv[1]);names=sys.argv[2:]
w,h=200,307
font=ImageFont.load_default(size=13)
sheet=Image.new('RGB',(len(names)*(w+8),2*(h+26)+32),'#232826');draw=ImageDraw.Draw(sheet)
data={name:np.load(root/f'flanks-{name}.npz') for name in names}
diff={}
for col,name in enumerate(names):
    surface=data[name];diff[name]={}
    for row,side in enumerate(['near','far']):
        a=surface[side];finite=np.isfinite(a)
        # Derivatives of normalized side depth in the common head frame.
        safe=np.where(finite,a,0.)
        dz,dx=np.gradient(safe,-.01,.01)
        length=np.sqrt(dx*dx+dz*dz+1.)
        light=(.55*dx-.57*dz+.61)/length
        grey=np.where(finite,54+176*np.clip(light,0,1),31).astype(np.uint8)
        x=col*(w+8);y=row*(h+26)
        draw.text((x+4,y+3),f'{name} / {side} flank',font=font,fill='#ede8db')
        sheet.paste(Image.fromarray(grey).convert('RGB').resize((w,h),Image.Resampling.BICUBIC),(x+4,y+24))
        base=data['parent'][side];common=finite&np.isfinite(base)
        diff[name][side]={'newly_open_grid_points':int((~finite&np.isfinite(base)).sum()),
            'newly_covered_grid_points':int((finite&~np.isfinite(base)).sum()),
            'mean_absolute_depth_change':round(float(abs(a[common]-base[common]).mean()),4)}
draw.text((4,sheet.height-24),'Same light on both flanks',font=font,fill='#dfdfd8')
sheet.save(root/'mane-flanks.png')
(root/'mane-flanks.json').write_text(json.dumps({'method':'Mirror and render identical unposed x,z windows. An outer silhouette movement can change coverage without opening a hole. Consult the enclosed-gap counts and inspect the actual rotating model.','change_from_parent':diff},indent=2)+'\n')

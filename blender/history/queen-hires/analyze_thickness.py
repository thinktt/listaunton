import ast, sys, math
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2]
out=root/'outputs/queen-hires'
sys.path.insert(0,str(out))
import overlay_qa as qa
src=np.asarray(Image.open(out/'reference.png').convert('RGB')).max(axis=2)
model=np.asarray(Image.open(out/'queen-matched.png').convert('RGBA'))[:,:,3]>127
masks={t:qa.fill_holes(qa.largest_component(src>t)) for t in (1,3,6,12)}
tree=ast.parse((out/'build_queen.py').read_text())
profile=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='body_profile' for t in n.targets))
p=np.asarray(profile)
# Interpolated control polyline for identifying which region drives an outline.
idx=np.linspace(0,len(p)-1,6000)
rs=np.interp(idx,np.arange(len(p)),p[:,0]);zs=np.interp(idx,np.arange(len(p)),p[:,1])
S=273.5; SN=math.sin(math.radians(55.32));C=math.cos(math.radians(55.32))
rows=[]
for y in (330,340,350,360,380,400,420,460,500,530,540,550,560,570,580,590,600,610,620,640,660,680,700,800,940,1000,1060):
    item={'y':y}
    for t,m in masks.items():
        xx=np.flatnonzero(m[y]);item[str(t)]=(int(xx[0]),int(xx[-1])) if len(xx) else None
    xx=np.flatnonzero(model[y]);item['model']=(int(xx[0]),int(xx[-1])) if len(xx) else None
    d=(y-(874-S*C*zs))/(S*SN*rs)
    widths=S*rs*np.sqrt(np.maximum(0,1-d*d))
    k=np.argmax(widths);item['driver']=[round(float(rs[k]),3),round(float(zs[k]),3),round(float(widths[k]),1)]
    rows.append(item)
print('y    mask1       mask3       mask6       mask12      model       controlling r,z,halfwidth')
for item in rows:
    print(str(item['y']).ljust(5),*(str(item[t]).ljust(12) for t in ('1','3','6','12','model')),item['driver'])

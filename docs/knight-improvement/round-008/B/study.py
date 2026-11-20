"""Compare contour, specular placement, and physical section smoothness."""
from pathlib import Path
import json
import sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'scripts/knight'))
from audit_mission import registered,black

def profile(data):
    out={}
    parent=json.loads((OUT/'chest-parent.json').read_text())
    for key,rows in data['horizontal'].items():
        curve=np.asarray(rows)
        curve=curve[abs(curve[:,0])<=.7]
        peak=int(np.argmax(curve[:,1]))
        rebounds=[]
        for vals in (curve[:peak+1,1][::-1],curve[peak:,1]):
            rebounds.append(float(max(vals-np.minimum.accumulate(vals))))
        base=np.asarray(parent['horizontal'][key])
        yp=np.arange(-.67,.671,.01)
        tilt=lambda c:np.degrees(np.arctan((np.interp(yp+.025,c[:,0],c[:,1])-np.interp(yp-.025,c[:,0],c[:,1]))/.05))
        out[key]={'outward_rebound_within_0_7':round(max(rebounds),4),
                  'maximum_change_from_parent_in_section_normal_degrees':round(float(np.max(abs(tilt(base)-tilt(np.asarray(rows))))),2)}
    center=np.asarray(data['center'])
    z,x=center.T
    near=(z>=1.75)&(z<=2.30)
    zz=np.arange(1.79,2.271,.01)
    left=np.degrees(np.arctan((np.interp(zz,z,x)-np.interp(zz-.05,z,x))/.05))
    right=np.degrees(np.arctan((np.interp(zz+.05,z,x)-np.interp(zz,z,x))/.05))
    out['center']={'widest_breast_z':round(float(z[near][np.argmax(x[near])]),3),'widest_breast_x':round(float(x[near].max()),4),
                     'max_turn_degrees_over_0_10':round(float(max(abs(right-left))),2),
                     'x_at_1_72':round(float(np.interp(1.72,z,x)),4)}
    zline=np.arange(1.90,2.851,.02)
    angles=np.degrees(np.arctan((np.interp(zline+.05,z,x)-np.interp(zline-.05,z,x))/.1))
    reversal=angles-np.minimum.accumulate(angles)
    out['center']['largest_cumulative_reverse_turn_degrees_1_90_to_2_85']=round(float(reversal.max()),2)
    if 'midline_collar_section_z_breast_x_collar_x' in data:
        across=np.asarray(data['midline_collar_section_z_breast_x_collar_x'])
        for a,b in zip(across[:-1],across[1:]):
            da=a[1]-a[2];db=b[1]-b[2]
            if da<=0 and db>0:
                out['center']['height_where_breast_emerges_from_collar']=round(float(a[0]+(b[0]-a[0])*(-da)/(db-da)),4)
                break
    return out

refs=registered()
crop=(290,530,725,765)
pics={'Original':refs['original'].crop(crop),'Black 2':refs['selected'].crop(crop),'parent':Image.open(OUT/'parent-wood.png').crop(crop)}
for path in sorted(OUT.glob('trial-*-chest.png')):pics[path.stem.removesuffix('-chest')]=Image.open(path)
if (OUT/'wood.png').exists():pics['B']=Image.open(OUT/'wood.png').crop(crop)
edges={}
shading={}
paths=json.loads((OUT.parent/'chest-carving-study/paths-fit.json').read_text())['curves']
yy,xx=np.indices((235,435));yy+=530;xx+=290
traces={}
for name in ('shoulder','crest','trough'):
    co=np.array([row['pixel'] for row in paths[name]])
    traces[name]=np.interp(yy,co[:,1],co[:,0])
lum=lambda im:np.asarray(black(im.convert('RGBA')).filter(ImageFilter.GaussianBlur(2.4)))@np.array([.2126,.7152,.0722])
target=lum(pics['Black 2'])
for label,pic in pics.items():
    a=np.asarray(pic.convert('RGBA'))
    mask=a[:,:,3]>127
    if label in ('Original','Black 2'):mask&=a[:,:,:3].max(2)>12
    edge={}
    for j in range(540,656):
        l=mask[j-530]
        hs=np.flatnonzero(l[:-4]&l[1:-3]&l[2:-2]&l[3:-1]&l[4:])
        edge[j]=int(hs[-1])+294
    edges[label]=edge
    g=lum(pic)
    shade={}
    for name,yaxis in traces.items():
        band=(abs(xx-yaxis)<=3)&(yy>=580)&(yy<=728)
        region=(abs(xx-yaxis)<=12)&(yy>=580)&(yy<=728)
        shade[name+'_mean_luma']=round(float(g[band].mean()),2)
        shade[name+'_local_mae_to_black2']=round(float(abs(g-target)[region].mean()),2)
    end=(yy>=675)&(yy<=739)&(abs(xx-traces['crest']-48)<15)
    shade['terminal_luma_p90']=round(float(np.percentile(g[end],90)),2)
    shading[label]=shade
stats={}
for label,edge in edges.items():
    cost={}
    for source in ('Original','Black 2'):
        cost[source]={}
        for lo,hi in ((540,580),(581,655),(540,655)):
            cost[source][f'{lo}–{hi}']=round(float(np.mean([abs(edge[y]-edges[source][y]) for y in range(lo,hi+1)])),2)
    data={'mean_edge_error_pixels':cost,'edge_at_545':edge[545],'shading':shading[label]}
    sections=OUT/f'chest-{label}.json'
    if sections.exists():data['sections']=profile(json.loads(sections.read_text()))
    stats[label]=data
old=OUT/'chest-7B.json'
if old.exists():stats['discarded_7B']={'sections':profile(json.loads(old.read_text()))}
(OUT/'chest-study.json').write_text(json.dumps(stats,indent=2)+'\n')
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
def details(names,file):
    w,h=316,193
    canvas=Image.new('RGB',(w*len(names),h*3+32),'#292b2c')
    d=ImageDraw.Draw(canvas)
    for col,label in enumerate(names):
        dx=col*w
        im=black(pics[label].convert('RGBA')).resize((312,169),Image.Resampling.LANCZOS)
        canvas.paste(im,(dx,25))
        d.text((dx+4,3),label,font=font,fill='white')
        prefix=label
        for row,side in enumerate(('near','far')):
            task=OUT/f'{prefix}-clay-{side}.png'
            if not task.exists():continue
            q=Image.open(task).convert('RGBA')
            q=black(q).crop((146,275,511,502)) if side=='near' else black(q).crop((128,275,494,502))
            q=q.resize((309,192),Image.Resampling.LANCZOS)
            canvas.paste(q,(dx,202+row*193))
    canvas.save(OUT/file)
names=[n for n in pics if n.startswith('trial-')]
if names:details(['parent']+names,'trial-comparison.png')
if 'B' in pics:details(['Original','Black 2','parent','B'],'chest-comparison.png')

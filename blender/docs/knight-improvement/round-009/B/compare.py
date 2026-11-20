"""Inspect the two source sprites, frozen parent and physically rendered trials at native registration."""
from pathlib import Path
import json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
R=D.parents[2]
sys.path.insert(0,str(R/'scripts/knight'))
from audit_mission import registered,black

BOX=(245,281,524,434)
def open_rgb(path):return black(Image.open(path).convert('RGBA'))
def metrics(tile):
    lum=np.asarray(tile.filter(ImageFilter.GaussianBlur(2)),dtype=float)@[.2126,.7152,.0722]
    ax=[300,320,340,360,380,400,420,440,460,470]
    ay=[345,341,338,338,338,339,340,342,351,357]
    lines=[]
    for x in range(312,457,4):
        px=x-BOX[0]
        col=lum[:,px-2:px+3].mean(1)
        guide=round(np.interp(x,ax,ay))-BOX[1]
        peak=guide-14+np.argmax(col[guide-14:guide+15])
        valley=peak+6+np.argmin(col[peak+6:peak+29])
        threshold=.5*(col[peak]+col[valley])
        lo=hi=peak
        while lo>peak-22 and col[lo-1]>threshold:lo-=1
        while hi<valley and col[hi+1]>threshold:hi+=1
        lines.append([int(x),int(peak+BOX[1]),int(1+hi-lo),float(col[peak]),float(col[valley])])
    upper=lum[294-BOX[1]:314-BOX[1],320-BOX[0]:374-BOX[0]].max(0)
    surface=[]
    for x in range(280,447,2):
        col=lum[:,x-BOX[0]]
        inds=np.flatnonzero(col>16)
        surface.append([x,int(inds[0]+BOX[1]) if len(inds) else None])
    values=np.array(lines)
    return {'median_main_highlight_width_px':float(np.median(values[:,2])),
        'median_main_luma':round(np.median(values[:,3]),2),
        'median_below_main_luma':round(np.median(values[:,4]),2),
        'upper_band_median_maximum_luma':round(np.median(upper),2),
        'forward_sweep_px':round(np.median(values[-4:,1])-np.median(values[9:18,1]),2),
        'visible_top_scan':surface,
        'main_trace':[r[:3]+[round(r[3],2),round(r[4],2)] for r in lines]}

def go():
    refs=registered()
    tiles={'Original':black(refs['original']).crop(BOX),'Black 2':black(refs['selected']).crop(BOX),
           'Parent':open_rgb(D/'parent-wood.png').crop(BOX)}
    complete=(D/'wood.png').is_file() and '--trials' not in sys.argv
    if complete:tiles['9B']=open_rgb(D/'wood.png').crop(BOX)
    else:
        for p in sorted(D.glob('trial-*-crest.png')):
            if '-clay-' not in p.name:tiles[p.stem.replace('-crest','')]=open_rgb(p)
    w,h=279,153
    cols=4 if complete else 3
    rows=(len(tiles)+cols-1)//cols
    canvas=Image.new('RGB',(cols*w,rows*(h+24)),'#262828')
    dr=ImageDraw.Draw(canvas)
    res={}
    for i,(name,tile) in enumerate(tiles.items()):
        x=i%cols*w;y=i//cols*(h+24)
        dr.text((x+5,y+3),name,fill='white')
        canvas.paste(tile,(x,y+23))
        res[name]=metrics(tile)
    ref=np.array(res['Black 2']['visible_top_scan'])[:,1]
    other=np.array(res['Original']['visible_top_scan'])[:,1]
    for name,data in res.items():
        outline=np.array(data['visible_top_scan'])[:,1]
        data['local_top_outline_error_to_black2_px']=round(float(abs(outline-ref).mean()),2)
        data['local_top_outline_error_to_original_px']=round(float(abs(outline-other).mean()),2)
        print(name,{k:v for k,v in data.items() if k not in ('visible_top_scan','main_trace')})
    stem='crest-comparison' if complete else 'shape-tests'
    canvas.save(D/(stem+'.png'))
    (D/(stem+'.json')).write_text(json.dumps(res,indent=2)+'\n')
if __name__=='__main__':go()

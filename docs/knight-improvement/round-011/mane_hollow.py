"""Locate the inside shadow of the long mane and compare against native part boundaries."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
r=Path(sys.argv[1]).resolve();d=Path(sys.argv[2]);sys.path.insert(0,str(r/'scripts/knight'))
from audit_mission import registered,black
refs=registered();ims={'Original black':refs['original'],'Black 2':refs['selected'],'Original white (mirrored)':refs['white_mirrored'],'Current model':Image.open(r/'assets/knight/render.png')}
rows=np.array([p for p in json.loads((d/'back-mane-parent.json').read_bytes())['rows'] if 460<=p[0]<=640])
out=Image.new('RGB',(len(ims)*214,318),'#262926');draw=ImageDraw.Draw(out);font=ImageFont.load_default(size=14)
bounds=(177,424,374,675);report={}
for i,(name,im) in enumerate(ims.items()):
    rgb=black(im.convert('RGBA'));luma=np.asarray(rgb.filter(ImageFilter.GaussianBlur(4)),float)@[.2126,.7152,.0722]
    coord=[]
    for y,left,right in rows:
        # The trough in both source images falls within this wide corridor around
        # a few hand-picked points. The far left outer outline is excluded.
        center=np.interp(y,[460,500,540,580,610,640],[277,268,270,276,286,298])
        lo=int(max(left+7,center-22));hi=int(center+24)
        section=luma[y,lo:hi+1]
        x=lo+int(np.argmin(section))
        coord.append([int(y),x,int(right),round(float(luma[y,x]),1)])
    x=i*214;out.paste(rgb.crop(bounds),(x+8,28))
    draw.text((x+8,4),name,fill='white',font=font)
    draw.line([(x+8+line[2]-bounds[0],28+line[0]-bounds[1]) for line in coord],fill='#5fd2b7',width=1)
    draw.line([(x+8+line[1]-bounds[0],28+line[0]-bounds[1]) for line in coord],fill='#f7bc4b',width=1)
    report[name]={'samples':coord,'distance_x_mean':round(float(np.mean([q[2]-q[1] for q in coord])),2),'distance_x_y490_to_575':round(float(np.median([q[2]-q[1] for q in coord if 490<=q[0]<=575])),2)}
draw.line((8,296,31,296),fill='#5fd2b7',width=2);draw.text((39,287),'Physical mane edge in current knight',fill='#eeede7',font=font)
draw.line((312,296,335,296),fill='#f7bc4b',width=2);draw.text((343,287),'Darkest line in the local image',fill='#eeede7',font=font)
out.save(d/'mane-hollow.png');(d/'mane-hollow.json').write_text(json.dumps(report,indent=2)+'\n')
for name,v in report.items(): print(name,v['distance_x_y490_to_575'],v['samples'][::15])

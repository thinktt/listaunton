"""Read-only pixel landmarks for the king base; never modifies references."""
from pathlib import Path
import argparse,hashlib,json
from collections import deque
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def components(mask):
    todo=set(zip(*np.where(mask)));parts=[]
    while todo:
        seed=todo.pop();q=deque([seed]);part=[seed]
        while q:
            y,x=q.popleft()
            for d in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
                if d in todo:todo.remove(d);q.append(d);part.append(d)
        if len(part)>10:
            p=np.array(part);parts.append(dict(pixels=len(part),centroid_xy=p.mean(0)[::-1].tolist(),bounds_xyxy=[int(p[:,1].min()),int(p[:,0].min()),int(p[:,1].max()+1),int(p[:,0].max()+1)]))
    return sorted(parts,key=lambda p:p['pixels'],reverse=True)
def main(output):
    out=ROOT/output;out.mkdir(parents=True,exist_ok=True);rows=[];box=(350,750,750,1070)
    sheet=Image.new('RGB',(820,365),'#17191b');draw=ImageDraw.Draw(sheet)
    for i,(label,path) in enumerate([('Reference',ROOT/'assets/king/reference.png'),('Accepted 014',ROOT/'history/king-mission-014/render.png')]):
        im=Image.open(path).convert('RGBA');a=np.asarray(im);rgb=a[:,:,:3].astype(float)*a[:,:,3:4]/255
        bright=(rgb[:,:,2]>65)&(rgb[:,:,1]>85)&(a[:,:,3]>127);area=np.zeros(bright.shape,bool);area[790:1015,500:670]=True
        rows.append(dict(label=label,path=path.relative_to(ROOT).as_posix(),sha256=sha(path),components=components(bright&area)))
        crop=Image.fromarray(rgb.astype('uint8')).crop(box);cd=ImageDraw.Draw(crop)
        for x in range(400,751,50):
            cd.line((x-box[0],0,x-box[0],320),fill='#494949');cd.text((x-box[0]+2,2),str(x),fill='#9cdeef')
        for y in range(800,1071,50):
            cd.line((0,y-box[1],400,y-box[1]),fill='#494949');cd.text((2,y-box[1]+2),str(y),fill='#9cdeef')
        sheet.paste(crop,(i*410+5,35));draw.text((i*410+5,8),label,fill='white')
    sheet.save(out/'base-landmarks.png')
    report=dict(threshold='RGB on black: B>65,G>85,alpha>127 in x[500,670),y[790,1015). A diagnostic, not a match score.',images=rows)
    (out/'landmarks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output');a=p.parse_args();main(a.output)

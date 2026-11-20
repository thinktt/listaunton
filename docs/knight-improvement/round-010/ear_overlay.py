"""Compare the editable ear boundary to visible lines in the two source images."""
import sys,json
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(sys.argv[1]).resolve();n=int(sys.argv[2]);labels=sys.argv[3:]
sys.path.insert(0,str(root/'scripts/knight'))
from audit_mission import registered,black
out=root/f'build/knight-mission/round-{n:03}-judge'
refs=registered()
box=(215,339,592,487);w=box[2]-box[0];h=box[3]-box[1]
canvas=Image.new('RGB',(w*3,(h+24)*len(labels)),'#252728');draw=ImageDraw.Draw(canvas)
for row,code in enumerate(labels):
    points=json.loads((out/f'ear-{code}.json').read_bytes())['visible_ear_columns']
    model=Image.open(root/'assets/knight/render.png' if code=='parent' else root/f'build/knight-mission/improvement-{n:03}-{code}/wood.png')
    for col,(name,im) in enumerate([('Original',refs['original']),('Black 2',refs['selected']),('Model',model)]):
        offset=(col*w,row*(h+24)+24)
        canvas.paste(black(im.convert('RGBA')).crop(box),offset)
        draw.text((offset[0]+5,offset[1]-20),f'{code} ear on {name}',fill='#ece9e2')
        for index in [1,2]:
            polygon=[(x-box[0]+offset[0],v[index]-box[1]+offset[1]) for v in points for x in [v[0]]]
            draw.line(polygon,fill='#78cfd9',width=1)
canvas.save(out/'ear-footprint.png')

"""Compare polished ridges with their actual crosswise changes of surface normal."""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

root = Path(sys.argv[1]).resolve()
number = int(sys.argv[2])
build = root / 'build/knight-mission'
judge = build / f'round-{number:03}-judge'
names = ['parent', *sys.argv[3:]]
font = ImageFont.load_default(size=14)
cell, margin = 342, 36
sheet = Image.new('RGB', (cell*len(names), 362), '#222622')
draw = ImageDraw.Draw(sheet)
for index, name in enumerate(names):
    rec = json.loads((judge/f'bevel-{name}.json').read_bytes())
    rows = rec['columns']
    offsets = np.array(rec['offsets_from_source_px'])
    source = root/'assets/knight/render.png' if name=='parent' else build/f'improvement-{number:03}-{name}/wood.png'
    tile = Image.open(source).convert('RGBA')
    black = Image.new('RGBA', tile.size, 'black')
    black.alpha_composite(tile)
    box = (270,287,493,390)
    base = index*cell
    left, top = base+margin, 30
    width, height = cell-margin-12, 134
    sheet.paste(black.convert('RGB').crop(box).resize((width,height), Image.Resampling.LANCZOS),(left,top))
    def xscale(x):return left+(x-box[0])*width/(box[2]-box[0])
    def yscale(y):return top+(y-box[1])*height/(box[3]-box[1])
    for dy in (-18,18):
        draw.line([(xscale(row['x']),yscale(row['guide_y']+dy)) for row in rows], fill='#7d9890',width=1)
    draw.text((left,5),('Released parent' if name=='parent' else 'Candidate '+name),font=font,fill='#f1ede3')
    graph_top = 204
    graph_height = 74
    for row in rows:
        x = row['x']
        for k, deg in enumerate(row['smooth_normal_angle_change_deg']):
            y0 = graph_top+k*graph_height/(len(offsets)-1)
            y1 = graph_top+(k+1)*graph_height/(len(offsets)-1)
            if deg is None:color='#678892'
            else:
                v = np.clip(deg/14,0,1)
                color = tuple(int(c) for c in (np.array([40,37,34])*(1-v)+np.array([255,195,99])*v))
            draw.rectangle((xscale(x-2), y0, xscale(x+2), y1), fill=color)
    for dy in (-18,0,18):
        draw.text((base+4,graph_top+(dy+18)*graph_height/36-7),str(dy),font=font,fill='#dadfd3')
    draw.text((left,175),'Surface turn across the marked strip',font=font,fill='#edece4')
    for x in (300,380,460):
        draw.text((xscale(x)-10,graph_top+graph_height+4),str(x),font=font,fill='#cbd0c8')
    middle=rec['sections']['middle']['median_10_90_turn_width_px']
    draw.text((left,309),f'Middle section · 80% of turn within {middle:g} px' if middle else 'Middle section crosses separate surfaces',font=font,fill='#edece4')
draw.text((8,338),'Gold marks a sharper turn. Blue marks a boundary between parts.',font=ImageFont.load_default(size=11),fill='#cbd0c8')
sheet.save(judge/'bevel-sections.png')

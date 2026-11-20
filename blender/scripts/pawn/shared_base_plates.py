"""Draw the accepted pawn study from genuine saved camera renders."""
from pathlib import Path
import json
import sys

from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from audit_mission import ASSETS, ROOT, rgba, sheet
from compare_native import to_native
from compare_shared_base import font, side_tile

OUT=ROOT/"docs/pawn-shared-base/iteration-001"
BUILD=ROOT/"build/pawn-shared-base"
OLD=ROOT/"history/pawn-side-quality-003"


def plate(rows, size, name):
    width,height=size
    image=Image.new("RGB",(width*len(rows),height+65),"#222526")
    draw=ImageDraw.Draw(image)
    for i,(label,path,base_px,detail) in enumerate(rows):
        x=i*width
        draw.text((x+width/2,12),label,font=font(20),fill="#f2ede1",anchor="mt")
        image.paste(side_tile(path,width,height,base_px),(x,40))
        draw.line((x+10,height+36,x+width-10,height+36),fill="#8e8b80")
        draw.text((x+width/2,height+44),detail,font=font(15),fill="#e2c69f",anchor="mt")
    image.save(OUT/name)


def draw():
    OUT.mkdir(parents=True,exist_ok=True)
    source=json.loads((OLD/"mission-validation.json").read_text())
    metrics=json.loads((BUILD/"final-comparison/measurements.json").read_text())
    samples=[
        ("Checkpoint 003","Previously accepted",OLD/"profile.png"),
        ("Shared turning","donor-at-old-width",BUILD/"donor-at-old-width/side.png"),
        ("Wider foot","wide-only",BUILD/"wide-only/side.png"),
        ("Strong shortening","wide-short-strong",BUILD/"wide-short-strong/side.png"),
        ("Accepted pawn","balanced-light",ASSETS/"profile.png")]
    rows=[]
    for label,key,path in samples:
        item=metrics[key]
        rows.append((label,path,180*item["diameter"]/source["diameter"],
                     f'Ø {item["diameter"]:.3f}    H {item["height"]:.3f}'))
    plate(rows,(240,356),"proportions.png")
    rows=[
        ("Previous pawn",OLD/"profile.png",242,"Checkpoint 003"),
        ("Queen",ROOT/"assets/queen/queen-wood-profile.png",242,"Checkpoint 033"),
        ("King",ROOT/"history/king-mission-017/profile.png",242,"Checkpoint 017"),
        ("Accepted pawn",ASSETS/"profile.png",242,"Shared turning")]
    plate(rows,(283,162),"donor-bases.png")
    alignment=json.loads((ASSETS/"original-alignment.json").read_text())
    images=[("Lichess original",rgba(ASSETS/"original.png")),
            ("Black candidate 2",to_native(rgba(ASSETS/"reference.png"),alignment)),
            ("Previous pawn",to_native(rgba(OLD/"render.png"),alignment)),
            ("Accepted pawn",to_native(rgba(ASSETS/"render.png"),alignment))]
    sheet(images,(55,80,177,246),238,OUT/"source-comparison.png")


if __name__=="__main__":
    draw()

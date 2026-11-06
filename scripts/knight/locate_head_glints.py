"""Locate fixed-reference highlights on the current evaluated surfaces."""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image
from probe_reflections import ASSETS,surface_probe

TARGETS={
 "ear patch":("near swept ear",[(345,396),(355,392),(366,391),(377,390),(389,389)],7),
 "ear edge":("near swept ear",[(352,412),(377,420),(400,424),(422,430),(448,434)],6),
 "forehead":("continuous horse head and neck",[(530,429),(544,425),(558,427),(574,432),(591,438)],7),
 "lower eyelid":("continuous horse head and neck",[(476,488),(488,495),(504,499),(518,500),(530,499)],5),
}


def main():
    p=argparse.ArgumentParser();p.add_argument("mesh",type=Path);p.add_argument("output",type=Path)
    args=p.parse_args()
    target=np.asarray(Image.open(ASSETS/"ref.png").convert("RGB"),dtype=float)
    sample,digest=surface_probe(args.mesh);features={}
    for name,(part,guesses,radius) in TARGETS.items():
        rows=[]
        for x,y in guesses:
            band=np.arange(y-radius,y+radius+1)
            cy=int(band[target[band,x-2:x+3,1].mean(1).argmax()])
            hit=sample(x,cy)
            if hit and hit["part"].endswith(part):rows.append(hit)
        if len(rows)>=3:features[name]=rows
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({"source_sha256":digest,"features":features},indent=2)+"\n")
    print({k:len(v) for k,v in features.items()})


if __name__=="__main__":main()

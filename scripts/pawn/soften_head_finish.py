"""Change one finish channel around the lower ball, preserving all other texels."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from derive_wood import ROOT,ramp

def run(cfg):
    src=ROOT/cfg["source"]
    assert hashlib.sha256(src.read_bytes()).hexdigest()==cfg["source_sha256"]
    pixels=np.asarray(Image.open(src).convert("RGB")).copy()
    v=1-(np.arange(len(pixels))+.5)/len(pixels)
    band=ramp(v,*cfg["rise"])*(1-ramp(v,*cfg["fall"]))
    lo,hi=cfg["range"]
    channel=cfg.get("channel",0)
    assert channel in (0,1)
    gain=lo+(hi-lo)*pixels[:,:,channel]/255
    value=np.clip(gain*(1+cfg["gain"]*band[:,None]),lo,hi)
    result=pixels.copy();result[:,:,channel]=np.rint(255*(value-lo)/(hi-lo)).astype(np.uint8)
    assert np.array_equal(result[:,:,[i for i in range(3) if i!=channel]],pixels[:,:,[i for i in range(3) if i!=channel]])
    assert np.array_equal(result[band==0],pixels[band==0])
    out=ROOT/cfg["output"];Image.fromarray(result).save(out)
    report={"config":cfg,"sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
            "changed_uv_fraction":float(np.mean(result[:,:,channel]!=pixels[:,:,channel])),
            "other_channels_identical":True,"outside_band_identical":True}
    (ROOT/cfg["record"]).write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("config",type=Path);a=p.parse_args()
    run(json.loads(a.config.read_text()))

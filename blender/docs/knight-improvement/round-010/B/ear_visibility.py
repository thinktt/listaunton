"""Count visible far-ear surface samples in the fixed upper crown window."""
from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D))
from carve import load,sha
from probe_carving import point_probe
def main():
    readings={}
    for name,file in [('Parent','parent.blend'),('10B','knight.blend')]:
        scene=load(file);probe=point_probe(scene)
        counts={};ear=[]
        for y in range(289,325,2):
            for x in range(273,450,2):
                h=probe(x+.5,y+.5);part=h[1].split(' | ')[-1] if h else 'background'
                counts[part]=counts.get(part,0)+1
                if part=='far swept ear':ear.append([x,y])
        readings[name]={'model_sha256':sha(D/file),'roi':[273,289,449,323],'sample_pitch_px':2,'counts':counts,'visible_far_ear_samples':ear}
    (D/'ear-visibility.json').write_text(json.dumps(readings,indent=2)+'\n')
    print({k:r['counts'] for k,r in readings.items()})
if __name__=='__main__':main()

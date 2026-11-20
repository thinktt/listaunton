"""Measure the level shelf around the neck on the actual exported mesh."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

def radial_section(triangles, z, center):
    # Intersect the horizontal plane with each triangular face, then each ray with those segments.
    p0, p1 = triangles, np.roll(triangles, -1, axis=1)
    crosses = (p0[:,:,2] < z) != (p1[:,:,2] < z)
    p0, p1 = p0[crosses], p1[crosses]
    fractions = (z-p0[:,2]) / (p1[:,2]-p0[:,2])
    segments = (p0[:,:2] + fractions[:,None]*(p1[:,:2]-p0[:,:2]) - center).reshape(-1,2,2)
    radii = []
    for degrees in range(360):
        a = np.radians(degrees)
        direction = np.array([np.cos(a),np.sin(a)])
        transverse = np.array([-direction[1],direction[0]])
        offsets = segments @ transverse
        active = (offsets[:,0] <= 0) != (offsets[:,1] <= 0)
        chosen, offsets = segments[active], offsets[active]
        t = offsets[:,0] / (offsets[:,0]-offsets[:,1])
        points = chosen[:,0] + t[:,None]*(chosen[:,1]-chosen[:,0])
        radius = points @ direction
        radii.append(float(radius.max(initial=0)))
    return np.array(radii)

def measure(assets):
    meta = json.loads((assets/'mesh.json').read_bytes())
    mesh = (assets/'mesh.bin').read_bytes()
    vertices = np.frombuffer(mesh,'<f4',count=meta['vertexCount']*8).reshape(-1,8)
    indices = np.frombuffer(mesh,'<u4',offset=meta['indexByteOffset'])
    tris = {}
    for part in meta['parts']:
        block = indices[part['indexOffset']:part['indexOffset']+part['indexCount']].reshape(-1,3)
        tris[part['name']] = vertices[block,:3].astype(float)
    base = next(v for k,v in tris.items() if k.endswith('turned pedestal'))
    head = next(v for k,v in tris.items() if k.endswith('horse head and neck'))
    p = base.reshape(-1,3)
    center = (p[:,:2].min(0)+p[:,:2].max(0))/2
    # Measure the flat surface up to a height loss of 0.002 units (0.13% of base radius).
    top = float(p[:,2].max())
    z = top-.002
    outer = radial_section(base,z,center)
    neck = radial_section(head,top,center)
    margin = outer-neck
    return {'model':meta['sourceSha256'], 'mesh_sha256':hashlib.sha256(mesh).hexdigest(),
        'center':center.tolist(),'top_z':top,'level_band_z':.002,
        'platform_mean_radius':float(outer.mean()),'neck_section_z':top,
        'mean_clearance':float(margin.mean()), 'min_clearance':float(margin.min()),
        'nonpositive_degrees':int((margin<=0).sum()),
        'cardinal_clearance':dict(zip(['front','far','back','near'],margin[::90].tolist())),
        'table':np.column_stack((outer,neck,margin)).round(5).tolist()}

def sheet(data, outfile):
    scale=105; w,h=325,352
    image=Image.new('RGB',(w*len(data),h),'#202522')
    draw=ImageDraw.Draw(image)
    for i,(name,d) in enumerate(data.items()):
        cx=i*w+w/2;cy=h/2
        draw.text((i*w+10,7), name+' / platform seen from above',fill='#ecece3')
        for column,color in [(0,'#f6c980'),(1,'#8ccdb4')]:
            pts=[]
            for n,row in enumerate(d['table']):
                a=np.radians(n);pts.append((cx+scale*row[column]*np.cos(a),cy-scale*row[column]*np.sin(a)))
            draw.line(pts+pts[:1],fill=color,width=2)
        draw.text((i*w+7,h-42),'Gold: level surface   Green: neck footprint',fill='#dedbd3')
        draw.text((i*w+7,h-22),f"Front {d['cardinal_clearance']['front']:.3f}   Back {d['cardinal_clearance']['back']:.3f}    model units",fill='#dedbd3')
    image.save(outfile)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('out',type=Path);p.add_argument('assets',type=Path,nargs='+')
    a=p.parse_args()
    result={source.parent.name if source.name=='knight' else source.name:measure(source) for source in a.assets}
    a.out.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    sheet(result,a.out.with_suffix('.png'))
    for key,row in result.items():print(key,{k:v for k,v in row.items() if k!='table'})

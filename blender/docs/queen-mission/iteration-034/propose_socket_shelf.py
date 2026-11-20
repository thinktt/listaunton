"""Test flatter socket shelves while preserving their projected front arcs."""
from pathlib import Path
import json
import numpy as np

P=Path(__file__).resolve().parent;S=P.parents[2]
c=np.load(P/'controls-033.npy')
r=np.linalg.norm(c[:,:,:2],axis=2).mean(1);z=c[:,:,2].mean(1)
np.save(P/'controls-033.npy',c)
source='243844939937d0b753df253810f0e60d67b86a664f14b86dd678e7e22d348a68'
configs=[]
# Keep the vertical outer wall and its top ring 33 exact. The roof becomes a
# broader shelf as its inner seat lowers; upper-stem edits decay by ring 42.
weights={34:-.18,35:-.325,36:.106,37:.596,38:1,39:.625,40:.28,41:.0625}
for tag,drop in [('267-flatter-socket-seat-032',.032),('268-flatter-socket-seat-050',.050)]:
    dz={str(i):float(-drop*w) for i,w in weights.items()}
    shelf_outer=float(z[35]+dz['35']);shelf_inner=float(z[38]+dz['38'])
    for i,t in [(36,.42),(37,.79)]:
        dz[str(i)]=float(shelf_outer*(1-t)+shelf_inner*t-z[i])
    rr={str(i):float(r[i]+np.cos(np.deg2rad(54))/np.sin(np.deg2rad(54))*dz[str(i)]) for i in weights}
    cfg={'variant':tag,'source_sha256':source,'angle':54,'floor':860.223491056495,
         'scope':'Controls 34-41 only. Outer socket wall, flare, foot, upper stem and all upper geometry exact.',
         'hypothesis':'Broaden the shelf and lower the inner seat while retaining each edited front meridian projection at 54 degrees.',
         'inner_seat_drop':drop,'ring_radii':rr,'ring_z_offsets':dz}
    target_z=z.copy();target_r=r.copy()
    for i in weights:target_z[i]+=dz[str(i)];target_r[i]=rr[str(i)]
    assert np.all(np.diff(target_z[29:45])>0)
    assert np.all(np.diff(target_r[29:42])<=1e-6)
    cfg['front_arc_constraint_max_pixel_error']=float(np.abs(264.61125*(-np.cos(np.deg2rad(54))*(target_z-z)+np.sin(np.deg2rad(54))*(target_r-r))).max())
    cfg['shelf_top_height_span_35_to_38']=float(target_z[38]-target_z[35])
    cfg['shelf_radial_span_35_to_38']=float(target_r[35]-target_r[38])
    configs.append(cfg);(P/(tag+'.json')).write_text(json.dumps(cfg,indent=2)+'\n')
(P/'socket-shelf-studies.json').write_text(json.dumps(configs,indent=2)+'\n')
print(json.dumps(configs,indent=2))

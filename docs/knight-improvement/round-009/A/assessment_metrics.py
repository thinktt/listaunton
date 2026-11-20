"""Bind the final checks to the known blend, packed source and gallery images."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
def doc(name):return json.loads((D/name).read_text())
def sha(name):return hashlib.sha256((D/name).read_bytes()).hexdigest()
p=doc('parameters.json');a=doc('verified.json');e=doc('export-verification.json');f=doc('eyes-A.json')
m=doc('evaluated-mesh.json');op=doc('outline-metrics.json');rgb=doc('final-cheek.json');s=doc('paired-cheek.json')
model=sha('knight.blend');pigment=sha('pigment.png')
assert model==p['model_sha256']==a['candidate']['scene_sha256']==e['model_sha256']==f['source_sha256']
assert pigment==p['atlas_sha256']==e['pigment_sha256']==doc('pigment-parameters.json')['output_sha256']
assert sha('wood.png')==p['reopened_renders']['fixed_sha256'] and sha('wood-side.png')==p['reopened_renders']['side_sha256']
changes=[n for n,v in a['parent']['studio'].items() if v!=a['candidate']['studio'][n]]
assert changes==['Eye reflection lower'] and op['parent_overlap']['fixed']==1 and op['parent_overlap']['side']==1
data={'model_sha256':model,'parent_sha256':p['parent_sha256'],'pigment_sha256':pigment,'gallery':p['reopened_renders'],
      'fixed_cheek':{l:measure['cheek'] for l,measure in rgb.items()},'paired_flank_cheek':s,
      'registered_silhouette':op,'fixed_eye':{l:a[l]['eye'] for l in ('parent','candidate')},
      'bilateral_aperture_iou':f['exposed_insert_mirrored_iou'],'changed_studio_sources':changes,
      'nonmanifold_edges':sum(v['nonmanifold_edges'] for v in a['candidate']['meshes'].values()),
      'evaluated_triangles_under_1e-10_double_area':sum(v['double_area_below_1e-10'] for v in m['candidate'].values()),
      'exported_parts':e['parts'],'exported_triangles':e['triangles'],'exported_varnish_bytes':e['finish_file_bytes'],
      'packed_png_equals_delivered_atlas':e['packed_png_matches'],'all_existing_uv_data_exact':all(v['uv_exact'] for v in e['uv_and_geometry'].values())}
data['dense_angular_eye_comparison']=doc('eye-comparison.json')
data['physical_side_samples']={s:doc('eyes-'+s+'.json')['near_exposed_insert']['samples'] for s in ['A','parent']}
data['protected_chest_crown_and_muzzle']=e['uv_and_geometry']['Knight | continuous horse head and neck']['chest_crest_and_muzzle_probes']
(D/'assessment-metrics.json').write_text(json.dumps(data,indent=2)+'\n')
print(model,pigment,data['nonmanifold_edges'])

# Knight reconstruction

The owner rejected the previous head after rotating it: its separate lower jaw looked like a hanging mass under a beak. This revision follows the owner's request for a recognizable carved horse head with a more conical muzzle, and the owner-endorsed imagined side view in `assets/knight/concepts/side-01.png`. That concept is an interpretation, not recovered geometry. The original Lichess black and white sprites still guide the set's character and overhead comparison; selected black candidate 2 supports detail interpretation. All source images remain unchanged.

The skull, cheek, chin and muzzle now share one continuous loft envelope that joins the neck. Its cross-sections taper toward a small rounded muzzle end, with recessed nostrils, a small upper-lateral eye and a brow. The long ears lie back along the poll. The upper neck and mane meet without the open gap introduced by the first anatomy study; the lower neck, turned pedestal and saved 54-degree orthographic camera retain their established character.

Seven visible components are individually closed and overlap: head/neck skin, mane, two ears, two eyes, and pedestal. Two closed construction lofts remain hidden and editable. The parts are not fused for manufacturing. Depth, eye and nostril carving, and unseen surfaces remain artistic choices. Neutral clay does not reproduce the wood material.

Four anatomy passes follow the initial seven reconstruction passes. The rejected committed model and its Blender file are preserved in `history/knight/07-before-anatomy-correction`; the anatomy studies are in `08-single-envelope-study`, `09-concept-profile-study`, and `10-joined-mane-study`. `assets/knight/anatomy-comparison.png` compares the rejected head, approved side concept and revision. `anatomy-angles.png` shows true level profile, front, three-quarter, side, opposite, and reference-camera views.

## Rebuild

From the repository root, using Blender, ordinary Python with Pillow/NumPy, and Node:

```sh
blender --background --python scripts/knight/build_knight.py
blender --background --python scripts/knight/qa_views.py
python scripts/knight/compare.py
blender --background --python scripts/knight/validate.py -- "$PWD"
python scripts/knight/build_qa_sheet.py
python scripts/knight/build_viewer.py
node scripts/knight/check_viewer.cjs
python scripts/build_candidate_pages.py
python scripts/check_model_site.py
```

Use Windows/UNC paths when Windows Blender works on the WSL repository. The viewer's Front button faces the muzzle; Side shows the horse profile. Reset returns to the saved overlay camera.

The export has 184,918 triangles. Validation checks closed components, positive volumes, mesh bounds/normals/indices, source hash and saved-camera agreement. The viewer runtime passes camera and interaction checks, including the horse's front/side presets, with sampled projection error below 0.00005 pixels. Native browser rendering has not been independently tested here.

Original silhouette IoU is 92.50%, with mean boundary discrepancy about 3.14 original pixels; selected candidate IoU is 92.35%, and mirrored original white is 92.32%. These are comparison records. The current priority is the owner-requested plausible horse anatomy across viewing angles; high silhouette overlap in the rejected model did not establish anatomical quality.

# Knight reconstruction

The original Lichess black and white sprites determine the proportions, with selected black candidate 2 supporting detail interpretation. The white sprite is mirrored for comparison; source files remain unchanged.

The head, neck and jaw form a continuous sculpted skin built from volumetric lofts. The model also has a swept mane, paired laid-back ears, recessed eye and nostril details, and a turned pedestal. The seven visible components are individually closed and intersect; they are not fused for manufacturing. Three hidden construction lofts remain editable. The saved reference camera is orthographic at 54°.

Seven render/refinement passes adjusted the silhouette, ear position, cheek undercut, mouth, collar and neck channels. Side, front and opposite renders in `assets/knight/volume-inspection.png` check the inferred depth. Earlier passes are preserved in `history/knight/`.

## Rebuild

From the repository root, using Blender, ordinary Python with Pillow/NumPy, and Node:

```sh
blender --background --python scripts/knight/build_knight.py
python scripts/knight/compare.py
blender --background --python scripts/knight/validate.py -- "$PWD"
python scripts/knight/build_viewer.py
node scripts/knight/check_viewer.cjs
python scripts/build_candidate_pages.py
python scripts/check_model_site.py
```

For supplementary inspection, run `qa_views.py` with Blender and `build_qa_sheet.py` with ordinary Python. Use Windows/UNC paths when Windows Blender works on the WSL repository.

The current exported model has 196,806 triangles. Original silhouette IoU is 96.81%, with mean discrepancy about 1.38 original pixels; the selected reference is 96.50%, and mirrored original white is 96.25%. These measurements do not establish unseen anatomy. Depth, ear cupping, nostrils, cheek and neck-channel carving remain interpretations. Neutral clay does not reproduce the wood material.

Closed components, positive volumes, mesh bounds/normals/indices and source hashes pass validation. The actual viewer runtime passed camera and interaction checks with maximum sampled projection error below 0.00005 pixels. Native browser rendering has not been independently tested in this environment.

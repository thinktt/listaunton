# King projection variants

Five alternate kings explore how an uncertain camera elevation changes the recovered proportions. No candidate has been promoted; the existing king model, camera, mesh and references are preserved byte for byte.

Open **Projection variants** in the king review, or [the standalone comparison](../king-projections.html). **Profiles** uses one camera and scale for all five, **Rotate** keeps the view when switching models, and **Reference overlay** uses each model's own fitted camera. Original Lichess is the default authority; the chosen black candidate 1 is also available.

| Assumed elevation | Height / base diameter | Original silhouette overlap | Selected enlargement overlap |
| --- | ---: | ---: | ---: |
| 48° | 2.221 | 95.51% | 97.13% |
| 52° · current shape | 2.389 | 96.00% | 97.41% |
| 56° | 2.595 | 96.27% | 96.65% |
| 60° | 2.869 | 94.66% | 94.54% |
| 64° | 3.242 | 92.98% | 92.70% |

Overlap is intersection over union of silhouettes, not a measure of complete 3D correctness. The 56° version fits the original outline best among these trials; 52° fits the selected enlargement best. The steepest variants increasingly disagree around circular features. Different elevations cannot preserve every ellipse while retaining plausible planar rings. These are alternatives for visual judgment, not five equally exact solutions.

## Method

The existing king is the starting geometry for every variant. Its turned profile is described in image-space circle centers and radii. Changing elevation requires recovering different heights and adjusting the profile groups. The fitting script keeps the physical foot diameter fixed, weights original silhouette evidence more heavily than the enlargement, and preserves the already fitted front edges of the principal rings. It changes group positions/radii rather than individually distorting each ring. The cross depth also changes with elevation. The 52° variant retains the current shape, translated onto the common ground plane.

Each `.blend` contains the editable body and cross. Both components are closed and positive-volume; they overlap and are not Boolean-fused. The exported mesh, overlay render and saved camera come from that same model. Common front-profile renders use identical camera matrices, resolution, floor and scale. The interactive viewer likewise never normalizes each variant by its height.

## Rebuild

Run from the repository root with Blender, ordinary Python with Pillow/NumPy, and Node.js:

```sh
python scripts/king/fit_projections.py
blender --background --python scripts/king/build_projection_models.py
python scripts/king/analyze_projection_renders.py
python scripts/king/build_projections_viewer.py
python scripts/king/check_projection_variants.py
node scripts/king/check_projections_viewer.cjs
python scripts/build_candidate_pages.py
node scripts/check_candidate_review.cjs
python scripts/check_site.py
```

`assets/king-projections/variants.json` records measurements and fit settings. Per-variant folders retain profiles, render comparisons, camera matrices, source hashes and geometry validation. `baseline-preservation.json` records the existing king hashes before this study. The check scripts exercise matching cameras, common framing, orbit/pan/zoom, candidate switching and lazy tab initialization. Browser visual interaction has not been independently screenshot-tested in the current environment.

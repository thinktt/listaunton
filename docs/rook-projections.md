# Rook projection and proportion study

This study compares six actual geometry refits at **48°, 52°, 54°, 56°, 60°, and 64°**. The 54° entry retains the current rook shape. The canonical rook model, mesh, camera, render, references, profile and builder remain byte-for-byte unchanged; `assets/rook-projections/baseline-preservation.json` records their hashes.

[Open the comparison](../rook-projections.html). The page contains shared-camera front profiles, a freely rotating model with persistent physical framing, and original/selected-reference overlays rendered from each candidate's saved reference camera. Original black is the default; selected black candidate 8 is optional. The references are embedded without altering their pixels. Their pre-existing uniform registration is preserved.

## Geometry and fitting

Each candidate is regenerated through the existing rook builder in an isolated build directory. Feature-group profile heights and bounded collar, neck and crown radii are refitted. Changing the assumed elevation also changes the physical height implied by the image. This is not a collection of camera-only views of one mesh and does not warp reference images.

All candidates have exactly the same base diameter and a base plane at z = 0. The 54° copy is translated to that common ground without changing its shape. Profiles use one identical 600 × 900 orthographic camera (height 4.4 world units, target z = 1.95) and lighting. Rotation uses one shared center and union bounds; switching geometry retains the user's orbit, pan, zoom and projection. Selecting a candidate's reference camera is an explicit action.

The turret has four equal curved merlons, unchanged 20° slot widths, and a constant visible wall-thickness ratio of 23/177 across all variants. The model never independently thickens the rear wall. The cavity floor, notch floor and top-rim heights are constrained separately. The canonical editable Boolean construction is retained.

The objective gives the original silhouette 80% weight and selected candidate 8 20%. The original's near-black wood makes a strict RGB cutoff unreliable around the neck; fitting uses alpha > 128 and maximum RGB > 8. Reports also retain the historical RGB > 12 score and expose cutoffs 4, 8, 12 and 16. Existing lower-ring arcs, both sides of the top rim, notch arcs and the source's rear cavity-floor edge constrain internal geometry. Bounds and regularization keep feature changes modest.

At some camera angles Blender's exact Boolean leaves coincident vertices separated by floating-point epsilon. If closure inspection detects this, a 0.000001-world-unit Weld modifier joins those vertices, followed by a fresh model save, mesh export and render. The modifier and repair count are recorded in the variant manifest; the process stops if closure is still invalid.

## Results

| Assumed camera | Height / base diameter | Original IoU, strict | Original IoU, fit mask | Selected IoU |
| --- | ---: | ---: | ---: | ---: |
| 48° | 1.4541 | 0.9547 | 0.9711 | 0.9760 |
| 52° | 1.5409 | 0.9610 | 0.9791 | 0.9753 |
| 54° (current) | 1.5928 | 0.9565 | 0.9753 | 0.9696 |
| 56° | 1.6493 | 0.9586 | 0.9776 | 0.9659 |
| 60° | 1.8038 | 0.9478 | 0.9660 | 0.9523 |
| 64° | 2.0179 | 0.9363 | 0.9521 | 0.9374 |

The 54° shape was deliberately held fixed; the other candidates receive bounded feature refits. This is a comparison of plausible interpretations, not an unconstrained camera-estimation benchmark.

The scores do not establish that one assumed camera angle is the true original camera. Circular horizontal arcs change apparent ellipticity with elevation, so the wider angle experiments cannot exactly match both the silhouette and every interior ring. Hidden geometry remains an interpretation of the visible source. Materials remain neutral; wood and finish are future work.

The rendered contact sheets are [front profiles](../assets/rook-projections/profiles-comparison.png) and [reference-camera renders](../assets/rook-projections/reference-renders-comparison.png). Each angle directory also contains `overlay-original.png`, `overlay-selected.png`, contour comparisons, fit parameters and QA. The source images and current canonical rook are not overwritten.

## Rebuild and checks

From the repository root with Python + NumPy/Pillow, Blender, and Node:

```sh
python scripts/rook/fit_projections.py
blender -b --python scripts/rook/build_projection_models.py
python scripts/rook/analyze_projection_renders.py
python scripts/rook/build_projections_viewer.py
python scripts/rook/check_projection_variants.py
node scripts/rook/check_projections_viewer.cjs
```

All builders accept `--root`; Blender options follow its `--` separator. `build_projection_models.py -- --angles 60,64` rebuilds only those model/render candidates. The original canonical hash guard must pass before and after building.

The geometry checker verifies six distinct models and mesh buffers, render provenance tied to model hashes, equal diameters and ground levels, equal thin merlons, positive volumes and zero nonmanifold edges for every evaluated union and construction object, normalized finite mesh data, correct saved elevations, common profile cameras and current embedded HTML assets. The actual viewer JavaScript is tested in a Node VM for all six cameras, responsive framing, reference selection, opacity endpoints, context-independent profile fallback, and camera persistence across variant/tab changes. Native browser file access was unavailable; renders and comparison images were visually inspected directly.

Final viewer regression: 1,818 sampled mesh/camera comparisons across six variants and three viewport shapes, maximum error **0.00008331 pixels**. All 30 evaluated editable objects passed closure and positive-volume checks. The 60° union required nine coincident-edge repairs at the recorded 0.000001-unit weld tolerance; other candidates passed without that repair.

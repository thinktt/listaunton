# Rook reconstruction

The original black and white Lichess sprites determine proportions. Black candidate 8 (the direct color grade of candidate 6) supports detail interpretation. Source PNGs are preserved byte-for-byte as `original.png`, `original-white.png`, and `ref.png`.

The editable Blender model uses a continuous subdivided lathe body with a shallow recessed floor and four identical curved merlons. The merlons have a uniform visible radial thickness of 23 / 177 of the outer radius. The hidden feet taper into the body to remove coplanar Boolean seams; this does not thicken the rear wall. Four editable exact-union modifiers form the visible surface. Construction merlons remain named, hidden objects in the blend file.

The saved orthographic camera has 54 degrees elevation and -0.35 degrees roll. The mesh export contains 62,522 visible triangles and the exact saved Blender camera matrices. The viewer uses those matrices for its reset, preserves the interactive orbit between tabs, and defaults to the original black reference. The selected reference uses its existing uniform scale/translation registration. Geometry materials are neutral; wood remains future work.

## Rebuild

From the repository root, with Blender, Python + Pillow/NumPy, and Node available:

```sh
blender -b --python scripts/rook/build_rook.py
python scripts/rook/compare.py
blender -b --python scripts/rook/validate.py -- "$PWD"
python scripts/rook/build_viewer.py
node scripts/rook/check_viewer.cjs
```

`build_rook.py -- --root PATH` permits a relocated staging root. No absolute source paths are embedded in the scripts. Source reference images are packed into the blend file.

## Evidence and limitations

Six rendered revisions were compared. Earlier profile, builder, render and QA snapshots are in `history/rook`; they are evidence, not the current rebuild entry point. Revisions corrected the foot/shoulder height, rounded base curvature, four thin walls, cavity depth, and construction seams. The rear floor edge was raised by 10 model-frame pixels after comparing the original black and white sprites.

`assets/rook/comparison.png` shows original, neutral model and selected reference side by side. `overlay-original.png` and `overlay-selected.png` are actual-source 50% overlays; `contour-*.png` show source boundaries cyan and model boundaries pink.

The inherited strict silhouette mask (alpha > 128 and maximum RGB > 12) reports original IoU 0.95649 and selected IoU 0.96962. The original's near-black wood is partly excluded by that cutoff: RGB cutoffs 8 and 4 yield 0.97526 and 0.98220. These are sensitivity results, not independent evidence of interior fidelity. Strict mean boundary error is 5.70 pixels in the 1254 frame (about 1.34 original sprite pixels). A single view does not establish unseen geometry; rotational symmetry and four equal crenels are informed interpretations.

`validation.json` verifies closed components, positive signed volumes, equal merlon volumes, the current blend hash, binary bounds, finite positions, unit normals and the camera export. `viewer-validation.json` records the actual page's Node VM interaction and 501-vertex camera regression: maximum error below 0.00004 pixels. Native browser visual interaction was unavailable in this task; rendered geometry and source overlays were inspected directly.

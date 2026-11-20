# Round 7A

The upper mane, ear roots and forehead now curve farther back over the eye. At registered image row 325 the crown spans pixels **249–512**. The original spans 249–513, black 2 spans 242–512 and the parent spanned 274–529. Across rows 295–389, mean absolute horizontal error over both edges falls from 15.10 to 3.43 pixels against the original and from 17.22 to 2.91 against black 2. Full-silhouette overlap rises from 97.27% to 97.85% against the original and from 96.67% to 97.51% against black 2.

The ear roots, mane and forehead share a bilateral deformation in the horse's rest coordinates. It moves the rear crown up to 0.169 scene units backwards and the forehead up to 0.103 backwards. A smooth vertical adjustment of up to 0.040 units seats the crown and forehead together. The long side bevel and the centerline continue around the back. The free points of both ears recover 89% of the initial rearward shift towards their original positions. They also open outwards by up to 0.036 units and rise by up to 0.049 units locally. The adjustment tapers to zero towards each root.

The first visible near-ear sample is again **x271, y386**, compared with x244, y386 in the initial uniformly translated study. The front root still ends at x556, y466. Over the tip patch, mean RGB error on a 0–255 scale drops from 26.30 to 21.89 against the original and from 22.00 to 18.84 against black 2 compared with that study. The released parent scored 13.41 and 14.82 there. Bringing the point back costs 0.15 pixels of whole-crown edge error against the original and 0.42 pixels against black 2 compared with the uniform study. The fixed silhouette has zero internal alpha gaps in the upper crown check. In side views the tip sits closer to the side mane face. A small triangular carved plane remains visible above its seated root.

The fixed image fits the original slightly less closely over rows 395–415, where mean edge error rises from 3.83 to 5.02 pixels. Over those same rows the fit to black 2 improves from 3.57 to 1.95 pixels.

The parent studio and orthographic camera are identical. The existing arch catches the same fixed area lights in its new position. Both bare eye meshes retain their coordinates, and the same 163 fixed-camera samples see the eye floor in both scenes, with identical bounds and centroid. All 7,666 vertices in the protected skull region around the eyes retain their exact coordinates. Every visible mesh retains its existing UVs and vertex varnish values. Packed image hashes are identical. The native mesh checks found zero nonmanifold edges and the evaluated meshes have finite normals and zero triangles with double area below 1e-10.

The final scene, both gallery images, outline, ear footprint, eye registration and mesh checks are bound together by their hashes in `assessment-metrics.json`.

## Files

| File | SHA-256 |
| --- | --- |
| parent.blend | `1837b02f0c472044a8e86ffd112d15dbe007eb70d9a4330d86f8f073b7440208` |
| knight.blend | `4c0dafdc512c99a5628441d904650ce51c5c0a81ac13ce2d574b7f9e0343c28d` |
| wood.png | `9166e6ee81cc68068f67c9b44726ed0fbfff9f1cae27d043bf20fd6744d1029f` |
| wood-side.png | `79147b84c66ea211f8c5c7c15b3f5e6e17e0b6ac76f578c62bf82cb523005f8f` |

## Reproduction

1. In the mission directory layout, run Blender 5.2 in background mode with `--python extract.py` to extract the evaluated parent surfaces and orthographic matrix. Run `fit.py` in the mission Python environment to recreate `fit.json` from the registered original and black 2. The fit measures projected mesh-edge intersections and searches six bounded quantities in the shared rest-space deformation defined in `shape.py`.
2. Run Blender in background mode with `--python sculpt.py` to apply the fit and the bilateral correction in `ear_tip.py`, save the editable model and reopen it for the 144-sample fixed and registered side renders. `diagnostic_views.py` also renders opposite, rear and front wood views and a 16-angle clay turn. Camera and render hashes are in `parameters.json`.
3. Run `inspect_features.py`, `verify_registration.py` and `evaluated_mesh.py` in Blender for neutral clay, camera, receiver-light, mesh and UV checks. The matched-parent wood images are copies of the gallery renders after verifying that their studio settings are identical. The eye visibility also appears in `verified.json`.
4. Run `report.py`, `review.py` and `final_study.py` in the mission Python environment. `poll-contour.png` displays the registered outlines. `poll-carving.png` compares both source sprites, native board size and the actual side carving. `clay-ridges.png`, `diagnostics.png` and `clay-turn.webp` show the front, opposite and rear views.
5. Run Blender with `--python trace_ear.py -- STAGING_ROOT MODEL OUTPUT_JSON` to obtain the foremost ear samples at fixed pixel centers. `ear_report.py` compares the final and parent traces with the earlier in-memory ear study. `ear-footprint.png` shows each contour on both registered sources and its model. The matched side photographs and shared clay study are in `ear-study.png`.

# Round 8A

The lower orbital shelf now rolls into the cheek as one convex surface. Both upper lids extend over the eye floor, and both eye floors sit deeper in the carved sockets. The fixed camera sees 110 eye-floor samples at two-pixel spacing, compared with 163 in the parent. The visible almond remains inclined by 11.55°. Sampling the unposed head from opposite sides gives 99.9% overlap between the paired eye openings.

In the fixed walnut render the cheek patch measures **RGB 95, 46, 15**, compared with **130, 65, 27** in the parent and **97, 47, 17** in black 2. Its fine-grain contrast measures 0.2700 on the lead's log-luminance scale, compared with 0.2012 in the parent and 0.2680 in black 2. A denser pigment softens the amber streaks through the lower return. The highlight tapers towards the noseward corner. It remains narrower and less diffuse than the photographed lower-lid highlight, and the eye floor is more subdued in the fixed view.

The 3072×3072 UV atlas carries a local walnut stain and fine anisotropic grain sampled in three-dimensional wood coordinates. Only the head and eye islands receive the pigment edit. The stronger stain reaches the near cheek, tapering to one-third strength on the already denser far side. The identically lit near-flank patch moves from RGB 119, 64, 34 to 91, 48, 24. The far-flank patch moves from 89, 46, 20 to 80, 41, 18 and retains its fine figure. Its local contrast moves from 0.291 to 0.297.

The sculpt changes 7,254 editable skull vertices by more than 0.00001 scene units and seats each eye floor by up to 0.0225 units. The mane, both ears and pedestal retain their exact positions. All visible meshes retain their UV data. The existing lower-eyelid studio card was refocused to 0.044 W over an elliptical area measuring 0.16×0.32 scene units. The other studio lights and fixed camera are identical. Both full-size matched-parent studio renders and all neutral clay views are included.

## Files

| File | SHA-256 |
| --- | --- |
| parent.blend | `8d984d59beea0f86d69bbb5b8f5dc57becf7e707e576412eb8eda4503e81a948` |
| knight.blend | `e021797f7d6063cd9c7293e4d9ec06e196b5885135b6737cfd33738246e5bc7a` |
| pigment.png | `86debdcce4b5b6075ae7510cb25f77066ae912cfb8e1a0c4a49101ed43b79978` |
| wood.png | `921e89261c73e3fde20025b3ee0ca5b65cb5159e1e6a038d840b4936c14d7db6` |
| wood-side.png | `1d5be73848fbeb91658f298bafdf53f544afa5ec808d2379bb0201919df12690` |

The gallery pair was rendered from the reopened scene at 144 samples. The fixed and side silhouette masks exactly match the parent. The exact bytes of `pigment.png` are packed into the model. The release atlas filename recorded in the scene is `wood-atlas-improvement-008-A.png`. The mission's WebGL exporter verified all seven parts, 214,866 triangles, the existing pigment UV layer and per-vertex varnish stream. Its test output is under `webgl-check`. `assessment-metrics.json` binds the final model, both renders, packed pigment, native meshes and WebGL data to these measurements.

## Reproduction

1. With the mission staging layout intact, run Blender 5.2 in background mode with `--python extract.py` to extract the original packed atlas and native UV charts. Run `pigment.py` in the mission Python environment to reproduce `pigment.png`. `surface.py` defines the rest-space carving and pigment coordinates.
2. Run Blender with `--python sculpt.py`. It checks the parent digest, updates the surfaces and polish, focuses the lower card using `lid_card.py`, packs the atlas and saves the editable model. `diagnostic_views.py` reopens the model, verifies its packed image and produces both gallery renders, wood turn views and a 16-angle clay turn.
3. Run `inspect_features.py`, `evaluated_mesh.py` and `export_check.py` in Blender for matched parent-light wood, shared-light clay, topology checks and the actual WebGL export. `verified.json`, `evaluated-mesh.json` and `export-verification.json` record the results.
4. The final feature, board-size, rear and opposite-side sheets are produced by `review.py`, `final_study.py` and `cheek_review.py`. For equal-light side photographs, run Blender with `--python paired_walnut.py -- STAGING_ROOT BLEND OUTPUT_FOLDER` for the two scenes. Then run `walnut_sides.py . parent A` and `flank_stats.py`. `bilateral_eye.py` and `plot_bilateral_eye.py` reproduce the unposed eye comparison.

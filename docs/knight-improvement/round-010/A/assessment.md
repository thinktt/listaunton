# Round 10A

The new bevel sharpens both outer shoulders of the mane. At longitudinal station −0.6, each shoulder turns through 30° to 60° across 0.0184 model units. The parent used 0.0371. At station −0.8 the same measurement falls from 0.0501 to 0.0204. The high point remains centered at all six sampled stations. Five retain their measured peak height exactly and the frontmost peak changes by 0.00013 units. The width within 0.004 units of each peak remains the same.

The front of the lower mane ridge rolls into the forehead before it meets the ear. In matched broad-light clay this removes the long straight highlight bounding the triangular plate. The side still shows the ear as a separate carving, with a short shadow at its seat. Both ear roots turn into the surrounding skull, and the bronze-colored patch beneath the far ear is less conspicuous at 54°. In the 22×8-pixel patch around that ear glint, 90th-percentile luminance drops from 189 to 120. Black 2 measures 66. The broad upper reflection and the lighter far-ear surface remain visible compared with Black 2.

The first two editable rings of each ear keep their original coordinates. The near tip still first appears at x271, y386 in the registered 54° view. Its visible root stops at x553, three pixels earlier than the parent. The new piece and parent have identical true-side silhouette masks. Their fixed-view masks overlap by 0.99939. Fixed silhouette overlap with the original black sprite falls from 0.98231 to 0.98185. Overlap with Black 2 falls from 0.97910 to 0.97890.

The evaluated piece measures 3.24566 × 2.98866 × 5.07268 scene units, the same bounding dimensions as the parent. The mane measures 1.71521 × 1.11524 × 3.34693 in the unposed head axes. Its greatest editable vertex shift is 0.07125, mostly redistribution across the bevel. The greatest visible forehead fillet lift is 0.01926. Both eyes and their finish, and 46,173 chest, cheek and eye-region skull vertices below z4.70, pass an exact coordinate and varnish comparison. The 54° cheek patch remains RGB 97, 47, 16 and the chest stays 106, 52, 21. The fixed camera, all studio lights, UVs, topology and packed pigment compare exactly to the parent.

## Mesh verification

The complete evaluated mane contains 25,600 triangles and each full ear contains 13,312. Independent within-part checks found **zero non-adjacent self-intersections** in the mane, near ear and far ear in both scenes. The evaluated continuous head also has zero, including at the new fillet. These checks include the terminal caps. A separate audit returned zero nonmanifold edges and zero evaluated triangles under the recorded area threshold.

## Files and reproduction

- `knight.blend`, `wood.png` and `wood-side.png` are the submitted scene and both 1254×1254 reopened 144-sample renders.
- `matched-features.png` shows the two sculptures at 54° and in side, front and back clay. `crown-comparison.png` includes both protected references, the full forms and the 100-pixel board views. `paired-walnut.png`, `diagnostics.png` and `clay-turn.webp` show both real flanks, front, back and turn. `sections.png` overlays six measured curves.
- `parameters.json` records the tangent cuts, forehead radii, ear geometry and studio-camera evidence. `validation.json`, `dimensions.json`, `evaluated-mesh.json`, `self-intersections.json`, `skull-intersections.json` and `assessment-metrics.json` hold the underlying geometric and image measurements.
- To rebuild, use Blender 5.2 in background mode with `--python sculpt.py` in the mission staging layout. The script verifies the supplied `parent.blend`, shapes the existing polygon cages, applies the local finish, saves, then reopens the model for both gallery views and the turn. Use `--python sculpt.py -- --render-only` to rerender the frozen scene directly. The byte-identical packed 9A pigment is inside the scene.
- Run `verify.py`, `dimensions.py`, `evaluated_mesh.py` and `self_intersection.py` in Blender. Append `-- --skull` to the last script for the continuous head check. `survey.py` and `interface.py` sample physical ownership under each anatomical feature in the actual cameras. Append `-- --candidate` for the candidate.
- `carving_light.py`, `paired_walnut.py`, `top_sections.py` and `trace_ear.py` each take staging root, scene path and output path after `--`. The parent clay and walnut controls are bound to the parent scene digest. Run `review.py` and `walnut_sides.py . parent A` with Python and Pillow to assemble the final sheets.

| Frozen output | SHA-256 |
|---|---|
| Parent scene | `8e015620e552bda2c1e67866da8a7a3ba0e671c16deb22d93c07fb6c7859121d` |
| 10A scene | `1f308f8ee1e4d2c4c241d2bee15a08a2dab0aa2ce7aa353e8b2765a357efc057` |
| 54° gallery | `7faf9c08d082d9619636a87c35c840400dc77f3051b9f5c9049f057401da61ac` |
| Registered side | `9455958fe9f81546c764148456ffd8d816f829376c367eecd191366f5d1044d8` |

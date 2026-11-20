# Round 9A

The upper eyelid arches five pixels higher at the center of the 54° view. The exposed walnut eye starts at x477 in both sculptures. Its nose-side corner extends from x529 to x540 and lands six pixels lower. The exposed surface grows from 658 to 1,028 pixels. The black reference puts the central upper crease around y464–466. This carving reaches y467, compared with y472 in the parent.

The upper lid and inner eye share a continuous deformation on both flanks. The eye floor has a shallow convex center. I widened the lower cheek turn by stretching the existing bevel outward from its inner edge, burnished a short section, and refocused the existing physical lower-eye reflector. In matched side clay the upper brow covers the enlarged eye and the lower lid curves into the cheek. The geometry remains visible under the parent studio. Its cheek reflects much less light there. The refocused reflector supplies the bright accent in the gallery view.

The brightest part of that cheek reflection moved from y490 to y497, measured at the centroid of its local half-peak area. Black 2 centers at y499. The candidate’s accent is shorter and less diffuse, measuring 16×6 pixels against 31×9 in black 2. The smooth eye has one dominant glint. The photographed surface has finer broken reflections and a more irregular transition into the forward corner. These differences are clearest in the enlargement at the top of `native-eye.png`.

The original 8A pigment is packed byte-for-byte. The fixed cheek sample gives RGB 97, 47, 16 and local contrast 0.263, against RGB 97, 47, 17 and 0.268 in black 2. Under a symmetrical studio the near cheek shifts from RGB 120, 64, 34 to 92, 49, 24. The far cheek shifts from 89, 46, 20 to 80, 41, 18 and keeps its fine grain contrast at about 0.29. The protected chest and pedestal patches reproduce their parent measurements.

Both gallery silhouette masks agree with the parent at every tested pixel. The mirrored eye openings overlap by 99.45%. The pedestal, ears and mane retain exact vertex coordinates. The topology audit found zero nonmanifold edges and zero evaluated triangles below the recorded area threshold. The WebGL exporter wrote all seven meshes, 214,866 triangles and 120,211 bytes of vertex varnish. All existing UV arrays compare byte-for-byte.

## Files

| File | Use |
|---|---|
| `knight.blend`, `wood.png`, `wood-side.png` | Frozen editable sculpture and both reopened 144-sample views |
| `native-eye.png` | Original sprite at its native 300×300, Black 2, 8B, 8A and 9A |
| `final-features.png`, `matched-features.png` | Fixed and side eyes in identical clay, identical parent lighting and the gallery lighting |
| `paired-walnut.png`, `clay-ridges.png`, `diagnostics.png`, `clay-turn.webp` | Both flanks, rear, front and turn |
| `pigment.png`, `source-atlas.png`, `atlas-samples.npz` | Delivered packed atlas, original atlas and 3D pigment coordinates |
| `assessment-metrics.json`, `eye-comparison.json`, `verified.json` | Render and object digests, dense eye rays, studio settings and geometry |

## Reproduction

1. Use the supplied `parent.blend` in this directory and the mission staging scripts. The verified parent SHA-256 is `53ca17473c08fc898e6c29bd5189e4188b3573e003719362cabb102ab621f757`. Running `pigment.py` with the supplied cache and original atlas recreates the 8A pigment. The shader’s packed image is named `Knight walnut | figured cheek pigment 008-A`. Its external release name is `wood-atlas-improvement-008-A.png`.
2. Run Blender 5.2 in the background with `--python sculpt.py`. The script checks its parent, applies the bilateral carving in `surface.py`, edits vertex varnish, focuses the lower reflector with `lid_card.py`, packs the pigment and saves the model. It reopens that file and renders both 1254×1254 gallery images plus the orbit. For the submitted model without rebuilding, use `--python sculpt.py -- --render-only`.
3. Run `inspect_features.py`, `evaluated_mesh.py` and `export_check.py` in Blender for the identical studios, mesh checks and the mission’s WebGL export. `bilateral_eye.py`, `eye_footprint.py` and `paired_walnut.py` each accept the staging root, scene path and output path after `--`. Sample both scenes. The archived parent walnut pair is bound to the parent SHA in `wood-parent/source.json`.
4. With Python and Pillow run `review.py`, `final_study.py`, `cheek_review.py`, `eye_evidence.py`, `flank_stats.py` and `assessment_metrics.py`. The earlier 8A gallery is used only for the preceding-eye comparison. `walnut_sides.py . parent A` and `plot_bilateral_eye.py . parent A` reproduce the side studies.

## Frozen hashes

| Output | SHA-256 |
|---|---|
| Model | `de181485ddcc8e4e0fe65790eee5fb3933175574590eb6bbd50133400951093a` |
| Gallery 54° | `3ef8c9b196cd97ee00e82d41b57831f5d3f0ab71dafa1bac9077ea04b361f883` |
| Gallery side | `7acfe5a45353057a14d63d43c7e253d0668c69ba1a5b04998c4d19d16abe5d27` |
| Packed pigment | `86debdcce4b5b6075ae7510cb25f77066ae912cfb8e1a0c4a49101ed43b79978` |

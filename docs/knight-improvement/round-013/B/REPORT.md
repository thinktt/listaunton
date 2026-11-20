# 13B · eye and cheek

The near and far eyes each have a shallow domed face with a short crescent below it. The upper lid casts a longer shadow. The lower cut rises into the cheek and opens out toward the nose. Both flanks use the same carving in the unposed head frame.

## Physical results

Across 65 transverse sections per flank, the near lower rim has a median recess of 0.00895 model units, down from 0.02006. The far lower rim measures 0.00998, down from 0.01964. The deeper upper crease retains 0.03023 and 0.03014 on the near and far sides. The sections are measured against a 0.070-unit chord through the surrounding wood. The photographs establish the appearance of the cut and cannot determine its physical depth.

Each eye is one closed shell with 14,082 vertices. The surface tapers from 0.119 units of thickness to 0.035 units at its buried perimeter. Native checks found zero nonadjacent crossings in 28,160 triangles per eye and 20,880 triangles of adjoining skull. The exposed outlines on opposite flanks overlap by 98.86% on the 0.006-unit ray grid. The 95th-percentile left/right difference in exposed surface depth is 0.00305 units.

## Registered comparison

| Measure | Original | Black 2 | 12B parent | 13B |
| --- | ---: | ---: | ---: | ---: |
| Middle 80% of lower-lid reflection | x483–525 | x483–525 | x493–511 | x486–517 |
| Lower-lid reflection peak | x498 | x495 | x504 | x495 |
| Nose-side share of the reflection inside the eye | 53.7% | 32.0% | 9.5% | 36.6% |
| Brightest point inside the eye | (536, 482) | (504, 473) | (508, 487) | (512, 478) |

The lower reflection is broader and softer below the eye. Its nose-side end falls eight pixels short of the references at the 90th percentile. The brightest interior glint sits eight pixels farther right and five lower than Black 2. Across the whole inner-eye crop, luminance error against Black 2 rises from 13.96 to 15.00 on the 0–255 scale. This choice retains the clearer nose corner and gives the lower lid a gentler silhouette from the side.

The lens uses barycentric interpolation of the previous walnut UVs and satin finish, followed by a local blend with the billet directly below the eye. The two dedicated eye islands and their two-texel bleed account for all 8,017 modified texture pixels in the 3,072-pixel-square atlas. Median eye pigment changes from RGB (68, 34, 13) to (76, 39, 19). The two existing eye-reflection softboxes were repositioned and resized to follow the changed surface normals. The common-parent-light sheet shows the carving before those lamp adjustments. Moving-light sheets and clay sections give independent views of its relief.

The source has a finer lower reflection. In 13B it remains a broad, slightly broken patch when enlarged. At portrait scale, the upper rim also shows a few small grain changes at the old eye-island boundary. Four exposed near-side triangles and 46 far-side triangles span more than four texels. They cover 0.14% and 1.33% of the respective exposed surfaces. All UVs lie within the inherited eye atlas bounds and all exposed faces have positive UV area.

## Delivery

| File | SHA-256 |
| --- | --- |
| Parent scene | 739bf4c1e3671770de868593ec10135c5345417bd80c043ee04ee7dea86efe4c |
| knight.blend | 213c6597a98fe98057778838b953b23321af65e5f5b758e99e97d5846f6ad253 |
| wood.png | 58a5cc4ef7a2b57faacc38b8236662090483431eb4156775fa0ccd0eb2b7adb7 |
| wood-side.png | 61007b0bd24e92d5b6e03c6d0aa77ada62fb7b50316656d89139fcbfedefbd69 |
| Parent 12B pigment | 1e35b27f1eea257ee9bacc6ae60aa26cbeaf80fad5139365d58be1db395dd78b |
| pigment.png, packed as wood-atlas-improvement-013-B.png | 71260879e1f471d7c40bafe1599318181beba8f880e6c5bcb784d2a08a701ff3 |

Both registered renders came from the reopened frozen model at 144 samples. At alpha 128 both silhouettes are pixel-identical to the inherited renders. Measured physical height is 5.089041 units for both versions. The private viewer export in `review-copy` passes the repository validator for geometry, bounds, normalized normals, camera, component count and eye seating. Run `reproduce.ps1` with Blender 5.2 and the bundled Python in a copy of this directory at the same depth beneath the staging root. `proof.json` records the hashes of the frozen outputs and scripts. Blender may assign fresh internal IDs when the editable scene is rebuilt.

The side portraits, front and rear walnut, sixteen-angle clay turn, common studio comparison and registered 80-pixel board view accompany the original scene and its two reference renders.

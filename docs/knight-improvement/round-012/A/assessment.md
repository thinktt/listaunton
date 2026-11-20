# Round 12A hanging mane

The carved joint now follows the curve in the original black sprite and black candidate 2. On eight fixed-camera sections between rows 460 and 628, the first visible neck surface averages 3.25 pixels from the black-2 hollow. The released 11B joint averaged 47 pixels. Both the mane and the neck intersect every reference ray in this set. In 11B the neck reached three of the eight rays.

The narrow inside bevel turns into a continuous curved recess. The adjacent blade face uses a convex section through the old shoulder, and the neck expands underneath the blade on both sides. The median physical depth of the recess, measured against a 40-pixel chord across it, rises from 0.0233 to 0.2038 Blender units. The comparison uses the deepest ray within 16 pixels to the left and 17 to the right of the source trace. The carved opening sits up to seven pixels to the rear of the source shadow in the upper half. Its deepest walnut shadow occurs three pixels to the rear when averaged across the study.

| Fixed rendered brightness, 0–255 | Rear face | Inner face | 20 px before hollow | At source hollow | Neck |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original | 31.4 | 21.3 | 23.6 | 9.1 | 41.6 |
| Black 2 | 39.3 | 24.9 | 27.4 | 8.6 | 54.7 |
| 11B | 34.8 | 26.3 | 25.2 | 35.7 | 50.4 |
| 12A | 21.5 | 27.8 | 26.2 | 14.1 | 59.9 |

The first two columns sample equal fractions of the entire reference mane width, from its back to the cut. The last three use fixed offsets around the hollow. Black 2 carries more light on the broad rear plane. On 12A the dark cut is conspicuous at the same board-scale location, but the forward part of the blade still reads a little brighter than its back. The actual side has a narrower blade and a fuller neck. Its upper return below the ear is more pronounced under the matched side studio. The lower point remains seated when viewed from either rear quarter.

The material uses the inherited all-around walnut figure. A broad stain grades from the front toward the back of the hanging mane and fades through the ends. The opposite side gets 58% of the near-side stain strength. The grade uses three native billet coordinates. It changes 406,812 of the 3072 × 3072 atlas texels and zero texels within other parts’ UV islands. All studio lights, cameras, both eye meshes, both swept ears and the pedestal match the parent. The head ahead of rest-space x=0.24 has zero measured displacement. The maximum bidirectional nearest-vertex difference on the poll above z=4.64 is 0.00047 Blender units.

The native mane’s evaluated lateral span narrows from 1.1152 to 1.0056 units. Its extreme front, back, top and bottom coordinates are preserved to five decimals. The full registered silhouette overlaps 11B at 99.90%. Its left edge moves outward by an average 1.47 pixels across rows 445–659, with a maximum of seven pixels. The silhouette overlap with the original slips from 98.37% to 98.29%.

The evaluated mane, continuous skull and neck, and both ears each passed the test for nonadjacent self-intersections. The separate blade and neck intentionally overlap along the seat. A 0.01-unit opposed-ray grid returned zero enclosed gaps on either flank. Its mean near/far outer-depth difference is 0.0962 units versus 0.0908 on the parent. The WebGL export verified 244,690 triangles, 136,046 vertices, unit corner normals, finite UV coordinates and one finish byte per exported vertex. The reopened scene’s active packed image matches the supplied pigment byte for byte.

## Files

- `knight.blend` is the frozen editable scene. Its SHA-256 is `468df802932b0c97d716c913b2fadb9c6e1aa367756cd43ad411fe383573cf9d`.
- `wood.png` and `wood-side.png` are the reopened 144-sample studio renders. Their SHA-256 digests are `beea4f6157ceb3ec981fd7eb9490df39f9fe6121aeb1303999da690ec02a151b` and `acd7b2592168f7a58dd9a1e77f89e8be8727d2cfab2f886d6fef5ddac9391c97`.
- `pigment.png` is the packed walnut atlas, SHA-256 `2ead7436dfb7897c982f4676f461bbd8adf32905cdd7230c13493de3379b0ff5`. The public export data are in `web-export`.
- `comparison.png` and `board.png` show the full-scale and 100-pixel reference comparisons. `source-study.png`, `fixed-study.png` and `side-study.png` show the carved area. `diagnostics.png` compares the two models under identical clay and walnut studios. `turns.png` shows the flanks and rear.
- `assessment.json`, `parameters.json`, `protected.json`, `stain.json`, `bilateral.json`, `self-intersections.json` and `skull-intersections.json` contain the numerical checks. The input model is `parent.blend`, SHA-256 `c4e629d930d907d77885c01dd430cab58e99e26a26e04b63d2a36b373ecdac58`.
- `reproduce.ps1` runs the production and review scripts. Use it in a copy of this directory at the same staging depth. The measurements and comparison use the black sprite and black candidate 2. The two profiles and rear views come from the saved geometry.

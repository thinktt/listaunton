# Pawn shared base 001

This checkpoint starts from the accepted side-quality pawn at `fe7d95f`. The sole, foot, single groove, flared shoulder, socket and first stem support come from queen 033 and king 017. A uniform scale of 0.814100 fits those 40 rings to the pawn. The upper stem narrows to a lower waist, and the shallower ball dome keeps the seat near the collar in the original Lichess view. [Visual study](index.html)

## Dimensions and projection

All trials use the saved orthographic camera at 54° above the board, the original foot plane and the existing sprite registration. Foot diameter and total height are measured from the subdivided mesh in Blender units.

| Geometry | Foot diameter | Total height | Black sprite silhouette overlap |
| --- | ---: | ---: | ---: |
| Previous pawn | 1.654 | 2.775 | 98.50% |
| Shared turning at previous dimensions | 1.654 | 2.775 | 96.05% |
| Foot widened 3.5% | 1.711 | 2.775 | 96.68% |
| Foot widened 3.5%, height reduced 2.8% | 1.711 | 2.697 | 95.43% |
| Foot widened 6.0%, height reduced 5.5% | 1.753 | 2.622 | 92.35% |
| Accepted, with a refitted upper piece | 1.700 | 2.725 | 96.62% |

The accepted foot is 2.8% wider and the piece is 1.8% shorter. Strong shortening moved the top of the ball six native pixels below the original. The accepted dome brings that difference down to 1.22 pixels. The average vertical errors at the front collar and bottom edge are 0.71 and 0.17 pixels. The front socket transition and groove are still 4.39 and 3.99 pixels too low. These last two measurements follow visible brightness transitions, so both material and shape affect them. [All nine geometry trials and the lighting fit](measurements.json)

The reviewer compares the true level profiles at equal foot diameter. After undoing the uniform scale, the greatest distance between the finished pawn and king meridians is 0.00000017 donor units. For the queen it is 0.00135, about 0.065% of the foot diameter. The queen uses a denser lathe. Reopening the pawn confirmed one connected, closed mesh with 66,432 triangles. Both side cameras and the 54° camera use the same editable object. [Geometry checks](donor-check.json)

## Wood and lighting

The camera-facing lights are fitted from measured Cycles responses on the new turning. The original sprite supplies 72% of the body color target and 45% of the head target, with the remainder from black candidate 2. The side studio retains the accepted lighting and the wood, relief, varnish and slope maps remain attached to the surface. [Lamp settings and powers](light-powers.json)

Native mean absolute RGB error on common foreground fell from 16.81 to 14.77 on a 0–255 scale. The earlier model fits the brighter high-resolution candidate more closely. Mean error against that candidate changed from 3.20 to 13.53 on the head, 4.42 to 16.43 on the collar and stem, and 3.56 to 25.51 on the base. The new model has 96.08% silhouette overlap with candidate 2. The viewer keeps both references available. [Source comparison](source-comparison.png)

## Side assessment

| Quality at a level view | Weight | Previous | Accepted |
| --- | ---: | ---: | ---: |
| Profile and proportions | 30% | 79 | 83 |
| Turned details | 15% | 69 | 88 |
| Wood continuity | 20% | 70 | 70 |
| Surface finish | 15% | 71 | 71 |
| Lighting and form | 15% | 87 | 86 |
| Seating and presentation | 5% | 87 | 88 |
| **Weighted visual rating** | | **76.10** | **80.05** |

These are artistic ratings. The wider sole and single-groove turning read as part of the same set as the king and queen. Broadening the foot further makes the ball look undersized. The horizontal band on the shoulder and stippled highlights still interrupt the grain, and the groove has less contrast than on the two donor pieces. [Level base comparison](donor-bases.png)

## Reproduction

Run from the repository root. The source model and donors are hash-pinned in the proportions file. The original queen 033 is also available as `abc7281:models/queen/queen-rebuilt.blend`. The lighting replay applies measured powers directly.

```sh
study=docs/pawn-shared-base/iteration-001
blender -b --python-exit-code 1 --python scripts/pawn/build_shared_base.py -- "$study/proportions.json" refit-balanced
blender -b --python-exit-code 1 --python scripts/pawn/light_shared_base.py -- "$study/lighting.json" --replay "$study/light-powers.json"
python3 scripts/pawn/audit_mission.py ../pawn-shared-base/balanced-light --previous history/pawn-side-quality-003/render.png
blender -b --python-exit-code 1 --python scripts/pawn/deliver_mission.py -- ../pawn-shared-base/balanced-light
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
blender -b --python-exit-code 1 --python scripts/pawn/validate_shared_base.py -- "$study/proportions.json" build/pawn-shared-base/donor-check.json
python3 scripts/pawn/compare.py
python3 scripts/pawn/contact_sheet.py
python3 scripts/pawn/build_side_comparison.py
python3 scripts/pawn/build_viewer.py
python3 scripts/build_candidate_pages.py --piece pawn
python3 scripts/build_set_comparison.py
```

To repeat the full study, omit the `refit-balanced` argument in the geometry command. Run `compare_shared_base.py` with the proportions file, the output directory `build/pawn-shared-base/final-comparison` and `--lighting-target` to prepare the registered original. The light-fitting script can then estimate the powers anew. After delivery, repeat the comparison command and run `scripts/pawn/shared_base_plates.py` to draw the level and source studies.

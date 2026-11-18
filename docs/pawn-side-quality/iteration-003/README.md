# Pawn side study 003

The stem now widens smoothly into the underside of the collar. In a level render at 1,254 pixels, the narrowest section moved from row 500 to row 537 and its width went from 198 to 192 pixels. The ball still seats directly in the collar. The model measures 2.77485 units tall and 1.65357 across the foot. Seven control rings shape the stem. A wider shoulder trial broke up the foot reflection and was discarded.

The side studio now gives the ball three feathered highlights. The fixed reconstruction camera is still 54° above the board. Its original 47 lamps illuminate the same editable pawn and wood as both side cameras.

## What the side guide shows

The sole in the imagined guide curves downward at its center. Fitting a horizontal circle to that visible arc gave elevations of 11.5–12.0° across three horizontal spans. A second fit to the dark groove just above it gave 11.1–11.8°. The added 11.5° portrait uses that estimate. The actual camera in the generated image is unknown. The level side camera remains available for judging the lathe profile. Both photographs register independently to the guide by foot width and floor height with a single uniform scale. [Arc fits](guide-elevation.json) · [Side views](side-comparison.png)

## Visual assessment

| Criterion | Weight | Previous | Current |
| --- | --- | --- | --- |
| Profile and proportions | 30% | 70 | 79 |
| Turned details | 15% | 64 | 69 |
| Wood continuity | 20% | 70 | 70 |
| Surface finish | 15% | 70 | 71 |
| Lighting and form | 15% | 82 | 87 |
| Seating and presentation | 5% | 85 | 87 |
| Weighted judgment | | 71.65 | **76.10** |

The new cove gives the collar a clear underside. A broad cylinder still interrupts the shoulder. The three reflections describe the ball more clearly. The front of the base still has a pale band and a dark grain break. These also appear in the unlit pigment and read differently as the pawn turns. The rear grain looks softer. Material continuity remains the largest challenge. [Four level views](orbit-sheet.png)

## Fixed-view checks

At native size the mean black-sprite color error is 16.81 on the 0–255 scale, previously 16.67. Its silhouette overlap is 98.50%. White-sprite overlap is 98.14% and selected black candidate 2 overlap is 96.81%. All three head glint centers stay within one original pixel. The selected high-resolution errors for head, collar/stem and base/foot are 3.20, 4.42 and 3.56, compared with 3.20, 3.41 and 3.36 previously. A small brighter area under the right side of the collar is visible at high magnification. [Fixed-view crops](comparison.png) · [Native-size comparison](native-comparison.png)

The saved model reopens as one closed, editable mesh with 57,984 evaluated triangles. The wood maps are byte-identical to checkpoint 002. The side lighting and profile are genuine scene changes. The browser uses the exported mesh for rotation and the saved Cycles photographs for the reference and side comparisons. [Model checks](scope-validation.json) · [Measurements and ratings](checkpoint.json)

## Rebuilding

From the repository root, run the checkpoint with Blender, then regenerate the comparison and viewer in order.

```sh
blender -b --python-exit-code 1 --python scripts/pawn/accept_side_material.py -- docs/pawn-side-quality/iteration-003/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
python3 scripts/pawn/compare.py
python3 scripts/pawn/contact_sheet.py
python3 scripts/pawn/build_side_comparison.py
python3 scripts/pawn/build_viewer.py
python3 scripts/build_candidate_pages.py --piece pawn
python3 scripts/build_set_comparison.py
node scripts/pawn/check_viewer.cjs
```

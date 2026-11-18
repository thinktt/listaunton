# Side checkpoint 001 — readable side studio

Date: 2026-11-18. The owner asked for a high-quality pawn side view, informed by
standard Staunton examples, while preserving the successful reference match.
The new goal is active. This is an intermediate presentation improvement;
the requested quality level has not been reached.

## Accepted change

The Blender file now contains a separate `Pawn side studio` scene. Both scenes
share the exact same editable pawn object, geometry, UVs and wood material.
The original scene keeps the fixed 54-degree camera, world and all 47 lights.
The side scene uses a level camera, three photographic area lights and two
diffuse-only fill cards. The fill separation is an artistic lighting choice.
The profile is rendered at 1254 × 1254 rather than 640 × 640.

The public reference image, rotating mesh and side comparison use this saved
model. The side comparison explicitly identifies its studio lighting. Live
WebGL lighting remains approximate. Generated side guides and gallery size
defaults are unchanged.

![Before and after, same geometry and material](side-before-after.png)

## Side-quality assessment

These are subjective aesthetic scores under the rubric in the parent document,
not measured reconstruction probabilities. Lighting earns no geometry credit.

| Criterion | Weight | Before | Current |
| --- | ---: | ---: | ---: |
| Profile and proportions | 30% | 68 | 68 |
| Turned details | 15% | 60 | 60 |
| Wood continuity | 20% | 48 | 48 |
| Surface finish | 15% | 62 | 62 |
| Lighting and form | 15% | 52 | 82 |
| Seating and presentation | 5% | 75 | 85 |
| Weighted score | 100% | **59.85** | **64.85** |

The working rounded assessment is **65/100**, with a holistic range of 60–70.
The target remains at least 90 overall with no category below 85, subject to
visual inspection and preservation of the original view. Do not round this
checkpoint up to a finished result.

Remaining problems are the bulky base/socket profile, the pinched groove,
the abrupt grain/color transitions on the front of the head, upper stem and
lower flare, and uneven varnish detail. The original view fit previously hid
some of these shortcomings. The rear is materially more coherent than the front.

![Same material and studio inspected around the pawn](orbit-sheet.png)

## Reference preservation

The evaluated mesh, smooth normals, UVs and exported mesh bytes are unchanged.
The pawn remains one closed component with Euler characteristic 2 and positive
volume. The source sprite pixels, selected black candidate 2, framing and 54°
camera remain unchanged.

Compared with checkpoint 017, the fresh reference render's alpha is identical.
Mean absolute foreground RGB change is **0.000033/255**, with a maximum of one
code value from render variation. Silhouette overlaps remain 96.8107% against
the selected enlargement, 98.4992% against original black and 98.1358% against
original white. Native original RGB error remains 16.67/255. The collar's front
highlight remains at approximately 2.96/255 luma error and 0.890 fine correlation.
These preservation checks do not imply a perfect original match.

The saved model SHA-256 is
`ba243990f54a0444f94852667dd8335b7f9b177dde97ec8ccd42749f55bf1536`.
The previous checkpoint-017 file remains archived and unchanged.

## Rejected experiments

- Filling the base groove and compressing the base improved isolated side
  features but displaced or weakened the selected view's turning and glints.
- A thinner lower collar looked more deliberate in profile. Close inspection
  exposed a front-highlight regression: luma error rose from 2.96 to 15.26 and
  fine correlation fell from 0.890 to −0.203. A local reflector fit and a ray-based
  re-aim did not recover the accepted feature. The collar edit was discarded.
- Conservative hidden-wood completion preserved the original pixels but did
  little for the visible side artifacts. Extending reference-derived grain into
  the hidden wood created new stretching and pattern inconsistencies. Neither
  those color maps nor the matching relief experiment enters the accepted model.

Configs, comparisons and measured failures are in `rejected/`. Third-party
research photographs remain in the private cache; `research-sources.json`
records their URLs and hashes. They are not public textures or new ground truth.
The experimental completion scripts used a preexisting depth/meridian cache;
regenerate those measurements from the archived model before another attempt.

## Reproduce and validate

From the repository root, run Blender in background with:

```text
blender -b --python-exit-code 1 --python scripts/pawn/rebuild_side_checkpoint.py -- docs/pawn-side-quality/iteration-001/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
```

The rebuild asserts the allowed controls, full shader graph and color ramps,
packed image hashes, unchanged reference lights, saved camera and shared studio
object, then reopens the file and renders both scenes. `scope-validation.json`
records the verified scope. The final configuration makes no control edits.

Rebuild `scripts/pawn/build_side_comparison.py`, `scripts/pawn/build_viewer.py`,
the pawn candidate page, and the current whole-set comparison page. Run the
pawn viewer, model-site, lineup, height-mode, whole-set and affected comparison
checks. These JavaScript checks use a mocked GPU; they do not establish native
browser shader quality. Inspect the actual Blender images as recorded here.
Keep the canonical repo and existing Windows preview synchronized.

The pawn viewer, model-site, current-model lineup, height modes, board,
proportion-warping and candidate interaction checks pass. The whole-set
presentation check also passes. Its stricter historical measurement check
finds a pre-existing knight mismatch: the current mesh/camera hashes differ
from the side-gallery measurement record. Those knight files and the sizing
record are byte-identical to their pre-checkpoint Git versions. They are left
unchanged; this checkpoint does not recalculate or change any gallery sizes.
The full failure and separate passing presentation check are recorded in
`site-checks.json`.

Next investigate pigment/illumination separation at the front-side texture
boundaries. Preserve this paired-scene setup so future form/material comparisons
use consistent side lighting and still guard the reference view.

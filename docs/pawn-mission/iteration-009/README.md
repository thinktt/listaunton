# Pawn checkpoint 009

Accepted on 2026-11-12. Trial 042 refines the walnut finish from checkpoint
008 (`db3222d`). The fine grain in the flare and foot reflections is clearer.
The ball-to-collar reflection remains unfinished.

## Measured finish

Nine real Cycles renders sample combinations of roughness and polish strength.
A second render seed estimates noise. The bounded fit modifies finish only
where the response exceeds that noise. The new packed map uses red for
roughness and green for polish strength. It modulates the real Principled
wood and coat, preserving the existing groove mask.

| Reflection | Fine contrast before / after / selected | Pattern correlation before / after |
| --- | --- | --- |
| Upper head | 17.6 / 19.6 / 18.4 | 0.800 / 0.824 |
| Left flare | 17.7 / 22.4 / 29.4 | 0.786 / 0.870 |
| Narrow flare line | 17.9 / 20.3 / 29.4 | 0.372 / 0.742 |
| Foot line | 17.1 / 22.7 / 30.4 | 0.789 / 0.903 |

Contrast is the RMS of the same small-scale brightness residual used at
checkpoint 008. More contrast alone is not better. These reflections also
move closer to the selected pattern. See `fine-detail.json`.

The head, collar/stem and base/foot common-foreground RGB errors are
3.43, 3.65 and 4.00 on a 255-level scale. Native original error changes
from 16.37 to 16.40, a small tradeoff. The three head glint centers remain
within 0.90 original pixels. The high-resolution reference itself differs
from the original by 15.74 RGB levels using that native comparison.

## Reflection experiments

The black-material diagnostic isolates the light returning from the collar
onto the lower ball. Secondary paths account for most of the unwanted pale
edge. Trial 043 removes secondary glossy bounces. The pale line disappears,
but the lower ball becomes too dark. Its contact-profile RMSE increases
from 7.16 to 13.65. Trial 044 re-estimates diffuse pigment under that lighting,
but only reduces the error to 12.83. Both are rejected.

The accepted scene retains four diffuse and four glossy bounces. It retains
the same 44 lights, world, pigment and normal map as checkpoint 008. The
rejected pigment map and ray-depth settings are not used by the review.

## Assessment and remaining defects

| Category | Checkpoint 008 | Checkpoint 009 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 90 | 92 |
| Lighting | 90 | 91 |
| Working mean | 92.16% | 92.76% |

The four visual ratings are judgments. Holistic range is 90–95%.
Original black and white IoU remain 98.50% and 98.14%. The selected
enlargement's narrower rear flare still conflicts with both originals.
The model follows the originals there.

The pale line under the ball, the collar's over-bright mottling, left stem
reflection and socket highlight shape remain visible differences. Fine
grain on the flare is still weaker than the selected detail reference.
The back uses broader inferred grain. Four-angle studio and neutral-light
renders check the mapped finish away from the fitting camera.

The mission remains incomplete. Next constrain the ball/collar reflection
without the global darkening seen in the rejected ray-depth trial.

## Rebuild and verification

From the repository root, using Blender 5.2.2 and Python with NumPy/Pillow:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/apply_finish.py -- docs/pawn-mission/iteration-009/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate_finish_scope.py -- docs/pawn-mission/iteration-009/reproduction.json models/pawn/pawn-rebuilt.blend docs/pawn-mission/iteration-009/finish-scope.json
```

The first command rebuilds trial 045 from archived checkpoint 008 and the
tracked finish map. It does not replace accepted assets. The second checks
the current accepted model. `finish-calibration.json`, `finish-estimate.json`
and the fitting scripts record how the finish was inferred.

The reopened render and independent replay retain identical alpha and
differ from the inspected trial by at most one RGB level. The closed
57,984-triangle mesh, normals and UVs are unchanged. Packed texture pixels,
shader channel connections, original groove masks and all lights are checked.
The viewer includes the same finish map and an approximate lighting model.

Code-based page checks exercise camera registration, texture hashes, orbit,
pan, zoom, reference switches and side comparison. Native browser screenshot
verification was blocked because browser automation does not permit the
local file URL. No alternate browser path was attempted.

Repository site, model-page, candidate-interaction and pawn-viewer checks pass.
The full-set check reaches the separate knight height-metadata mismatch
already recorded at checkpoint 008. The pawn's archived height source is
unchanged. See `site-checks.json` for complete outputs.

# Queen checkpoint 31 — flatten the join under the bottom collar

The bottom collar already had a rounded bead, but its connection to the stem
still formed a conical underside. This checkpoint raises only stem controls
48 and 49 by 0.01275 and 0.085 units. The bead, all radial controls, socket
shelf and steep drop, base, crown and seated egg remain unchanged. The gap
from control 49 to the bead's bottom drops from 0.11530 to 0.03030 units.

Source checkpoint 29 is preserved in `history/queen-mission-029` with hash
`441f40d2ef07e5bf6c5f14380c2d7ba71c94172add6c1891da9eb399907ecea0`.
The new active model is
`f6cbac79d43ce1e894f498340da4ebb0700c87dd44d0845cf0bab56e13310442`.

## Comparison and decision

Both 0.050 and 0.085 join lifts preserve the elevated alpha outline exactly
relative to their production-subdivision Workbench control. The stronger lift
is accepted: it makes the collar read as a rounded plate sitting on the stem
with less of the flaring underside. `collar-join-sheet.png` shows identical
side framing. Actual Cycles wood/clay renders confirm the result. Final saved
renders use 256 fixed samples, denoising and no light tree, as before.

| Metric | Checkpoint 29 | Checkpoint 31 |
| --- | ---: | ---: |
| Original black outline IoU | 97.8523% | 97.8523% |
| Selected high-res outline IoU | 97.9622% | 97.9622% |
| Interior/side shape, subjective | 87% | 88% |
| Wood color, subjective | 85% | 85% |
| Grain/texture, subjective | 79% | 79% |
| Lighting/reflections, subjective | 76% | 76% |
| Equal-weight working mean | 84.9705% | 85.1705% |

The holistic estimate remains 80–85%. The form increase reflects the side
join, not proof of recovered hidden geometry. Both original colors were
inspected; white remains a secondary shape reference, not a matched finish.
Height 4.393650, base diameter 2.089251, their 2.102978 ratio, and gallery
defaults remain unchanged.

## Coupled base study — rejected, not published

Coherent 6%, 10% and 16% compression of the foot, flare and socket was tested
with a bounded radial refit weighted 80% original and 20% selected reference.
Draft original/selected IoUs were 97.7830/98.0017, 97.7773/97.9879 and
97.7516/97.9722. This recovers much of the exterior fit lost in earlier
Z-only tests, but the good scores conceal an interior mismatch.

The actual 10% Cycles trial moves the socket's front lip downward relative to
both references and weakens its bright crescent under the retained lights.
`compact-material-socket.png` compares identical pixel coordinates. The 16%
draft also emphasizes an extra step near the flare's lower rim. Neither
replaces the accepted shelf/drop construction. `compact-base-sheet.png`
records the shared-scale bracket, `rejected-base-90.json` the 10% proposal,
and `rejected-255-validation.json` its passing topology check. The rejection
is visual. Failed models remain under ignored `build/`.

## Reproduction and validation

```sh
blender -b --python scripts/queen/study_compact_turning.py -- \
  --source history/queen-mission-029/queen-rebuilt.blend \
  --expected-source 441f40d2ef07e5bf6c5f14380c2d7ba71c94172add6c1891da9eb399907ecea0 \
  --variant 254-rounded-collar-join --join-lift 0.085 --samples 32
```

Validate with `validate_side_shape_iteration.py` and recorded `profile.json`,
then use `publish_side_shape_checkpoint.py`. The composed profile is relative
to checkpoint 22; the two-control delta is from checkpoint 29.

The saved mesh has zero boundary/non-manifold edges, positive volume 4.521449,
six exact receivers, 715,776 render triangles and 82 verified receiver links.
Separate checks preserve packed image bytes, shader graph, 85 lights, camera
and world transform. The viewer exports the same editable control mesh
(44,924 triangles) and saved 54-degree camera; Cycles uses its subdivision
surface. Browser lighting remains approximate. Fixed/side renders, registered
comparisons and viewer are rebuilt together. The camera/reference interaction
checks use the existing simulated DOM/WebGL harness; site checks and source
hashes are recorded alongside this document.

Native in-app-browser inspection also confirms that the current rotating
viewer opens, its Side/Neutral controls work, and the Side comparison loads
the accepted render with working material and opacity controls.

## Next

The whole-base request remains unresolved. Constrain the visible socket shelf
arc and stem seat alongside the exterior contour. Keep checkpoint 31 until a
compact interpretation also preserves those internal relationships. Texture
and lighting finishing remain deferred; the goal stays active.

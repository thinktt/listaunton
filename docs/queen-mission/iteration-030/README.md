# Queen profile bracket 030 — preserve the shelf/drop

Date: November 11, 2026  
Starting revision: `ca3771b`  
Active source model: `models/queen/queen-rebuilt.blend`  
Active model SHA-256: `441f40d2ef07e5bf6c5f14380c2d7ba71c94172add6c1891da9eb399907ecea0`  
Original black reference SHA-256: `b214bd3b522122f9a6040c4fd6ed4e00b2fe9d16436bf4f52e5f155b4b190567`  
Selected high-resolution reference SHA-256: `bc510a8f5fff0a1e51fd913f1cf4f4707849d68c5d4dabc8ce6df16cc2e1423a`

## Purpose

The owner clarified that the raised socket must continue to read as a clear
horizontal shelf followed by a steep inward drop.  This bracket therefore
tests the remaining side-profile requests without smoothing, widening, or
removing that construction:

1. a micro-narrower upper collar;
2. a coherent lower-assembly compression with **no** added flare swell; and
3. a shorter exposed socket wall with the shelf radius and stem seat fixed.

These are isolated drafts, not accepted model changes.  The saved active model,
receiver partitions, Cycles lighting, material, source images, and local review
page remain checkpoint 29.

## Controls and results

The quick neutral drafts use the same saved 54-degree orthographic camera and
unchanged source registration.  They render the editable 192-sided control
surface in Blender Workbench with subdivision disabled, solely to compare shape
directions quickly.  As a consequence their absolute IoUs are **not** acceptance
metrics; the `current_control` row is the calibration control for their relative
direction.  A promoted trial would need a receiver rebuild, saved-scene Cycles
render, full validator, and the standard `compare_finished_queen.py` check.

| Draft | Change | Original black IoU | Selected high-res IoU | Decision |
| --- | --- | ---: | ---: | --- |
| current control | checkpoint-29 geometry | 97.8423% | 97.8050% | baseline for this draft renderer |
| 243 | upper collar peak radius -0.003, rings 75–81 only | unchanged exterior alpha | unchanged exterior alpha | reject: not visibly different at normal scale |
| 244 | 3% Z-only compression through ring 38; no flare bulk | 97.6846% | 97.9788% | park: selected reference improves, authoritative original regresses |
| 245 | 4% Z-only compression through ring 38; no flare bulk | 97.6222% | 97.9682% | reject: worse original fit than 244 |
| 246 | 6% Z-only compression through ring 38; no flare bulk | 97.4882% | 97.8802% | reject: visibly squat and poorer on both directions than 244 |
| 247 | socket wall 82% of its height; shelf radius/height and stem seat exact | 97.7974% | 97.8156% | reject: no meaningful selected gain and original regresses |
| 248 | socket wall 70% of its height; same fixed shelf/seat | 97.7910% | 97.8092% | reject: stronger version does not improve the source fit |

For comparison, the accepted checkpoint-29 full Cycles/source metrics remain
97.8523% original-black and 97.9622% selected-high-res outline IoU.  Its
unchanged qualitative regression scorecard is silhouette 97.8523, interior
shape 87, color 85, grain 79, lighting 76, working mean 84.9705%, and holistic
visual range 80–85%.  No candidate earns a revised scorecard because none is
promoted.

## Geometry preserved by the bracket

- The socket shelf begins at ring 29, at radius 0.56450 and height 0.94400.
- In base-compression drafts, all radii stay exact; only the Z position below
  the lower-collar handoff at ring 50 changes.
- In socket-wall drafts, every radius stays exact, the shelf ring 29 and stem
  seat ring 38 stay exact, and only rings 30–37 move vertically.  The wall top
  moves from height 1.19400 to 1.14900 in 247 and 1.11900 in 248, preserving a
  more abrupt inward transition rather than replacing it with a smooth drum.
- The crown, seated egg, collars, UVs, material, light links, camera, and
  references remain untouched by every draft.

## Visual evidence and interpretation

`base-compression-side-sheet.png` puts the current profile alongside the
3%/4%/6% no-bulk bracket.  The 3% version is the only modest alternative: it
does look slightly more compact while retaining the shelf/drop profile, but its
fixed-source tradeoff is genuine rather than an artifact of a changed crop.
`base-overlay-selected.png` and `base-overlay-original.png` show the exact same
neutral drafts over the two unmodified registered references.

The original Lichess sprite remains the deciding source.  The high-resolution
image is useful for interpreting curvature, but it is a later selected
reconstruction and cannot by itself justify moving the active geometry away
from the original.  This bracket therefore records a real ambiguity instead of
silently promoting the aesthetically tempting shorter-base result.

## Next

Keep checkpoint 29 active, including its seated egg, rounded lower collar,
subtle upper collar, lower-foot support, and explicit shelf/drop socket.  The
next shape hypothesis must address side plausibility without the observed
original-reference regression.  Texture and lighting finishing remain deferred
in this shape-focused mission.

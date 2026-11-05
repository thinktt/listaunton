# Iteration 002 — button width and flatter foot

Accepted on 2026-11-05. This is a small geometry improvement; the bishop is
still visibly different from the reference, especially in material and light.

| Metric | Previous | Accepted |
| --- | ---: | ---: |
| Selected-reference silhouette IoU | 94.88% | 96.20% |
| Interior geometry, estimated | 78% | 81% |
| Wood color, estimated | 70% | 70% |
| Grain and texture, estimated | 64% | 64% |
| Lighting, estimated | 54% | 54% |
| Arithmetic mean | 72.18% | 73.04% |

The independent original-white IoU improves from 96.58% to 97.88%; original
black improves from 95.96% to 96.75%. The mask and fixed image registration
are unchanged. The mean is a working score, not a probability of correctness;
holistic resemblance remains roughly 65–75% because the material problems
are more conspicuous than these small outline improvements.

## Changes and comparison

The original white sprite and selected white candidate 3 both put the button's
outer edge slightly outside the previous model. Trial 012 widens the button
by 8% in its horizontal plane, preserving its height and bottom. It improves
both outlines without creating a neck. Trial 013 also changes ten lower-foot
profile rings: the wall becomes flatter, the underside corner turns more
quickly, and the upper edge retains a small rounded transition into the groove.
This gives the larger outline improvement.

The flare, raised socket, stem, all three collars, head curve, slit, image
registration and 54-degree camera retain their previous control coordinates.
Overall model height remains exactly 4.592006683349609 units. Evaluated base
diameter increases by about 0.124%, from 2.009791135787964 to
2.0122909545898438 units; there is no global rescaling.

The pigment projection is recalculated for the changed surfaces, then baked
again and checked after reopening the saved Blender file. The accepted
96-sample Cycles render uses real Principled BSDFs, with the same material
parameters and lighting as the previous checkpoint. No reference pixels,
generated reference choices, or camera parameters were changed.

Compare `comparison.png`, `head.png`, `base.png`, the original/selected contour
images, and the current neutral, side and rear renders. The button remains a
shallow dome seated directly on the head. The foot now has a flatter side
profile. The reference remains authoritative over the interpreted side guide.

## Validation and preservation

- Both editable components remain closed and have positive volume. All three
  full-depth slit probes and the solid-floor probe pass.
- The head has the same 2.281-degree maximum sampled normal step. Across 161
  junction sections, the surface has no gap, exposed cap or cylindrical neck.
  Button height/width is 0.413; contact width/button width is 0.839.
- Control topology, modifier settings and the Boolean cutter are unchanged.
  Control vertices match exactly the declared ring/radius edits within
  0.00000012 units. The flatter foot engages another bevel edge, so evaluated
  triangle count grows from 133,120 to 134,656; it is not claimed unchanged.
- Exported positions, unit normals, pigment UVs and the dedicated cut-face
  material pass validation. Packed and disk atlas pixels agree exactly.
- The viewer embeds the accepted mesh, atlas and fixed render. Its camera
  agrees with Blender within 0.00001 pixel for 501 sampled vertices. The
  overlay/rotation/candidate controls pass the simulated DOM/WebGL harnesses.
  This is not native browser visual inspection.
- `history/bishop-mission-001/` preserves the previous model and associated
  appearance/geometry data. The side gallery now cites this historical sizing
  source, so the owner's sizes, order and ground line do not move as details
  are refined. All sizing values remain unchanged.

The accepted main bishop page and existing local preview are refreshed together
after validation. Rejected trials stay out of the public comparison controls.
`scores.json`, `trials.json`, configuration snapshots and `reproduction.json`
record hashes and reproduction steps.

## Remaining discrepancies and next hypothesis

The reference has darker collar recesses, stronger local contrast and brighter
small glints. The current finish is too uniformly orange, with broad pale
grain bands and reflections that read as polished plastic. The foot reflection
is still too continuous; the base and button lack the reference's brightest
patches. The slot mouth and interior edge curvature also need more attention.

Next, isolate lighting: test a smaller diffuse source and lower ambient fill,
then tune the base/button reflections without lifting the collar recesses.
Keep the pigment and geometry fixed for that comparison. If light changes
cannot recover the grain's finer pattern, revisit the inferred pigment and
surface-relief model separately. Do not promote a brighter image merely
because its mean color is closer.

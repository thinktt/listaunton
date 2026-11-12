# Pawn checkpoint 015

The collar has finer reflected grain and warmer right/front highlights.
Trial 088 preserves the mesh, UVs, pigment and 54-degree camera. It changes
only the local finish/normal maps and the color/power of two existing
reflectors. The mission remains incomplete; the overall assessment stays
93.36% because visible discrepancies remain elsewhere and in the collar.

## Investigation and changes

Source isolation in study 081 covers all 44 fixtures, world illumination
and secondary glossy rays. Study 082 disables each relief layer separately,
then all three. Removing the measured fine-normal layer raises RGB error
in the worst collar patch from 14.37 to 28.41 levels. Removing every layer
raises it to 29.21. The accepted refinement retains all three layers.

The earlier collar calibration used 192 samples. Trial 083 remeasures nine
roughness/polish combinations plus an independent seed at the current
512-sample quality. Trial 084 measures seventeen normal responses and
fits both broad and fine residuals. Trial 088 makes a second, smaller-step
normal refinement under the selected light colors.

Study 085 identifies the existing right-flank and lower-glint reflectors as
the sources of the cool right/front highlights. Both the selected image
and original sprite support warmer colors there. Trial 086 fits bounded
RGB power changes using actual rendered responses; trial 087 refines the
front source after the first fit reaches its conservative red-power bound.
The fitted image is judged with a separate full render, not just the
cropped derivative prediction. All lamp positions, shapes and visibility
are preserved, and the other 42 lamps remain unchanged.

Only 0.184% of finish-map pixels and 0.230% of normal-map pixels change from
checkpoint 014. Both maps are byte-identical outside UV height 0.672-0.746,
with smooth fades over 0.672-0.688 and 0.736-0.746. The head, stem and base
maps remain intact. Roughness/polish gains remain bounded at 0.30-2.40 and
0.38-1.85. Normal slopes remain bounded at 0.135, about 7.69 degrees.
The recovery report includes unclamped proposals; the PNG encoding applies
the stated bounds. Pigment and the older pigment-driven bump are unchanged.

## Comparison and tradeoffs

| Collar patch | Fine correlation, 014 | Fine correlation, 015 | Luma error, 014 | Luma error, 015 |
| --- | ---: | ---: | ---: | ---: |
| Left | 0.837 | 0.893 | 7.48 | 6.08 |
| Right | 0.825 | 0.872 | 3.76 | 3.23 |
| Front | 0.871 | 0.892 | 3.31 | 2.86 |

Errors use a 255-level scale. The collar/stem region's common-foreground
RGB error falls from 2.303 to 2.206; head error changes from 2.665 to 2.646.
Base/foot error stays 2.724. Head, stem, socket, flare and foot reflection
pattern measurements remain essentially unchanged.

For each patch's brightest 20% of pixels, right-glint RGB/luma changes
from [1.239, 0.975, 0.808] to [1.280, 0.961, 0.797], against the selected
image's [1.280, 0.962, 0.795]. The front changes from
[1.226, 0.978, 0.815] to [1.281, 0.970, 0.776], against
[1.306, 0.964, 0.763]. These are descriptive display-color statistics,
not physical reflectance or proof of recovered historical lamp settings.
The original is warmer still; its separate measurements are retained.

Native original RGB error rises slightly from 16.61 to 16.63, while the
chosen enlargement itself measures 15.74. The head/contact profile error
improves from 3.48 to 3.45, but its darkest core rises from 6.53 to 6.64
against the selected image's 4.19. Those tradeoffs accompany the clearer
collar grain and warmer highlights; they are not hidden by the better
regional average. See `collar-detail.png`, `color-detail.png` and
`native-comparison.png`.

| Category | Checkpoint 014 | Checkpoint 015 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 94 | 94 |
| Lighting | 92 | 92 |
| Equal-weight working mean | 93.36% | 93.36% |

The four visual ratings are judgments, and the holistic range remains
90-95%. Original black/white IoU remain 98.499%/98.135%. The original's
broader rear flare continues to govern the shape where the generated
reference differs. The local gains do not yet justify raising the whole-piece
ratings or claiming a perfect match.

Remaining defects include dark gaps and coarse patches in the collar,
the lower-head reflected line, the stem's fragmented highlight, the base
groove/foot reflection, and inferred rear grain. The largest remaining
32-pixel residual is at reference x=545-577, y=930-962, around the groove
and foot highlight. Examine its profile, surface and illumination next.
Preserve the accepted collar/stem/head finish; do not reuse the rejected
trial-066 foot warming without new supporting evidence.

## Reproduction and validation

From the repository root with Blender 5.2.2:

```sh
blender -b --python-exit-code 1 --python scripts/pawn/rebuild_collar_finish.py -- docs/pawn-mission/iteration-015/reproduction.json
blender -b --python-exit-code 1 --python scripts/pawn/validate_local_surface.py -- docs/pawn-mission/iteration-015/reproduction.json models/pawn/pawn-rebuilt.blend docs/pawn-mission/iteration-015/surface-validation.json
blender -b --python-exit-code 1 --python scripts/pawn/validate.py -- .
```

The independent replay starts from archived checkpoint 014 and tracked
finish v9 / normal v10 maps, then applies the two explicit lamp-color rows.
`checkpoint.json` records actual saved-file and replay pixel comparisons.
The scope validator checks the full shader graph, prior relief, pigment,
packed maps, mesh positions/geometric normals/UVs, camera, world, ray
depths, sampling and lamps. Only the listed lamps' energy/color may differ;
their other properties and every unlisted lamp must match. The previous
unchanged-light checkpoint also passes this extended validator.

The fixed wood/clay renders, side comparison and rotating assets are
rebuilt from the same saved model. Four-angle studio and neutral-light
inspection is in `orbit-check.json`; site checks are in `site-checks.json`.
Original source pixels, registration and gallery defaults are preserved.
Native browser GPU appearance remains unverified after the earlier local-file
policy rejection; no alternate route was attempted. The interactive viewer
uses the matching maps with approximate lighting, not the full Cycles rig.

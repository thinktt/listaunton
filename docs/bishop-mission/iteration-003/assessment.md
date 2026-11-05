# Bishop iteration 003 — measured boxwood color and warmer reflections

Starting checkpoint: `4c3188f`, preserved in `history/bishop-mission-002`.
The control geometry, modifiers, deep slit, button contact, dimensions,
reference registration and 54-degree orthographic camera remain fixed.
White candidate 3 is still the selected detail reference; the original
white Lichess sprite remains authoritative. No source image was edited.

## Findings and changes

The previous render was too uniformly orange and pale across the collars,
with broad white reflections and coarse, marbled grain. The target has
darker recesses, fine grain, warm bright highlights and more regional color.

Reflection locations now use interpolated shading normals rather than flat
triangle normals. The difference was about 3.7 degrees at the base and changed
the inferred reflector height appreciably. This is a reconstruction of the
lighting, not evidence of the original rig. The broad key stays soft; a harder
key was rejected because it made the left-side shadows too harsh.

The display transform changed from AgX with Medium High Contrast to Standard
sRGB. A swatch check verified Blender's actual PNG export against OCIO,
including the Look. AgX inverse fitting failed to reproduce some saturated
gold colors and produced patchy confidence transitions. The Standard inverse
round-trip error on the supplied reference is below 0.000018 per channel.
This is an artistic/rendering choice, not a claim about Lichess's renderer.

Measured black and white BSDF renders estimate how the current surfaces
respond to pigment. Their difference supplies a bounded inverse pigment fit;
an actual-render feedback step compensates for part of the interreflection
error. Strong reflections, clipped channels, unreliable inverse colors and
silhouette edges are excluded. Visible-surface confidence blends into the
previous hidden wood. Pigment and confidence use separate linear EXRs during
fitting; only pigment is baked into the final 2048-square UV atlas.

A first Standard fit clipped red albedo in 23.55% of confident pixels, causing
greenish rims. Diffuse illumination was increased threefold and the starting
pigment reduced to one-third. This gives the inferred pigment headroom without
raising the glossy lamps. The final bounded fit removes that clipping artifact.
The cut interior retains the same diffuse-energy balance.

The final scene uses actual Principled BSDFs and packed pigment, with the
previous independent microrelief. Diagnostic emission passes only measure or
bake pigment; they never serve as beauty renders. Unused fitting nodes/images
are removed from the saved scene. The image remains a genuine 3D render.

## Scorecard

| Metric | Previous | Current |
| --- | ---: | ---: |
| Outside silhouette and placement | 96.20 | 96.20 |
| Interior shapes and carved details | 81 | 81 |
| Wood color and tonal variation | 70 | 84 |
| Grain pattern and surface texture | 64 | 77 |
| Lighting and reflections | 54 | 64 |
| Equal-weight working mean | 73.04 | 80.44 |

Only silhouette is measured IoU. Other values are subjective visual judgments;
the mean is a progress indicator, not proof or probability of fidelity.
Fixed-view holistic appearance is approximately **75–85%**. No claim of a
perfect match is made. The exact final metrics, hashes and render settings
are in `scores.json` and `checkpoint.json`.

The color gain comes from the collar/stem contrast, amber tone and base
markings. Grain is finer and closer to the selected image, although the relief
still comes from the earlier inferred source. Warmer glints and better
placement improve lighting; their shape and extent remain visibly different.
Neither geometry category is increased for a material-only change.
The shared foreground's mean absolute RGB difference drops from 27.56 to
7.93 on an 8-bit scale. This diagnostic excludes the background and boundary
pixels; it combines color, shading and shape error and is not a fidelity score.

## Trials and decisions

All trial scores below use the same five-category order: silhouette, interior,
color, grain, lighting. Small outline differences are sampling noise; no
geometry changed. Rejected variants are not choices on the public page.

| Trial | Scores | Decision and visible evidence |
| --- | --- | --- |
| 016 directed diffuse | 96.20 / 81 / 67 / 64 / 50 | Reject: left-side shadows too hard. |
| 017 brighter glints | 96.20 / 81 / 68 / 64 / 56 | Hold: brighter button/base, but cool, smooth highlights and pale collars. |
| 018 shading-normal placement | 96.20 / 81 / 68 / 64 / 57 | Useful placement step; color still wrong. |
| 019 warm glints | 96.20 / 81 / 69 / 64 / 60 | Useful lighting source; still too pale and smooth. |
| 020 AgX measured pigment | 96.20 / 81 / 68 / 62 / 60 | Reject: visible patches from unreliable inverse colors. |
| 021 Standard calibration | 96.20 / 81 / 73 / 64 / 62 | Useful display/light response; not a finished pigment fit. |
| 022 Standard measured pigment | 96.20 / 81 / 77 / 73 / 62 | Reject as final: greenish base/socket edges from capped red pigment. |
| 023 first feedback | 96.20 / 81 / 77 / 73 / 62 | Reject: feedback cannot repair an albedo cap; change incident light. |
| 024 diffuse balance | — | Preparation and response capture, not an accepted beauty candidate. |
| 025 balanced pigment | 96.20 / 81 / 83 / 77 / 64 | Improvement: green clipping removed and regional wood color closer. |
| 026 balanced feedback | 96.20 / 81 / 84 / 77 / 64 | Small improvement in regional color; source for final baking. |
| 027 first bake | 96.20 / 81 / 52 / 40 / 45 | Reject: cut-material baking overwrote an input atlas, producing dark patches around excluded highlights. |
| 028 isolated-target bake | 96.20 / 81 / 84 / 77 / 64 | Corrected bake; final validation and checkpoint manifest record acceptance. |

## Remaining shortcomings

- Button highlights are too small and smooth, with an overly dark rim.
- The bright area below the slit is too broad; the slit mouth/floor still
  differs internally even though the outside outline is close.
- Collar and foot reflections remain too sharp, narrow and gold in places.
  The stem/socket also catch an unwanted long highlight.
- Grain relief is not yet aligned with all the newly fitted pigment detail;
  some highlights still read as polished resin rather than fine-grained wood.
- Side/rear renders expose the existing transition between projected pigment
  and procedural hidden wood. The higher contrast makes parts of that boundary
  more apparent. The rear is less convincing than the fixed reference view.
- Some inferred pigment retains residual shading because the geometry and
  lighting are estimates. Original texture, lighting and unseen shape remain
  unknown. Opposite-color checks concern geometry, not a finished black material.

The fixed-view gain justifies retaining this checkpoint; rear material
continuity remains a priority for the next iteration. Preserve the visible
fit while extending compatible grain/color around the hidden surfaces, then
improve microrelief and the button/foot reflections.

## Validation and delivery

The first baking attempt exposed a pipeline defect: Blender bakes every
selected material's active image. The cut material retained an old atlas node,
so baking corrupted an input pigment image. A packed-versus-disk pixel check
alone could not catch that earlier corruption. Cut materials now receive a
disposable target, and the bake verifies every input image's pixels are
unchanged before saving. The failed render never reached the public page.

Validation results are recorded in `checkpoint.json`; render/crop evidence is
beside this document. Final acceptance requires a packed-texture reopen check,
geometry/anatomy/camera validation, both original comparisons, matching mesh
and pigment hashes, and the bishop page controls.

The main `bishop-review.html` and the existing local preview are refreshed at
acceptance. The overlay uses the actual saved Cycles render; the rotating
viewer uses the same mesh, UV atlas and exported diffuse-energy balance with
approximate real-time lighting. The page controls are checked by a simulated
DOM/WebGL harness, not native browser inspection. Gallery proportions and
order, all original/candidate sources, and the queen are unchanged.

## Reproduction

Use an isolated working copy because the final bake writes its atlas to
`assets/bishop/bishop-boxwood-albedo.png`. Start with the archived checkpoint
002, not an earlier clay rebuild. `reproduction.json` records the ordered
script arguments and exact input hashes. The sequence is:

1. Apply `lighting-021.json` to checkpoint 002.
2. Prepare `024-balanced-diffuse` with `rebalance_diffuse.py` (factor 3).
3. Capture the black/white/pigment response at 64 samples.
4. Fit `025-balanced-pigment`, then capture its actual BSDF/pigment response.
5. Apply one bounded feedback step to create `026-balanced-feedback`.
6. Bake, pack, reopen and render `028-baked-pigment` at 96 samples.
7. Compare and validate before promotion; export and refresh the accepted page.

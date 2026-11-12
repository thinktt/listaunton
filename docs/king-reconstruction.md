# King reconstruction

Current accepted state: [mission checkpoint 013](king-mission/iteration-013/README.md).
The upper collar has a gentler upper curve and better placed reflections, following
checkpoint 012's middle-collar repair. The v6 wood material, overall dimensions and
54-degree camera are preserved. Read the [mission log](king-mission-log.md) for
current scores and remaining work. Use the documented canonical fresh renderer;
earlier alternate-entry-point variation remains documented. Older builders below
are historical.

## Historical clay study


Current geometry study, 4 October 2026. The original Lichess **Black-King.png is the source of truth**. The owner's selected **black candidate 1** supplies a larger working image for locating edges; generated details do not override the original. The white original was also inspected to distinguish dark shading from geometry.

## Sources and registration

- Original: `references/lichess-staunton-3d/Black-King.png`, copied unchanged to `assets/king/original.png`. SHA-256: `182e0ad834a1ffab73c010544cecf7eea7bdb62e4139e690066eb55f6d03e6f4`.
- Selected image: black king candidate 1, copied unchanged to `assets/king/reference.png`. SHA-256: `eb6094ebfd426d45fb5e57db5dfc73fed4ba47de1eb8f95a758c8663e0bf250c`.
- `assets/king/original-alignment.json` retains the candidate registration from the comparison tool. Its scale and percent translations describe the candidate on the original canvas. The model overlay applies the inverse to the original so both references share the selected image's 1254-pixel frame. There is no nonuniform stretching or image warping.
- Both original king sprites clip the cross at their top boundary. The model's top is an interpretation of the visible flat-topped cross, not evidence recovered beyond the crop. See [the provenance investigation](../PROVENANCE.md).

## Shape and camera

`scripts/king/profile.json` contains the measured turned profile as radius and projected ring-center Y in working-image pixels. `build_king.py` converts these measurements into a surface of revolution with 96 angular segments and one subdivision level. The camera is orthographic at 52 degrees elevation, with a 0.45-degree roll. Circular ring projections constrain this choice, but one image cannot uniquely determine the original camera or all physical proportions.

The cross is a separate closed extrusion with small rounded bevels and a slightly widening lower leg. It sits inside a recessed center enclosed by two small raised rings. Below are a broad shallow platter, tapered upper body, three stacked collars, concave stem, rounded raised socket, wide curved flare, one narrow base groove and a low foot.

The editable Blender file has two closed components: the body and cross. They intersect at the seat but are not boolean-fused. The exported viewer mesh has **68,492 triangles**, with separate corner normals retaining the cross's flat faces. This is a geometry study; faithful wood, final lighting, retopology and manufacturing preparation are not complete.

## Refinement record

Earlier profiles, renders and reports are retained under `history/king/iteration-1` through `iteration-4`.

1. Established the cross, ring ellipses, continuous lathe body and reference camera.
2. Lowered and reshaped the socket, corrected main collar spacing and narrowed the upper platter.
3. Narrowed the concave stem, adjusted flare and foot, and matched the slight image-axis tilt.
4. Raised the cross pedestal and made the platter's center shallower while preserving its outer edge.
5. Recessed the pedestal center to expose the correct length of the cross's lower leg. Reduced mesh density without a material loss of silhouette agreement.

The first selected-image outline overlap was approximately 91.5%; the current one is 97.4%. These figures are intersection-over-union scores, not percentages of the whole model's accuracy. Earlier and current reports used slightly different dark-edge thresholds, so this is an approximate progress comparison.

## Checks and remaining uncertainty

`assets/king/qa.json` records current silhouette overlap of about **96.0% with the original** and **97.4% with the selected image**. Mean horizontal boundary error is 6.16 and 3.44 pixels respectively on the 1254-pixel working canvas. Original-image boundaries have significant low-resolution antialiasing and very dark shading. The measurement excludes neither uncertainty nor artistic interpretation; it does not evaluate internal grooves, unseen surfaces, wood grain or lighting.

`compare.py` writes diagnostic contour images: cyan is the reference boundary and magenta is the rendered model boundary. It does not change source pixels. Internal rings were checked visually against both images, rather than inferred from the silhouette score.

`validation.json` confirms both mesh components have outward volume and no nonmanifold edges. The viewer embeds the exact exported mesh and saved Blender camera, verified against the model file's hash. Its runtime check covers camera projection, rotation/pan/zoom/reset, source switching and image registration. The local browser automation policy prevents direct inspection of file-URL pages, so browser layout has not been screenshot-verified by that tool.

Use the **Model** tab on [the king review](../king-review.html). **Reference overlay** defaults to the original; switch to the selected image for larger edge detail. **Rotate model** allows an independent inspection, and **Reset view** restores the saved camera. Other unmodeled pieces have explicit placeholders. The queen review remains unchanged.

## Checkpoint 004 foundation: exact light receivers

Follow `docs/king-mission/iteration-004/README.md` and
`scripts/king/rebuild_checkpoint_004.py`. The current model is the accepted
five-ring foot correction, base pigment v5 and fitted local base polish rig.
Use `render_regions.controls(scene)` for the two closed editable components.
The body is tagged `king_editable_control` and hidden only from rendering.
Three `king_render_region` objects are exact evaluated receivers; never edit
them directly. Regenerate after geometry/UV/attribute changes and validate
with `validate_render_regions.check(scene)`. `mission_trial.py`, export and
validation now handle these controls explicitly. Preserve original UVs when
baking a local pigment repair; `bake_registered_pigment.py` retains upper and
cross atlas bytes for this base-only pass. The local profile-crossing check
supplements, rather than replaces, closed-manifold validation.

## Checkpoint 005 lighting foundation

The current scene retains 004 geometry and pigment v5, adds local flare coat relief and fitted lower reflectors, and splits the flare receiver at ring 17. Its four exact receiver regions are foot, lower-flare, upper-flare and upper-body. `regenerate` preserves this split and all light routes. See iteration 005 for the causal spill diagnosis, exact scope checks and complete reproduction. Keep the closed control for export.

# King checkpoint 004: base grain, polish and foot groove

This pass removes the broad central white wash from the base and shifts the
smaller remaining shine toward the selected reference. The wood figure reads
more clearly. The foot groove is narrower and its lip flatter. Cross, crown,
collars, stem/socket, physical height/base diameter and the fixed 54-degree
camera are preserved. Original and selected-reference pixels remain unchanged.

## What changed and why

Five lower profile rings move vertically: 4 +0.020, 5 +0.055, 6 +0.030,
8 -0.040 and 9 +0.020 model units. All radii and other controls remain exact.
Inspection found a real crossing in the previous evaluated lathe profile near
radius 0.989254, height 0.247247. The edited section has none. Closed/manifold
checks alone did not detect that defect. The new check covers the lower
axisymmetric section, not a general proof of no self-intersections everywhere.

Three derived light receivers partition the exact evaluated body into foot,
flare and upper body. The closed editable body remains the geometry source.
Every face, UV layer, float attribute, material and custom corner normal is
checked against it. Separate real glossy lights can illuminate the base without
altering the upper rig. This is an artistic studio reconstruction, not a claim
that the original light rig has been recovered.

A black/white BSDF response supports a bounded pigment correction on the base,
fading out between rings 18 and 22. Bright highlights and unreliable shadows
retain prior pigment. The base alone uses roughness 0.19, coat roughness 0.10
and reduced fine coat-relief strength 0.0875. Five focused-light powers are
fitted from actual linear responses, then judged in a full Cycles render.
The first sharper-polish render was too bright and was not accepted unchanged.

V5 is a pigment atlas under a real Principled BSDF, with live reflections.
It retains existing UVs. All cross atlas columns and the upper-body pixels
above Blender row 755 are copied exactly from v4. The source estimate can still
contain residual shading, and unseen wood remains inferred. This is not a
billboard, beauty-image composite, or a claim to recovered original texture.

## Assessment

| Metric | Checkpoint 003 | Checkpoint 004 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.826% | 97.820% |
| Interior form | 82% | 83% |
| Wood color | 81% | 82% |
| Grain and surface texture | 77% | 78% |
| Lighting and reflections | 55% | 58% |
| Equal-weight mean | 78.565% | 79.764% |

Original-sprite IoU increases from 96.824% to 96.833%. The selected silhouette
tradeoff is 0.006 percentage points. Only IoU is measured; other percentages
are subjective. The holistic range is 73–82%. All trials 029–039, including
rejected lighting, are recorded in scores.json and the base contact sheet.

The lower base highlight is still too tall/oval, and the small upper glint is
too thin. The foot crescent is too weak, narrow and low; removing the previous
wrongly centered glare does not make the replacement exact. Upper-body glints
remain pale, regular and poorly shaped. Cross seating, shelf-like collar edges,
cavity contrast and some socket curvature still differ. Side inspection shows
the conspicuous orange-to-dark transition into inferred horizontal rear grain.
The side guide is an imagining and the white finish is not scored here.

## Validation and reproduction

The saved scene retains two closed, positive-volume components: turned body
and separate intersecting cross. Their viewer export has 70,364 triangles and
exact evaluated triangle positions, normals and atlas UVs. The three open
render partitions are derived lighting surfaces, not the exported geometry.
Packed texture pixels survive reopening exactly. The reopened beauty has
identical alpha and at most 1/255 channel variation. Atlas filtering has mean
foreground difference 0.105/255 and maximum 15/255 in fine base grain; the
maximum-error crop was inspected and retained as evidence, not hidden by a mean.

Run Blender with `--background --python-exit-code 1 --python
scripts/king/rebuild_checkpoint_004.py -- FRESH_LABEL`. The complete chain
starts from archived checkpoint003 and uses the numbered config files here.
It regenerates foot geometry, exact receivers, measured reflection fits,
base pigment, polish and final atlas under a fresh build directory. It does
not overwrite the accepted model or public texture. Use
`check_foot_checkpoint.py` for the intentional five-ring scope and
`validate_render_regions.py` for receiver fidelity. Always regenerate derived
receivers after changing control geometry, UVs or float attributes.

The complete reconstruction chain was executed from archived checkpoint003.
The reproduced render has identical alpha, mean foreground error 0.00125/255
and maximum 3/255; six pixels exceed 1/255. The maximum-error crop was inspected.
Only 123 base-atlas pixels differ, each by at most 1/255; cross and upper atlas
regions remain exact. This small numerical variation is recorded explicitly.

The king review opens Reconstruction with Reference overlay, Rotate model and
Side comparison from this same model. Browser shading is approximate. The page
controls are checked with the actual page's DOM/WebGL harness; native browser
inspection is not claimed. Candidate choices, original images, whole-set
defaults and historical projection studies are preserved.

Next: recover a brighter, correctly placed foot crescent and reduce the
remaining base glint height without changing camera or proportions. The
hidden-surface material transition is a separate major unresolved mismatch.
The goal remains active and incomplete.

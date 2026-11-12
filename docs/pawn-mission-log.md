# Pawn reconstruction log

## Mission-statement cleanup — 2026-11-12

The owner requested static goals with progress recorded separately. The
piece mission now preserves the original full visual-match objective and
five-category standard. This is a documentation migration, not a new model
iteration, fresh assessment, or change to the accepted model. The complete
pre-cleanup statement is available in Git at `fb75902169d17a993280dbd593f8d5163204e592:MISSION-PAWN.md`.

### Information moved out of the mission

Former drafting snapshot (historical, not the current accepted hash):

- Model SHA-256 at drafting: `133796d71e3d3f21b4dd25abf00e765e75e6d54d2a990bea55180ffee844f89e`.

Checkpoint 008 fits fine grain within the flare and socket reflections.
Scores are 96.81 / 91 / 93 / 90 / 90, with a working mean of 92.16%.
Original black IoU is 98.50%. Read docs/pawn-mission-log.md before
revising these scores. Update the pawn review and local preview between
accepted iterations.

The statement also carried a snapshot saying the queen goal was paused.
Activation and pause state belong to the relevant goal, not this piece's mission.

Future checkpoints, scores, defect lists and phase completion belong in this
log and the iteration evidence. Change the static goal only at the owner's
direction. Apply [the shared mission standards](../MISSION-SET.md).


## Checkpoint 001 · 2026-11-05

The first walnut checkpoint lifts the round part of the head about 15 reference
pixels, keeps its broad contact with the collar, and flattens the bottom of the
foot. Overall height changes by less than 0.000003 model units. Base diameter
changes from 1.6500 to 1.6532. The camera stays at its saved orthographic 54°
view, and the gallery uses its approved 49.2%-of-king display height.

| Metric | Seated clay baseline | Checkpoint 001 |
| --- | ---: | ---: |
| Selected silhouette IoU | 94.21% | 95.65% |
| Interior form | 74 | 80 |
| Wood color | 0 | 78 |
| Grain and surface | 0 | 72 |
| Lighting | 23 | 48 |
| Equal-weight working mean | 38.24% | 74.73% |

Original black overlap improves from 96.54% to 97.82%. White improves from
95.90% to 97.91%. These values use the mission's filled foreground masks.
The earlier clay report used raw masks. The four visual ratings are estimates.
The selected-view holistic assessment is 70–79%. The clay baseline had no
wood pigment or grain to score.

The original sphere radius was already within a fraction of a pixel of the
black sprite's fitted radius. Its center sat roughly 17 output pixels low.
An egg-shaped trial and a trial with a raised pedestal were rejected after
side inspection. The retained upper sphere stays round. The lower flank blends
into the original seat at its original contact width.

The 2048-square atlas carries inferred diffuse wood. Actual black and gray
BSDF renders measure reflections and diffuse response. Reliable wood samples
supply the visible pattern. Surface-space interpolation and the existing
unlit walnut source carry grain through highlight gaps and onto hidden faces.
One closed editable control drives both the Cycles render and UV-mapped viewer.

The base needs a stronger dark groove and broader textured highlights.
The current base reflector adds an unwanted fourth head glint, and the three
intended glints are weak and too smooth. The neck/socket reflection and a
yellowish pigment patch also differ. The hidden wood is an interpretation.
Next isolate and fit the three head glints, then reassess base and collar spill.

The reopened and independently rebuilt renders have identical alpha to the
selected trial and differ by at most 1/255 in RGB. The mesh is one closed,
positive-volume component with 57,984 triangles. Camera regression error is
below 0.000011 pixels in the DOM/WebGL interaction check. See the full trial
scorecard, views, checks, and rebuild instructions under
[iteration 001](pawn-mission/iteration-001/README.md). Mission in progress.

## Checkpoint 002 · 2026-11-05

Grain relief and real shaped reflectors give the head three textured glints.
The unwanted fourth glint is gone. The base and socket now catch light in
more of the intended places. The base still has broad highlights, the stem
has an unwanted narrow streak, and the deep foot groove remains too light.
The left base reflection is also too square. These limit the current result.

| Metric | Checkpoint 001 | Checkpoint 002 |
| --- | ---: | ---: |
| Selected silhouette IoU | 95.653% | 95.651% |
| Interior form | 80 | 80 |
| Wood color | 78 | 79 |
| Grain and surface | 72 | 76 |
| Lighting | 48 | 66 |
| Working mean | 74.73% | 79.33% |

Original black IoU is 97.816% and white is 97.911%. Geometry, UVs, pigment
and camera are preserved. The exported geometry binary is identical to the
previous checkpoint. Only IoU is measured. Holistic assessment is 75–83%.
Saved/reopened and independent replay renders agree with the chosen trial
within 1/255, with identical alpha. The site and existing local preview are
refreshed at this checkpoint. For all trials, actual settings and remaining
issues, see [iteration 002](pawn-mission/iteration-002/README.md).
Next inspect the flare curvature and actual groove geometry against both
originals. The mission remains active.

## Checkpoint 003 · 2026-11-05

The upper flare follows both original silhouettes more closely. Its lower
edge turns into a single dark recess above a flatter foot. Isolated light
renders identified the stray reflector on the stem. The revised lower rig
removes its streak. Fresh diffuse estimates register the walnut to the
reshaped surface, and a narrow band of darker, less polished wood follows
the groove around the full piece.

| Metric | Checkpoint 002 | Checkpoint 003 |
| --- | ---: | ---: |
| Selected silhouette IoU | 95.65% | 96.84% |
| Interior form | 80 | 85 |
| Wood color | 79 | 83 |
| Grain and surface | 76 | 78 |
| Lighting | 66 | 72 |
| Working mean | 79.33% | 82.97% |

Original black IoU is 98.49% and white is 98.12%. The four visual scores
are estimates. Holistic range is 78–85%. The approved height is preserved.
The base reflections are still too broad. A longer lower hemisphere and
soft shadow make the head and collar read as one mass in the elevated view.
Next test a rounder lower head seated directly in a shallow collar. See the
[checkpoint record](pawn-mission/iteration-003/README.md) for the render
comparisons, light measurements, finish assumptions and replay instructions.

## Checkpoint 004 · 2026-11-05

The lower head now follows a circular arc into a shallow collar. The dark
contact moves from around row 601 to 589, against rows 589–592 in the
references. The head's highest point and the overall pawn height are
preserved. Darkening the studio brings the gray rim much closer to the
reference brown. The wood is measured again under that lighting. Four
close reflectors brighten the collar while preserving the fixed-view head
glints. A wider rig was rejected after its reflections crossed the head.

| Metric | Checkpoint 003 | Checkpoint 004 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.84% | 96.81% |
| Interior form | 85 | 88 |
| Wood color | 83 | 87 |
| Grain and surface | 78 | 79 |
| Lighting | 72 | 75 |
| Working mean | 82.97% | 85.16% |

Original black and white IoU rise to 98.51% and 98.14%. The selected
silhouette decreases by 0.03 percentage points. The visual estimates favor
the clearer join and closer regional color. Holistic range is 81–88%.
The broad base reflections and soft, pale head glints still differ from the
broken highlights in the original finish. Next measure how the actual
varnish responds to changes in roughness. The [checkpoint evidence](pawn-mission/iteration-004/README.md)
includes the darker-studio test, rejected lighting setup and exact replay.

## Checkpoint 005 · 2026-11-05

The walnut carries a measured roughness map. Three compact area emitters
bring the bright end of the original head-glint pattern closer to the
selected reference. The right glint rises from 170 to 233 at the 99th
percentile, against 239 in the reference. The left glint still has a
smooth, flat core. The broad reflections on the flare also stand out.

| Metric | Checkpoint 004 | Checkpoint 005 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 88 | 88 |
| Wood color | 87 | 88 |
| Grain and surface | 79 | 81 |
| Lighting | 75 | 80 |
| Working mean | 85.16% | 86.76% |

Original black IoU is 98.51% and white is 98.14%. The other four scores
are visual estimates. Holistic range is 83–90%. The rotating viewer uses
the same roughness and pigment maps as the saved pawn. See the
[checkpoint evidence](pawn-mission/iteration-005/README.md) for brightness
and contrast measurements, side views and the independent replay. Next
test how fine changes in surface orientation break up the three glints.

## Checkpoint 006 · 2026-11-05

Small surface slopes break up the pale patches in the varnish. Fitting
the lower emitters along the measured flare curves restores a narrow second
reflection on the right. The head, socket and flare now catch warmer light.
The left flare still has a short, broad patch, and the head-to-collar
shadow remains soft.

| Metric | Checkpoint 005 | Checkpoint 006 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 88 | 88 |
| Wood color | 88 | 90 |
| Grain and surface | 81 | 85 |
| Lighting | 80 | 84 |
| Working mean | 86.76% | 88.76% |

Original black IoU is 98.51% and white is 98.14%. All three head glints
fall within one original sprite pixel of their reference centers. The
fixed-view holistic assessment is 85–91%. The five-category mean includes
four visual ratings. The [checkpoint evidence](pawn-mission/iteration-006/README.md)
includes the native-size comparison, full-size crops and measured surface
tilts. Next remeasure the diffuse contribution under these revised lights,
especially the walnut beside the dark contact and around the flare.

## Checkpoint 007 · 2026-11-05

The lower cheek now occludes the collar within half a pixel of the selected
edge. Small front studio sources cast a narrow physical shadow. Its core
measures 6.3 brightness levels against the reference's 4.2. Six pixels out,
the collar returns to 28.7 against 29.1. Fresh diffuse measurements recover
the surrounding walnut. The four-angle orbit check also exposes broader,
inferred grain around the back.

| Metric | Checkpoint 006 | Checkpoint 007 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 88 | 91 |
| Wood color | 90 | 92 |
| Grain and surface | 85 | 87 |
| Lighting | 84 | 87 |
| Working mean | 88.76% | 90.76% |

Original black IoU is 98.50% and white is 98.14%. The selected enlargement
disagrees with both originals on the width of the rear flare. The model
follows the originals there. The holistic range is 87–93%. The four visual
ratings remain estimates. The [checkpoint evidence](pawn-mission/iteration-007/README.md)
includes the measured disagreement, shadow profiles and four-angle views.
Next inspect the remaining narrow flare and foot reflections and the
texture visible through their brightest areas.

## Checkpoint 008 · 2026-11-06

Compact reflectors and a second measured normal map bring out the upper
head glint, left stem edge, socket lip and flare reflections. One blown-out
lighting trial was rejected and the low-power search corrected. On the
left flare, fine brightness contrast rises from 11.4 to 17.7, against
29.4 in the target. The fine-pattern correlation improves from 0.60 to
0.79. The narrow right flare and foot lines still need a crisper finish.

| Metric | Checkpoint 007 | Checkpoint 008 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 92 | 93 |
| Grain and surface | 87 | 90 |
| Lighting | 87 | 90 |
| Working mean | 90.76% | 92.16% |

Original black IoU is 98.50% and white is 98.14%. Native original RGB
error improves from 16.75 to 16.37, compared with 15.74 for the chosen
enlargement. Holistic range is 89–94%. See the
[checkpoint evidence](pawn-mission/iteration-008/README.md) for actual
sampling, fine-contrast, material and reflector checks. Next test whether
variation in polished and porous wood can recover the remaining grain
contrast along these thin reflections.

## Checkpoint 009 · 2026-11-12

A measured finish map restores more of the wood pattern inside the thin
flare and foot reflections. It varies real roughness and polish strength,
with the existing geometry, pigment, normal map, camera and 44 lights held.
On the foot line, fine-pattern correlation improves from 0.79 to 0.90.
Its fine contrast rises from 17.1 to 22.7 against 30.4 in the selected image.

| Metric | Checkpoint 008 | Checkpoint 009 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 90 | 92 |
| Lighting | 90 | 91 |
| Working mean | 92.16% | 92.76% |

Original black and white IoU remain 98.50% and 98.14%. Native original
RGB error changes from 16.37 to 16.40, a small tradeoff. The visual ratings
are estimates, with a holistic range of 90–95%. The reopened model and an
independent reconstruction agree with the inspected trial to within one RGB
level. See the [checkpoint evidence](pawn-mission/iteration-009/README.md).

Tests traced the pale line beneath the ball to reflected light from the
collar. Disabling secondary glossy rays removed it but darkened the lower
ball, including after a measured pigment correction. Both trials are rejected.
The accepted scene retains its original ray depths. Next constrain that
reflection while preserving the surrounding walnut and contact shadow.

## Checkpoint 010 · 2026-11-12

The ball now casts a narrower contact shadow. A smooth local mix of matte
and varnished wood reduces the pale reflected line beneath it. Four existing
collar reflectors, collar-only normal detail and measured pigment are refined;
the geometry, proportions, UVs and 54-degree camera remain unchanged.

| Metric | Checkpoint 009 | Checkpoint 010 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 92 | 92 |
| Lighting | 91 | 92 |
| Working mean | 92.76% | 92.96% |

The contact brightness-profile error falls from 7.16 to 3.03 levels. Native
original RGB error rises slightly from 16.40 to 16.50. Original black and
white silhouette IoU remain 98.50% and 98.14%. The four visual ratings are
estimates; the holistic range remains 90–95%. The collar highlight is still
too coarse, and the pale lower-head reflection is reduced rather than gone.
See the [checkpoint evidence](pawn-mission/iteration-010/README.md).

The saved model and independent replay agree within one RGB level. The fixed,
clay, side and rotating assets share that saved model. Four-angle inspection
checks the actual material away from the fitted camera. The mission remains
incomplete; next refine the collar's fine reflection pattern while preserving
this contact and illumination.

## Checkpoint 011 · 2026-11-12

The collar has finer reflected grain after local finish and normal-map
calibration. Higher sampling and disabled light-tree selection make the
highlights more stable. Pigment is measured again at that quality. The
geometry, UVs, 54-degree camera, actual lights and contact setup stay fixed.

| Metric | Checkpoint 010 | Checkpoint 011 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 92 | 93 |
| Lighting | 92 | 92 |
| Working mean | 92.96% | 93.16% |

Left collar fine-pattern correlation improves from 0.657 to 0.815; the upper
head improves from 0.826 to 0.904. Fine flare and foot correlations regress
to 0.663 and 0.861. Native original RGB error changes from 16.50 to 16.60,
and contact-profile error from 3.03 to 3.44. These tradeoffs remain visible
in the [checkpoint evidence](pawn-mission/iteration-011/README.md).

The four visual scores are estimates; the holistic range remains 90–95%.
Original black and white silhouette IoU are 98.499% and 98.135%; tiny mask
changes reflect sampling, with an identical exported mesh. Saved/reopened
and independently rebuilt views agree within one RGB level. The mission
remains incomplete. Next refine the thin flare/foot reflections under the
more stable sampling while retaining the clearer collar and head grain.

## Checkpoint 012 · 2026-11-12

The lower finish now preserves more of the grain breaks inside the flare
and foot reflections. Local roughness/polish and normal maps change; the
geometry, pigment, contact setup, 44 lights and fixed 54-degree camera stay
unchanged. The surface maps are identical outside the base's UV band.

| Metric | Checkpoint 011 | Checkpoint 012 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 93 | 94 |
| Lighting | 92 | 92 |
| Working mean | 93.16% | 93.36% |

Thin-flare pattern correlation improves from 0.663 to 0.869, and foot-line
correlation from 0.861 to 0.929. Foot-line fine contrast rises from 21.4 to
25.6 against 30.4 in the selected reference. Base/foot RGB error falls from
3.14 to 2.76. Native original RGB error stays 16.60 at the reported precision;
original black and white IoU remain 98.499% and 98.135%. Contact-profile error
changes slightly from 3.44 to 3.48. A warmer-foot lighting test is rejected
because its small selected-view gain worsens the original color comparison.

The visual scores remain estimates, with a holistic range of 90–95%.
See the [checkpoint evidence](pawn-mission/iteration-012/README.md) for
reproduction, actual saved-model checks, alternate-angle inspection and
remaining mismatches. The mission remains incomplete; next examine the
stem/socket reflections and remaining collar residuals while preserving
the clearer head and lower finish.

## Checkpoint 013 · 2026-11-12

Local finish and normal detail make the stem and socket grain closer while
retaining geometry, pigment, camera and all 44 lights. A small reflector
repositioning worsened the full patch and original color comparisons and
was rejected. The head, collar and lower-base surface maps are preserved.

| Metric | Checkpoint 012 | Checkpoint 013 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 94 | 94 |
| Lighting | 92 | 92 |
| Working mean | 93.36% | 93.36% |

Stem pattern correlation improves from 0.402 to 0.735, and socket-lip
correlation from 0.883 to 0.943. The overall visual scores stay unchanged:
the enlarged stem highlight is still broader and rougher than the selected
reference. Collar/stem RGB error falls from 2.44 to 2.32; native original
RGB error changes from 16.60 to 16.61. Original black/white IoU remain
98.499%/98.135%, and the holistic visual range remains 90–95%.

See the [checkpoint evidence](pawn-mission/iteration-013/README.md) for
isolation studies, accepted/rejected trials, reproduction and saved-model
checks. The mission remains incomplete. Next isolate the older bump and
fine-normal layers at the stem rim before another material or curvature
change, preserving the accepted lighting and head/base improvements.

## Checkpoint 014 · 2026-11-12

A broader local normal-field and finish fit improves the stem's reflected
grain. The geometry, pigment, 54-degree camera, all 44 lights and the rest
of the surface remain unchanged. Removing relief layers worsened the
result; a six-parameter reflector adjustment produced too little benefit
and was rejected.

| Metric | Checkpoint 013 | Checkpoint 014 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.81% | 96.81% |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 94 | 94 |
| Lighting | 92 | 92 |
| Working mean | 93.36% | 93.36% |

Stem fine-pattern correlation improves from 0.735 to 0.830, with contrast
20.00 against the selected reference's 24.52. Collar/stem RGB error falls
from 2.325 to 2.303; native original RGB error stays 16.61 at the reported
precision. Original black/white IoU remain 98.499%/98.135%. Only 0.241% of
finish-map pixels and 0.286% of normal-map pixels change, within the stem
UV band 0.49-0.65.

The whole-piece visual scores remain estimates, with a holistic range of
90-95%. The reflection still has an overly soft, fragmented core and excess
light immediately under the collar. See the [checkpoint evidence](pawn-mission/iteration-014/README.md)
for actual layer ablations, rejected lighting changes, reproduction and
saved-model checks. The mission remains incomplete. Next examine the
larger collar residual at reference x=437-469, y=606-638, while preserving
the accepted stem, head and base refinements.

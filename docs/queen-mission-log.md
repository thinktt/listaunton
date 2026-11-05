# Queen mission log

## Baseline and current state

Mission activated from repository commit `b9daa1a`. The accepted model at
activation is the restored `3096e84` model, SHA-256
`eb7daec22f35f4c282e9e41ac2e1a5eb26b2169b8b30f49673a0d0878b81dcc4`.
Reference SHA-256:
`bc510a8f5fff0a1e51fd913f1cf4f4707849d68c5d4dabc8ce6df16cc2e1423a`.
The camera remains orthographic, 54 degrees above the board. All comparisons
use the original registration and unchanged source images.

The first live Luna check was 2026-11-05 05:39:46 UTC: 3% used / 97% remaining
in the 10080-minute codex weekly window, resetting 2026-11-11 13:19:48 UTC.
A fresh check at 05:47:27 UTC reported 4% used / 96% remaining. Luna is
assigned to check every five minutes and alert at <=3% remaining.

First accepted mission checkpoint: trial 013, saved model SHA-256
`35a939bf3af852067bfdd25dd7be217c60e11b2e6ffeeee688a11b7ff0160c0c`.
Its renders, viewer mesh/UVs, and side comparison are synchronized. The starting
model and renders are preserved in `history/queen-mission-start`; no rejected
trial is exposed in the review controls. Trials remain staged under
`work/queen-mission-run/build/queen-mission` in the Windows workspace.

## First iteration: internal profiles, grain, and reflections

Measured high-res collar front arcs at approximately y=456, 513, and 554
pixels. These measurements informed localized profile trials rather than
another global silhouette-only fit. The unchanged source light/material
settings were used for the initial geometry comparisons.

Scores are visual judgments except the measured high-res and original
silhouette IoUs. The overall column is the unchanged five-category mean.

| Trial | High-res IoU | Original IoU | Interior form | Color | Grain | Lighting | Overall | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Starting accepted model | 97.906% | 97.904% | 70 | 60 | 30 | 40 | 59.58 | Baseline |
| 001 collars | 97.548% | 97.303% | 74 | 60 | 30 | 40 | 60.31 | Reject: rear middle collar too wide; outline worsened |
| 001b narrower collars | 97.574% | 97.299% | 76 | 60 | 30 | 40 | 60.71 | Reject for promotion: lower assembly outline regressed |
| 002 crown | 97.567% | 97.299% | 70 | 60 | 30 | 35 | 58.51 | Reject: interior became a flat dish with a pronounced shoulder |
| 002b smooth bowl | 97.573% | 97.301% | 73 | 60 | 30 | 37 | 59.51 | Reject: highlights/cavity still less convincing; no net improvement |
| 003 contained collars | 98.023% | 97.865% | 74 | 60 | 30 | 40 | 60.40 | Trial: high-res outline improved; slight original-outline loss |
| 003b unchanged lower radius | 97.903% | 97.904% | 74 | 60 | 30 | 40 | 60.38 | Geometry candidate; alpha difference is confined to edge precision |
| 004 continuous grain | 97.903% | 97.904% | 74 | 58 | 45 | 40 | 62.98 | Trial: flow improves, but grain is too coarse and orange |
| 005 smaller lights | 97.903% | 97.904% | 74 | 55 | 45 | 38 | 61.98 | Reject: dimmer crown and insufficient bright reflections |
| 006 polish | 97.904% | 97.904% | 74 | 35 | 42 | 45 | 58.78 | Reject: pale pink/burl appearance and still misplaced reflections |
| 007 warm light | 97.904% | 97.904% | 74 | 62 | 43 | 51 | 65.58 | Material candidate: removes the large pale collar patch; finer grain still inaccurate |
| 008 compact finial | 97.903% | 97.904% | 77 | 60 | 30 | 40 | 60.98 | Geometry candidate: better seating; upper finial and bowl still differ |
| 009 fine wood | 97.904% | 97.904% | 77 | 50 | 50 | 46 | 64.18 | Reject for promotion: over-bright orange wood, overly clean polish, twin base highlights |
| 010 patina | 97.904% | 97.904% | 77 | 40 | 53 | 44 | 62.38 | Reject: pink cast and broad pale reflections |
| 011 directional wood | 97.904% | 97.904% | 76 | 60 | 52 | 48 | 66.78 | Trial: dark crown restored; obvious invented grain remains |
| 012 projected pigment | 97.904% | 97.904% | 76 | 64 | 65 | 48 | 70.18 | Candidate: recognizable base markings and regional grain; highlights still wrong |
| 013 pigment atlas | 97.904% | 97.904% | 76 | 64 | 65 | 48 | 70.18 | Selected for validation: same pigment baked into a portable UV atlas |
| 014 reflection fit | 97.904% | 97.904% | 76 | 63 | 65 | 45 | 69.38 | Reject: enlarged unwanted pale patch on left base |

An attempted promotion of 001b was rejected by automatic approval review
because its silhouette fit regressed. The command did not run. The safer
003/003b alternatives retain the accepted lower profile, with changes confined
principally to the upper/middle collars and crown-body transition. No rejected
trial has replaced the canonical model.

The 003b alpha test changes high-res IoU by -0.0029 percentage points and
original IoU by +0.0003 points relative to baseline. Body/collar, stem/socket,
and base/foot region overlaps are identical to the baseline; the tiny
difference lies at the crown boundary. This is distinct from the material
outline regression of 001b. The finial, bowl, lower body, camera, and overall
height are preserved in 003b.

For 004/005 the existing generated albedo is mapped continuously by
circumference and distance along the turned profile, rather than box
projection. The grain drives slight bump and roughness variation. No new
source images or generated reference replacements were introduced. A finer,
less saturated grain and stronger, smaller-light trial (006) failed: it turned
the surface pink and made the grain look like dense burl. Trial 007 restores
warmth and removes the distracting broad white collar patch. It remains a
candidate, not a promoted result.

Trial 008 raises the finial's base and gently raises the basin around it while
lowering the physical apex by about 0.027 units. The base, outer crown, camera,
and lower assembly remain unchanged; the height/base ratio remains within the
existing approved tolerance. This is an improvement in seating, not a claim
that the knob is now exact. Its upper projected boundary is still slightly high.

Trial 009 uses a new built-in ImageGen albedo, preserved as
`assets/queen/walnut-fine-albedo.png`; its exact prompt and reference role are
recorded in `walnut-fine-generation.json`. It is a new unlit material swatch,
not an edited reference. The material uses continuous circumference/meridian
UVs and real Cycles lighting. The resulting grain is less coarse, but the
bright orange color and excessively clean reflections prevent acceptance.
Trial 010 tests darker color, microscopic pore relief, and a lower left light
that reaches the socket without flooding the crown body.

Read-only reflection-ray measurements (`inspect_reflections.py`) identify
where selected reference highlights would reflect on the current surface.
These are hypotheses for the fit, not evidence of the original artist's light
setup. At the reference bowl highlight, the old finial occupied the camera ray;
this independently confirms a remaining shape mismatch.

Latest resource check: 2026-11-05 06:54:47 UTC, 7% used / 93% weekly remaining,
same codex weekly window and reset. The Luna guard continues every five minutes.

Remaining major discrepancies: finial and bowl form, lowest collar profile,
socket/flare transitions, missing distinctive base grain, regional color,
and the positions/intensity of reflections. No perfection claim is warranted.

## Candidate selected for the first accepted checkpoint: 013

The generated de-lit source is `assets/queen/reference-delit-source.png`, with
the exact built-in ImageGen prompt in `reference-delit-generation.json`. It
retains much of the visible grain placement but exaggerates some markings and
retains residual recess shading; it is an inferred albedo, not recovered ground
truth. `project_reference_material.py` stores fixed mesh UVs and visibility
coverage to blend that pigment into the generated continuous wood on hidden
surfaces. `bake_pigment_atlas.py` bakes only the color network to a 2048-square
atlas and restores the Principled BSDF before rendering/saving. Reflections and
lighting are not baked into this atlas. The public image remains a real Cycles
render of the complete queen, not a composited source photograph.

Compared with the baseline, this candidate keeps essentially the same outside
fit, improves the upper/middle collars and finial seating, replaces unrelated
fine texture with recognizable grain markings, darkens the crown body, and
removes the large pale rear-collar patch. Native reference and original sprite
comparisons remain necessary: the finial is still too pointed, the bowl/rim
needs refinement, collars are still too shelf-like, the socket is too soft,
and the highlights on the base and socket remain visibly misplaced. The
color/grain improvement does not resolve those geometry and lighting errors.
The side render also exposes the thin lowest collar and broad socket shoulder;
the next geometry iteration should address these without losing the original
outline fit. The texture remains attached in the side view, although transitions
to imagined grain on hidden surfaces still warrant more angular inspection.

The trial validator passes: closed manifold mesh, positive volume, eight crown
tips, monotonic lower body, camera 54.00000066 degrees. Height/base ratio is
2.167048 versus the target 2.179289, within the unchanged 0.015 tolerance; the
compact finial lowers physical height by 0.59%. Gallery defaults remain intact.
High-res IoU differs from baseline by only -0.00157 percentage points and the
original IoU by +0.000028 points, consistent with antialiasing precision, with
no meaningful external outline regression. This is not the rejected 001b trial.

The working five-category mean is 70.18%, up from 59.58%; the holistic visual
assessment is roughly 65–70%. These are explicitly subjective except the two
IoUs. The mission remains incomplete.

Completed checks for this checkpoint:

- Final saved mesh passes the same camera, manifold, positive-volume, eight-tip,
  monotonic-body and proportion-tolerance checks.
- Viewer exports all 715,776 evaluated triangles, without decimation. It splits
  UV seams while preserving every triangle corner's position and smooth normal;
  maximum corner UV difference is 1.2e-7, with an exact binary round trip.
- The same albedo atlas is embedded in the viewer. Camera regression passes
  30 Blender-projected samples across viewport shapes, maximum error 0.0000382
  pixels. Rotation, pan, projection changes, reset and tab persistence pass.
- Review interaction/source-hash checks and the site check pass, including
  eight pages, 55 local links, all twelve originals and the parts-map sandbox/CSP.
- All 39 protected inputs of the historical projection study remain intact.
  Its validator passed using Windows Python because WSL Python lacks NumPy.
- Pigment-only baking changes the rendered object by mean 0.233/255 RGB levels
  (95th percentile 1/255), preserving the tested appearance without baking lights.
- The side images were freshly rendered from this same saved geometry/material,
  registered uniformly to the unchanged imagined guide, and visually inspected.
- Native browser GPU inspection was unavailable; the browser checks execute the
  actual page runtime in a simulated DOM/WebGL environment. No native-browser
  render-quality claim is made. Blender's actual Cycles renders were inspected.

Evidence is in `docs/queen-mission/iteration-001/`. Rebuild instructions are in
`docs/queen-54-wood.md`. Next: improve lower-collar roll/socket curvature while
preserving the silhouette, then fit the bright edge crescents and base reflection.

## Second iteration in progress: edge rolls, reflections, and regional color

Starting accepted commit: `33f0adc` (file-mode cleanup in `6469bba`). Model SHA
remains `35a939bf3af852067bfdd25dd7be217c60e11b2e6ffeeee688a11b7ff0160c0c`.
The repository and local preview show that checked checkpoint. No trial below
has replaced it at this point.

| Trial | High-res IoU | Original IoU | Interior form | Color | Grain | Lighting | Overall | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 015 lower roll | 97.915% | 97.896% | 77 | 64 | 65 | 48 | 70.38 | Reject: slight rounding gain does not justify original-outline loss |
| 016 raised foot edge | 97.644% | 97.765% | 74 | 64 | 64 | 47 | 69.33 | Reject: base contour moves and the left reflection grows |
| 017 internal groove roll | 97.903% | 97.904% | 77 | 64 | 65 | 48 | 70.38 | Candidate: narrower edit preserves outline, but lighting remains uncertain |
| 018 measured lights | 97.904% | 97.904% | 76 | 63 | 65 | 45 | 69.38 | Reject: correct-area highlights also create excessive unwanted reflections |
| 019 varied surface polish | 97.904% | 97.904% | 77 | 63 | 65 | 44 | 69.38 | Reject: diffuse white patches and exaggerated collar reflections |

The localized four-ring groove change in 017 preserves the outer foot and
flared-base boundary. The wider 016 change did not; the actual alpha tests
exposed a regression that was not apparent from the front groove alone.

Highlight centroids were measured from the unmodified reference, then ray-cast
onto the accepted mesh at the fixed camera. Normals imply disparate light
directions; some foot/base locations imply lights below the model. This is a
diagnostic of the current geometry and inferred rendering, not a claim about
how the source was made. Seven targeted lights and orientation-dependent
roughness did not improve the overall image, so those trials are rejected.

Regional RGB measurements expose a more useful next target: the accepted
wood is too bright and too orange, especially the crown body, stem, socket and
foot. For example, crown-body median RGB is approximately (77,29,1), compared
with (43,17,4) in the reference; base median is (128,58,9), compared with
(87,39,13). These exclude black/background and the brightest reflection pixels.
Trial 020 corrects pigment in the actual shader using smooth height zones and
a separate finial region; geometry, lights and source images remain unchanged.
It is an artistic material adjustment, not evidence that original albedo has
been uniquely recovered.

Resource check at 2026-11-05 07:26:46 UTC: 8% used / 92% remaining in the same
weekly bucket. Luna continues five-minute checks; the goal remains active.

### Pigment, surface relief, and finial refinement

| Trial | High-res IoU | Original IoU | Interior form | Color | Grain | Lighting | Overall | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 020 regional pigment | 97.904% | 97.904% | 76 | 70 | 65 | 48 | 71.38 | Dark distribution improves, but blue correction creates a reddish/mauve cast; superseded |
| 021 warm pigment | 97.904% | 97.904% | 76 | 75 | 66 | 48 | 72.58 | Retain the narrower RGB correction; body, stem, socket and foot darken appropriately |
| 022 grain relief | 97.904% | 97.904% | 76 | 75 | 70 | 49 | 73.58 | Retain: highlights break over the visible pigment grain instead of unrelated procedural grain |
| 023 directed reflections | 97.904% | 97.904% | 76 | 73 | 70 | 47 | 72.78 | Reject: removes the left base patch but introduces a bright stem streak and wrong collar/bowl patches |
| 024 rounded finial | 97.903% | 97.904% | 78 | 75 | 70 | 49 | 73.98 | Candidate for acceptance: fuller upper curve and raised lower shoulder, unchanged maximum height |
| 025 turned polish | 97.904% | 97.904% | 78 | 75 | 70 | 49 | 73.98 | Reject: anisotropic response adds complexity without a clear visible improvement over 024 |

The 021 grade is an actual material adjustment using smooth height regions and
a separate radial finial mask. It preserves the albedo's grain. Against the
same measured image regions, crown-body median RGB changes from (77,29,1) to
(50,22,7), versus reference (47,20,4); stem changes from (84,32,1) to
(54,22,5), versus (55,23,5). Base changes from (124,56,7) to (89,41,18),
versus (85,38,13). Matching regional medians is not proof of matching the
spatial color pattern. The base still lacks the source's detailed warm/cool
variation, and its right highlight remains misplaced.

The previous bump network still used the earlier fine wood, although the
visible color had moved to the pigment atlas. Trial 022 uses the atlas's
ungraded luminance for relief, mixed with fine three-dimensional pores. Its
surface response is closer to the reference's broken reflections, though
the small wrinkles remain somewhat too uniform and artificial. Roughness is
0.19, coat roughness 0.075, coat weight 0.35; bump strength 0.45 and distance
0.007. Trial 025's directional polish was inspected but did not merit adoption.

Trial 024 only changes rings 107–116, making the finial fuller near its top
and raising the lower shoulder. It keeps the apex at the same height; the
neutral render was completed too. Its small IoU variation is antialiasing
precision from 48 rather than 64 samples, not a change to the outer boundary.
The finial is less pointed but is still not an exact match, and the bowl's
reflection and inner contour remain visibly different.

Latest resource check: 2026-11-05 07:53:22 UTC, weekly 10080-minute window,
9% used / 91% remaining, resetting 2026-11-11 13:19:48 UTC. Luna remains
active on the five-minute cadence. The mission is incomplete.

Trial 026 is the accepted pigment-only rebake of 024 into a second atlas. It
reuses the existing UV coordinates. No lights are baked; the material remains
a Principled BSDF, and the source images remain unchanged. The rendered
rebake differs from the graded shader by mean 1.51/255 RGB levels on the object
(95th percentile 7/255), including the difference between 48 and 64 samples
and denoising of fine relief. The images were inspected; regional tone and
visible grain are retained. This is not claimed to be an exact pixel match.

Accepted scores: silhouette **97.904%**, interior **78**, color **75**, grain
**70**, lighting **49**; equal-weight working mean **73.98%** (holistic visual
assessment about 70–75%). Original sprite IoU is **97.9036%**, unchanged from
the first checkpoint. The finial remains somewhat tall, the bowl and rim
still differ, the collars are shelf-like, and the socket's shoulder is too
soft. Strong reflections remain in the wrong places, especially on the base,
stem and bowl. The narrow bright edge crescents remain missing. These visible
differences prevent any claim of completion.

The saved accepted model SHA-256 is
`f2e65f66fa65de9f212e5300d889350b877259aaf422c8d29a9430a49a016b99`.
The closed mesh, positive volume, eight tips, monotonic lower body, 54-degree
camera and unchanged height/base ratio 2.167048 all pass. The viewer exports
all 715,776 triangles with exact geometry and UV seam handling; binary round
trip and source-file preservation pass. Camera regression passes 30 sample
points over five viewport shapes with maximum error 0.0000382 pixels.
The actual page runtime passes rotation/pan/reset, source validation, tabs,
parts-map containment and side-state checks. Native browser GPU inspection
remains unavailable; these runtime checks use the simulated DOM/GL harness.

Wood and neutral fixed-view and side renders were regenerated from the same
accepted file. The side images were visually inspected and uniformly
registered to the unchanged guide. They expose the same remaining flat
lower collar and broad socket shoulder; the texture remains attached in the
profile. The original references and side-gallery defaults are untouched.

Checkpoint resource reading at 2026-11-05 08:01:26 UTC: weekly **10% used /
90% remaining**, reset 2026-11-11 13:19:48 UTC. Luna continues five-minute
monitoring. The next hypothesis is to adjust one reflection light at a time,
starting with the left socket/base patch, and independently improve the lower
collar's roll without losing the original outline.

Repository checks after integration pass: eight site pages, 55 local links,
model/viewer hash, parts sandbox/CSP, all twelve original PNG hashes, candidate
provenance and alignment, and all 39 protected historical projection inputs.
Git whitespace checks pass and no executable-bit changes were introduced.

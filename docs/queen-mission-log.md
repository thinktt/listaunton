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

## Third iteration in progress: measured light fitting

Starting accepted revision is `9e03943`, saved model SHA-256
`f2e65f66fa65de9f212e5300d889350b877259aaf422c8d29a9430a49a016b99`.
The repository and local preview both show that checked checkpoint. The
following lighting trials have not replaced it.

| Trial | High-res IoU | Original IoU | Interior form | Color | Grain | Lighting | Overall | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 027 socket light | 97.904% | 97.904% | 78 | 73 | 70 | 51 | 73.98 | Reject: stem streak improves, but a large left base reflection appears |
| 028 base key | 97.904% | 97.904% | 78 | 73 | 70 | 54 | 74.58 | Retain measured key position for study; do not promote the unwanted second base patch |
| 029 balanced lights | 97.904% | 97.904% | 78 | 70 | 70 | 53 | 73.78 | Reject: base position improves, but the bowl becomes a bright ring and overall tones darken |
| 030 blended lights | 97.904% | 97.904% | 78 | 69 | 70 | 54 | 73.78 | Reject: dimming the bowl does not fix its reflection shape or the darker overall color |
| 031 controlled key | 97.904% | 97.904% | 78 | 70 | 69 | 51 | 73.18 | Reject: narrow spread removes finial streak but concentrates excessive light on base/collars |

`highlight_regions.py` measures bright, low-saturation reflection mass,
centroids and spread in fixed image regions. These are diagnostics, not a
replacement score or a proof of recovered source lighting. The reference's
main base highlight is centered near (579.31,903.45); trial 028 reaches
(578.94,904.25), while the accepted rig is near (540.39,898.19). However,
028's vertical spread is 24.47 pixels versus the reference's 37.69, and it
has excess brightness and an unwanted second patch. A correct centroid alone
does not justify acceptance. The updated finial normals were measured again
after the 024 geometry edit; old light directions must not be reused blindly.

The coupled lighting trials plateaued. The next method renders 14 independent
low-resolution light contributions (including the existing rig, measured
highlight directions and world light), then solves nonnegative light energies
against the reference. Blender already bundles PyOpenColorIO; no installation
was needed. The inverse AgX/sRGB transform was checked with a forward round
trip: mean error 0.000196 in normalized RGB over foreground pixels, maximum
0.0374. This converts the comparison target into the current renderer's
linear color space for fitting; it does not assert the reference used AgX.

Basis EXRs and their linear sums are diagnostic only. A fitted rig must be
rendered normally at full resolution, visually scored, and validated before
replacing the public beauty render. No reference pixels or composited image
will be substituted for the actual model render. The fit excludes background
and silhouette-edge pixels, balances major height regions, and retains
nonnegative physical light strengths. It cannot by itself repair wrong
geometry, albedo, roughness or unknown source image processing.

Pre-batch resource reading at 2026-11-05 08:28:46 UTC: weekly 10% used / 90%
remaining, reset 2026-11-11 13:19:48 UTC. Luna remains active on five-minute
checks. The mission is incomplete, with the accepted working score 73.98%.

The 14 basis renders completed and have distinct hashes. The first fit uses
38,969 foreground draft pixels and converges in 22 coordinate-descent passes.
Its weighted scene-linear RMSE is 0.3713 versus 0.7997 for the previous rig
under that diagnostic loss. It selects weaker individual lights and much
stronger world illumination (1.3874 rather than 0.03). That numerical result
is not yet a visual improvement claim; a full actual render is in progress.

The full trial 032 render was rejected: the high world strength covers the
wood in a gray reflective veil. Scores were 97.904 / 78 / 62 / 65 / 50,
mean 70.58. A smaller mathematical residual was not a better visual match.
Trial 033 adds one broad fill with specular contribution disabled and caps
world strength at 0.08. It avoids the gray veil and fits several reflection
positions better, but remains too dark and has misplaced bright bands.
Scores: 97.904 / 78 / 71 / 70 / 55, mean 74.38; not promoted. Its fitted
rig is being used as an experimental shading estimate, not a recovered claim
about the source artist's lighting. Accepted/public assets remain 9e03943.

The next material experiment measures the 033 shader's black/white base-color
responses under those lights, plus its unlit pigment. It estimates pigment
from `(reference - black response) / (white response - black response)`,
bounded to 0.3–3.5 times the prior pigment. It suppresses obvious source
highlights, pixels dominated by the model's specular response, silhouette
edges and weakly lit pixels. These limitations avoid directly painting bright
photographic reflections into color. Residual source shading is still possible;
multiple diffuse bounces also make the response only approximately linear.

Trial 034 applies that inferred pigment to fixed mesh UVs with view visibility
coverage. Hidden surfaces retain continuous wood, the output remains a
Principled BSDF, and no reference photograph replaces the beauty render. The
estimate has confidence above 0.5 for 296,838 pixels of 365,021 foreground
pixels, with mean confidence 0.7302. Its actual render and angular inspection
are pending; no new texture or lighting has been accepted yet.

Material-batch resource reading at 2026-11-05 08:46:03 UTC: weekly 11% used /
89% remaining, reset 2026-11-11 13:19:47 UTC. Luna continues five-minute checks.

Trials 034–036 have now been rendered and inspected at full-piece and detail
scales. None replaces the accepted checkpoint.

| Trial | High-res IoU | Original IoU | Interior form | Color | Grain | Lighting | Overall | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 034 inferred pigment | 97.904% | 97.904% | 78 | 72 | 71 | 55 | 74.78 | Reject: some local color detail returns, but the fitted lights make chalky patches across the crown and collars |
| 035 quality diagnostic | 97.905% | 97.904% | 78 | 72 | 71 | 55 | 74.78 | No acceptance: 512 samples and a separate undenoised render retain the same reflection defects |
| 036 fine grain only | 97.904% | 97.904% | 78 | 75 | 70 | 49 | 73.98 | Reject: returning to accepted lights avoids the chalky patches, but color-only grain transfer is too subtle to establish an improvement |

034/035's higher arithmetic mean does not outweigh their visible local
regressions. They are not accepted. The 036 experiment transfers only fine
luminance variation while retaining the accepted broad pigment field and
hue, with highlight/edge confidence masking. Existing coarse relief still
dominates the appearance, suggesting that normal response needs separate
attention rather than another full pigment fit.

The next isolated shape trial, 037, rounds the upper quadrant of the lowest
collar. Its lower support points and maximum radius remain fixed. The
reference shows a substantial rolled edge where the model shows a thin
horizontal shelf. Actual render comparisons will decide whether the new
curve improves it without losing the original outline.

Continuation check at 2026-11-05 09:08:57 UTC: weekly 12% used / 88% remaining,
reset 2026-11-11 13:19:47 UTC. Luna confirms the five-minute monitor is active.

037 improves the lower collar's roll but grows its back edge beyond the
source outline: high-res IoU 97.7908%, original 97.8039%. Scores 80 / 75 /
69 / 49 for form/color/grain/light, mean 74.16; reject the silhouette loss.
038 separately replaces visible relief with fine high-pass reference detail.
It leaves color and lighting unchanged, but over-breaks several reflections
and makes the polished surface look pitted. Scores 78 / 75 / 67 / 48, mean
73.18; reject. High-res/original IoU 97.9016% / 97.9025%, with unchanged mesh.

039 pulls the raised collar quadrant inward using the fixed 54-degree
projection relationship. The rolled edge remains and its excessive back
width is removed. Both outline metrics improve: high-res 97.9583%, original
97.9123%. Form rises to 80; color remains 75; local stretching of the mapped
collar grain is a small tradeoff (grain 69); the curved edge catches a more
coherent reflection (lighting 50). Working mean 74.39. This is a promising
geometry candidate, pending full validation and side inspection, not yet
the public accepted model. 040 tests a restrained physical light rig on it;
no pigment or relief changes from the accepted 026 material are included.

040 puts the main base reflection farther right, but its lights combine into
unwanted broad pale bands. Scores: silhouette 97.961%, form 80, color 73,
grain 69, lighting 54, mean 74.79; reject the bands. Original IoU 97.9109%.
The next method separates estimated warm specular highlights from the brown
diffuse field, using an explicitly artistic two-color linear decomposition.
Sixteen black-base-color light responses are diagnostic measurements of the
actual shader. Nonnegative fitting selects light strengths; the beauty image
must still be rendered normally. No reference pixels are composited into it.

041 exposed an implementation error: `Light.specular_factor = 0` does not
disable Cycles reflections in this installation. The requested separation
was not achieved, so the old reflections remained beneath the new lights.
The diagnostic `check_light_visibility.py` confirms identical reflected RGB
sum 1272.720459 with data factor 1 and 0, while setting the light object's
`visible_glossy = False` produces zero. This also means the earlier 033/040
"diffuse fill" labels described intent, not actual Cycles isolation.
041 scores remain approximately 97.959 / 80 / 75 / 69 / 50, mean 74.39;
it is not accepted. Original IoU 97.9117%.

042 repeats the fitted setup with explicit Cycles ray visibility. The script
requires binary diffuse/specular settings when that mode is enabled; older
configs retain their actual historical behavior. Reflection lights use warm
linear color [1,0.58,0.4], while the accepted white diffuse rig is retained.
This is art-directed shading, not a claim to recover a physically measured
source studio. The actual render is pending. No public asset has changed.

Pre-fit usage check at 2026-11-05 09:26:17 UTC: weekly 12% used / 88% remaining;
reset 2026-11-11 13:19:48 UTC. Five-minute monitoring continues.

The corrected separation operates, but its initial fit is too dull. A second
diagnostic verifies that turning off a light's diffuse visibility preserves
the full black-BSDF glossy response, so the separation itself is now measured.
The remaining problem is the fitted distribution, not that renderer control.

| Trial | High-res / original IoU | Form | Color | Grain | Light | Mean | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 042 corrected Cycles fit | 97.9593% / 97.9117% | 80 | 74 | 69 | 42 | 72.59 | Reject: unwanted old patches disappear, but the reference's polish and rim crescents are lost |
| 043 highlight-weighted fit | 97.9591% / 97.9115% | 80 | 74 | 69 | 44 | 72.99 | Reject: reflections strengthen somewhat but remain too weak and incomplete |
| 044 focused finial lights | 97.9593% / 97.9117% | 80 | 74 | 69 | 46 | 73.39 | Reject: some finial spots return, but spill and weak rim reflections remain |
| 045 narrower finial lights | 97.9599% / 97.9117% | 80 | 74 | 69 | 47 | 73.59 | Reject: tighter spots improve one detail without restoring the rest of the polished surface |

The three focused lights are ordinary spot emitters aimed at measured mesh
points. Their source angles are constrained and their energies fitted; they
do not project the reference photograph. The 045 fit reuses unchanged basis
responses after checking the source hash and renders only the three modified
spot responses. Its narrow beams require large fitted powers, another reason
not to treat these experimental settings as recovered studio data.

A new built-in ImageGen reflection-removal experiment was also rejected. Even
with a conservative prompt, it redraws fine grain into coarse, winding lines.
The generated image and full prompt are preserved in iteration-003 evidence;
neither reference nor the accepted material was replaced. Inspection confirms
the earlier de-lit source has the same grain defect. The next material trial
therefore derives pigment from the unchanged reference itself: estimate and
subtract its warm glossy component, divide by measured white-minus-black
shader response, and suppress low-confidence highlights and edges. It remains
an inferred 3D material with actual BSDF shading, not a photo substitute.

Pre-image experiment usage at 2026-11-05 09:44:07 UTC: weekly 13% used / 87%
remaining, reset 2026-11-11 13:19:47 UTC. The monitor remains active.

046's direct pigment estimate recovers some source grain but creates conspicuous
halos and blotches around highlights. Scores: silhouette 97.961%, form 80,
color 72, grain 68, lighting 48; mean 73.19. Reject. 047 fills uncertain
highlight areas from nearby reliable pigment before projection. It reduces
the abrupt blotches but retains halos on the finial and smooths away too much
grain on collars, socket and foot. Scores: 97.961 / 80 / 74 / 69 / 48, mean
73.79. Reject. Both original IoUs are 97.9109%; the reference remains unchanged.

The third checkpoint therefore selects **039, geometry only**. It retains
the previously accepted v2 color atlas, relief and lights. The visible benefit
is the lower collar's rounded upper quadrant, with its back edge pulled inward
to improve rather than sacrifice the fixed-view outline. Local grain stretching
on that curved band is a small documented tradeoff. Pending final side/viewer
checks, scores are silhouette 97.958%, interior 80, color 75, grain 69, lighting
50: working mean **74.39%**, holistic still about 70–75%. It is not a perfect
match. The flat parts of the other collars, broad socket shoulder, overly coarse
grain, misplaced highlights and missing fine bright crescents remain.

The second accepted model and its two fixed-view renders are preserved in
`history/queen-mission-002`. 039 passes closed/manifold mesh, positive volume
4.486084, eight tips, monotonic turned body, 54-degree orthographic camera and
unchanged height/base ratio 2.167048. The next step is regenerating all current
views and the exact viewer mesh, then checking and committing the checkpoint.

Checkpoint usage at 2026-11-05 10:01:47 UTC: weekly 13% used / 87% remaining,
reset 2026-11-11 13:19:47 UTC. Luna's monitor remains active.

The third checkpoint's final fixed-view and side renders are complete and
visually inspected. The side confirms a fuller rolled lower collar, while
the other collars and socket still need work. The material remains attached
and retains the same limitations. Actual 64-sample delivery overlap is
**97.9612% high-res / 97.9109% original**; the small difference from the trial
is render sampling/edge precision. The working mean remains **74.39%**.

Delivered model SHA-256:
`a6594fab05ae5f9c9cdbe9b32d01542129b5f6ca8825e8b16a7cb8fa0aa5b8db`.
The validated export contains the same 715,776 triangles, with exact binary
round trip, unit normals, UV seam handling and unchanged source file. Camera
checks cover 30 points over five viewport shapes with maximum error 0.0000382
pixels. Review interactions, source hashes, persistent tabs/orbit, parts-map
sandbox/CSP and side-state checks pass in the simulated DOM/GL harness.
Native browser GPU inspection remains unavailable and is not claimed.

The mission is still active. The next texture hypothesis is to remove the
coarse invented pigment variation before transferring bounded fine/medium
reference grain, while retaining the accepted broad color field. Earlier
grain-only blending left too much of the coarse source intact. Avoid another
full-color inversion until its highlight-mask artifacts are resolved.

Post-integration checks pass for eight site pages and 55 local links, the
model/viewer hash, all twelve original PNGs, candidate provenance/alignment,
parts sandbox/CSP, and all 39 protected projection-study inputs. Git whitespace
checks pass and there are no executable-bit changes. Other pieces and approved
side-gallery defaults remain unchanged. The checkpoint is ready for its local
commit; no push or hosting deployment is part of this mission.

## Fourth iteration in progress: bounded grain replacement

The third checkpoint was committed as `5ce46d1`; its local preview is exactly
synchronized and the repository is clean. Starting model SHA-256 is
`a6594fab05ae5f9c9cdbe9b32d01542129b5f6ca8825e8b16a7cb8fa0aa5b8db`.
The next trial keeps that geometry, material response and lighting fixed while
replacing coarse pigment detail. It smooths the prior pigment to retain broad
color, then adds bounded fine/medium reference grain. Obvious glossy regions
have their detail contribution suppressed rather than inverted into color.
A new fixed-coordinate high-pass diagnostic measures grain correlation in
interior regions, excluding obvious source and model highlights. It supplements
visual examination and does not replace the five-category scorecard.

Boundary reading at 2026-11-05 10:13:23 UTC: weekly 14% used / 86% remaining,
reset 2026-11-11 13:19:48 UTC. Luna continues five-minute monitoring.

048 improves high-pass correlation but suppresses too much grain, making the
collars and stem look smooth and plastic. Reject. Inspection identified an
overbroad highlight mask: the assumed two-color split classifies warm diffuse
wood as partly reflective. 049 instead suppresses only bright, relatively
neutral areas and strengthens the transferred detail. It recovers recognizable
grain, but the broad filter also transfers collar shading into dark pigment
bands. 050 couples that color to restrained reference-derived micro-relief;
the smoother highlights help locally but do not fix the bands.

051 narrows the transferred detail to a three-pixel repeated-box high pass.
It keeps more fine wood detail without as much collar shading contamination.
052 adds restrained relief to 051; its smoother, more continuous glare is less
like the reference's broken polished reflections. All five trials preserve
the exact accepted mesh and fixed-view outline (97.9612% high-res, 97.9109%
original). Candidate 051 is the strongest color-only result so far, pending
side views and texture-atlas checks; it is not yet published.

| Trial | Silhouette | Interior form | Color | Grain | Lighting | Mean | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 048 medium grain | 97.961 | 80 | 74 | 64 | 49 | 72.19 | Reject: overly smooth |
| 049 contrast grain | 97.961 | 80 | 73 | 74 | 50 | 74.99 | Reject: dark collar bands |
| 050 restrained relief | 97.961 | 80 | 73 | 76 | 49 | 75.19 | Reject: bands and smooth glare |
| 051 fine grain | 97.961 | 80 | 75 | 77 | 50 | 75.99 | Retain for further evaluation |
| 052 fine relief | 97.961 | 80 | 75 | 77 | 48 | 75.59 | Reject: reflection texture regression |
| 053 display reflection fit | 97.961 | 80 | 75 | 69 | 59 | 76.19 | Retain as lighting experiment |

These are working visual judgments, not objective recovery percentages. The
new correlation diagnostic is deliberately not averaged into the score: a
filtered photograph can correlate well while producing a visibly bad material.

053 fits the real reflection-light responses through Blender's AgX display
transform, keeping the existing diffuse rig. This avoids letting a few clipped
linear-light peaks dominate the fit. Its actual render moves the large base
reflection to the correct side and removes distracting old glints. However,
the finial spots are still poorly shaped, the socket highlight is incomplete,
and thin collar/crown crescents remain weak. It does not replace the accepted
model yet. The next test adds area-light positions derived from normals at
these missing glints and refits their powers. These are art-directed real
emitters, not an image projected as light or a claim to recover the source studio.

Boundary reading at 2026-11-05 10:33:39 UTC: weekly 15% used / 85% remaining,
reset 2026-11-11 13:19:47 UTC. Luna's five-minute guard remains active.

054 expands the display-space fit with twelve area-light responses aimed at
missing glints. It modestly improves the collar/socket placement but does not
recover the thin bright crescents. Scores stay 97.961 / 80 / 75 / 69 / 59,
mean 76.19. The next combined trial, 055, exposed a persistence defect rather
than an artistic failure: editing and repacking a reopened sRGB-tagged float
EXR converted the newly assigned linear pigment again. The saved 051 pigment
was substantially darker than the in-memory render. 055's actual render scores
97.961 / 80 / 22 / 25 / 59, mean 56.79; it is rejected. The in-memory scores
of 049–052 do not qualify those saved files for publication.

056 creates a fresh explicitly linear float image and saves EXR before packing.
Its color survives, but alpha-associated storage complicates an exact pixel
comparison (confidence was stored in the color image's alpha). 057 separates
opaque color from a grayscale confidence texture. After reopening, its color
has maximum absolute error 0.00001231 and mean error 0.000000113 versus the
generated linear input. No reference or public asset was changed by this bug.
056 and 057 both have the 051 appearance: 97.961 / 80 / 75 / 77 / 50, mean
75.99. Only 057 passes the corrected persistence check.

058 combines the reopened 057 material with the expanded fitted lights. The
full render retains the finer aligned grain and the improvement in base
reflection placement. It is a candidate for the fourth checkpoint, with
scores **97.961 / 80 / 75 / 77 / 59**, working mean **77.79%** and holistic
assessment around 75–80%. It remains visibly incomplete. The bowl still has
coarse grain from the old relief field; finial glints are elongated; the socket
crescent and thin rim/plate reflections are incomplete; collar and socket
curvature remain wrong. Some grain contrast on the crown and stem is too strong.

The color is now being baked into a v3 pigment-only atlas using the unchanged
UV layout. The old atlas remains the relief source. The lighting is an
art-directed reference rig with separated diffuse and glossy ray visibility,
not a recovered physical studio. The browser's lighting remains an approximate
real-time preview; its mesh, camera and new color atlas must match the saved
model. No failed experiment is added to public controls.

059's v3 bake preserves the 058 appearance (mean absolute foreground difference
0.3202/255; 95th percentile one channel level). Rebuilding from the archived
third model, tracked v3 PNG and recorded lights reproduces the actual render
with mean error 0.001486/255 and identical alpha. This independently exercises
the saved/reopened atlas and provides a repo-local reconstruction path.

The fourth delivery model is
`aae6d369ed42909b451be77ed0aa9e4f6731c20b338645755353290c7907e216`.
The 54-degree camera, control vertices, topology and atlas control UVs are
unchanged. The mesh remains closed/manifold with eight tips and height/base
ratio 2.167048. Original/high-res IoUs remain 97.9109% / 97.9612%.
All four current views were rendered and the wood/clay side views inspected.
The side material remains usable, but stretched inferred grain and an overly
glossy socket remain visible limitations. The working score stays **77.79%**.

The viewer export retains all 715,776 triangles, valid UV seams and exact binary
round trip. Its camera matches Blender within 0.0000382 pixels over 30 points
and five viewport shapes. Reference controls, persistent tabs/orbit, source
hashes, parts-map sandbox/CSP and side state pass the simulated DOM/GL checks.
Native browser GPU inspection remains unavailable and is not claimed.

Latest pre-sync allowance at 2026-11-05 10:55:19 UTC: 16% used / 84% remaining,
reset 2026-11-11 13:19:47 UTC. The next experiment should address regional color
and the residual coarse relief separately; geometry and thin reflected
crescents remain a later priority. Mission remains active and incomplete.

Post-integration checks pass: eight pages and 55 local links, all twelve original PNG hashes, candidate provenance/alignment, current model/viewer hash, and all 39 protected projection-study inputs. Git whitespace checks pass with existing file modes preserved. The fourth checkpoint is ready for its local commit; no push or hosting deployment is performed.

## Fifth iteration in progress: regional tone and residual relief

The fourth checkpoint was committed as `3b0ecd5`; the checkout is clean and
the local review is synchronized. Starting model hash is
`aae6d369ed42909b451be77ed0aa9e4f6731c20b338645755353290c7907e216`.
The next color-only test applies modest regional pigment multipliers: the
bowl is too orange, collars/base are slightly too bright, and socket tone is
off. Fixed-region non-highlight medians guide the direction; visual comparisons
remain decisive because the statistic does not fully separate reflection from
pigment. Geometry, UVs, relief and lights remain fixed for this trial.

061 improves most regional color medians but makes the bowl too red/muted and
the base slightly too cool. Scores: 97.961 / 80 / 79 / 77 / 59, working mean
78.59. Retain as a direction, not a delivery candidate. 063 reduces its blue
correction in the bowl and base and is awaiting examination. Separately, 062
derives fine relief from the v3 color atlas. It sharpens the glare without
reproducing the reference's irregular polished texture; scores 97.961 / 80 /
75 / 77 / 58, mean 77.59. Reject. This also clarifies that some coarse invented
lines remain in the broad color field, not only in its old relief. The next
isolated trial smooths that field more strongly before adding reference grain.

Fifth-iteration allowance at 2026-11-05 11:10:45 UTC: 17% used / 83% remaining,
reset 2026-11-11 13:19:47 UTC. Luna's five-minute monitor remains active.

063 removes 061's excess blue correction. All eight sampled non-highlight RGB
medians are now within one byte level per channel of the reference. The full
image also looks closer, though broad tonal variation and highlights still
differ. Scores: 97.961 / 80 / 80 / 77 / 59, mean 78.79. Retain for subsequent
publication checks. 064 smooths the old pigment field more strongly (radius
25 instead of 7), keeping the same fine grain and accepted rig. It produces
little convincing visible improvement; scores remain 97.961 / 80 / 75 / 77 /
59, mean 77.79. Do not promote it alone. A combined color/relief test (065)
checks whether each old component was masking the other's change.

A separate planned trial (066) starts from 063 and narrows the varnish response
without moving lights. The concrete target is the overly stretched finial
glints and weak thin edge reflections. It must be judged against the whole
image, especially the already improved base reflection, before acceptance.

065 combines the stronger pigment smoothing with the new atlas-derived relief.
The coarse pattern remains, and reflections become less like the source's
broken polish. Scores: 97.961 / 80 / 75 / 77 / 58, mean 77.59; reject.
066 narrows varnish lobes but does not resolve the stretched finial glint and
makes the socket reflection harsher. Scores: 97.961 / 80 / 80 / 77 / 58,
mean 78.59; reject in favor of 063. A diagnostic trial now removes all relief
and separately renders the pigment and its projection-coverage attribute.
Those emission diagnostics are not beauty renders or deliverable substitutes.

Allowance at 2026-11-05 11:26:38 UTC: 17% used / 83% remaining, reset
2026-11-11 13:19:48 UTC. Luna's five-minute guard continues.

067 disconnects both normal inputs. It confirms that the broad coarse pattern
is in pigment, while eliminating the irregular reflected polish makes the
result worse: 97.961 / 80 / 80 / 74 / 54, mean 77.19. Reject. Separate emission
diagnostics confirm broad visible projection coverage; fixed-coordinate
high-pass correlations of the actual pigment to the reference range from
0.82 to 0.95 in four sampled regions. The intended texture transfer works,
but loses fine detail and preserves too much broad prior grain. Correlation
alone does not justify increasing the visual score.

The fifth delivery candidate is therefore 063's color adjustment with the
previous accepted relief and lights. Its v4 bake reuses the existing UVs;
all surface experiments remain evidence rather than public alternatives.

068's v4 bake preserves 063 with mean foreground RGB error 0.1391/255 and
identical alpha. Rebuilding from the tracked fourth model and v4 PNG gives
mean error 0.00003262/255, maximum one level, and identical alpha. The saved
delivery model is
`16904dba7abc57e60ec8e6d73c30f46f9e0890ec46272753c648e7e88f64247e`.
Scores stay **97.961 / 80 / 80 / 77 / 59**, mean **78.79%**, holistic 75–80%.

Control geometry, topology and atlas UVs match the fourth checkpoint exactly.
The model remains closed/manifold with eight tips, positive volume, fixed
54-degree orthographic camera and height/base ratio 2.167048. Both reference
IoUs remain unchanged. Four actual views were rendered; wood and clay side
views were inspected. The side material retains prior grain stretching and
socket gloss, with no new shape change.

The viewer exports 715,776 triangles and 368,584 vertices including UV seams.
Its binary round trip, normals and source hash pass. Camera agreement is
within 0.0000382 pixels across 30 points and five viewport shapes. Source,
tab, persistent-orbit, parts sandbox/CSP and side-state interaction checks
pass in the simulated DOM/WebGL harness. Native browser GPU inspection is
still unavailable and is not claimed.

Boundary usage at 2026-11-05 11:39:57 UTC was 18% used / 82% remaining,
reset 2026-11-11 13:19:47 UTC. Luna continues monitoring. The next targeted
experiment will isolate broad finial reflection lights: the elongated glint
survived removal of relief, so the light rig needs examination before another
texture adjustment. The mission remains active and incomplete.

Post-integration site checks pass for all eight pages and 55 local links,
twelve original PNG hashes, candidate provenance/alignment, current model
and viewer hash, parts sandbox/CSP, and all 39 protected projection inputs.
Whitespace checks pass. The fifth checkpoint is ready for its local commit;
no push or hosting deployment is performed.

## Sixth iteration in progress: isolate reflected glints

The fifth checkpoint is committed as `b623c35`; the checkout is clean and
the local review page is synchronized. Starting model is
`16904dba7abc57e60ec8e6d73c30f46f9e0890ec46272753c648e7e88f64247e`.
Trial 070 removes the three broad finial area lights while retaining their
narrow spotlights. Separate black-BSDF diagnostic passes isolate the base
key, finial areas, finial spots, and remaining lights. The vertical base
reflector may also be contributing the elongated finial glint. These passes
will identify the cause before further tuning; they are not delivery images.

At 2026-11-05 11:48:45 UTC, weekly allowance was 18% used / 82% remaining,
reset 2026-11-11 13:19:48 UTC. Luna's five-minute guard remains active.

070 barely changes the stretched glint and weakens part of the base reflection;
it offers no convincing whole-image gain. Scores remain 97.961 / 80 / 80 /
77 / 59, mean 78.79; reject. The diagnostic base-key pass clearly contains
the long finial streak. Narrow finial spotlights make compact glints, while
other broad lights add spill. Trial 071 limits the tall base area's spread
to 36 degrees and fits only its power to preserve its prior base contribution.
It starts from the accepted model, retaining the three finial areas for an
isolated change. Geometry, pigment and camera remain fixed.

071 modestly shortens the streak while keeping the base highlight. Scores:
97.961 / 80 / 80 / 77 / 61, mean 79.19; retain as a lighting direction.
Its base light is now 10.6422 W at 36-degree spread, versus 219.036 W at
unrestricted spread; normalization changes the required power. The cached
actual-response ranking identifies upper-collar, socket and foot reflections
as additional finial spill. Trial 072 confines five such area lights to a
12-degree spread and fits each power only around its intended highlight.
This uses real emitters and leaves the material and geometry unchanged.

072 removes measured finial spill from all five constrained lights and makes
the finial glints more compact. However, it also weakens useful rim and collar
reflections. Scores: 97.961 / 80 / 80 / 77 / 60, mean 78.99; not ready to
promote. Trial 073 refits actual light powers through AgX with those confined
responses and a fresh diffuse baseline of the current v4 pigment. This should
test whether the lost highlights can be restored without recreating the spill.

073 restores some lower highlights but adds an unwanted bright stem spot and
overstates parts of the bowl reflection. Its numerical fit improves, but the
full image does not justify promotion: 97.961 / 80 / 80 / 77 / 59, mean 78.79.
Reject. 074 returns to 072 and confines the remaining targeted area lights,
while disabling three legacy untargeted glossy lights. The three diffuse
lights remain unchanged. Intended-neighborhood power fits precede another
whole-image examination; actual reference appearance decides acceptance.

Latest allowance at 2026-11-05 12:04:13 UTC: 19% used / 81% remaining,
reset 2026-11-11 13:19:48 UTC. Luna's five-minute guard remains active.

074 further reduces stray reflections but creates a wrong bright arc on the
inner bowl and leaves the crown rim dull. Scores: 97.961 / 80 / 80 / 77 / 58,
mean 78.59; reject as delivered. The final test of this direction refits the
fully constrained response set (075). If its visual result still fails, use
the narrower base-light improvement as the retained direction and revisit
surface curvature rather than continuing unconstrained power searches.

075 reduces its numerical fitting loss but again introduces pale vertical
body streaks and a false stem glint; the rim remains too dull. Scores:
97.961 / 80 / 80 / 77 / 58, mean 78.59. Reject. The sixth checkpoint retains
only 071's narrower base reflector: 97.961 / 80 / 80 / 77 / 61, mean 79.19.
This is a modest reduction in finial spill, not a resolution of the lighting
mismatch. All broader confinement/refitting trials remain diagnostic evidence.
Next examine collar/bowl curvature in neutral renders before retuning lights.

The sixth delivery model is
`82100ad9047426b1be46e72d01d769189b4e9f667005fd8c8bcc5d743c16526e`.
Its control geometry, topology and atlas UVs match the fifth checkpoint
exactly. Closed/manifold volume, eight tips, fixed 54-degree camera and
height/base ratio 2.167048 pass validation. Both reference IoUs are unchanged.
Four actual views were regenerated; the side material has no new regression.

A rebuild from the archived fifth model, unchanged v4 atlas and recorded
lights agrees with trial 071 at mean foreground error 0.00002628/255,
maximum one level, with identical alpha. The viewer retains 715,776 triangles
and exact binary round trip. Camera error remains below 0.0000382 pixels;
source, tabs, persistent orbit, parts sandbox/CSP and side state pass the
simulated DOM/WebGL checks. Native browser GPU inspection remains unavailable.
The working score is **79.19%**, holistic 75–80%, and the mission is incomplete.

Post-integration checks pass for eight pages, 55 local links, all twelve
original reference PNG hashes, candidate provenance/alignment, model/viewer
consistency, parts sandbox/CSP, and 39 protected projection inputs. Git
whitespace checks pass. The sixth checkpoint is ready for its local commit;
no push or hosting deployment is performed.

## Seventh iteration: rejected socket and reflection experiments

The sixth checkpoint is committed as `d1b806f`; its model and preview hashes
remain `82100ad9047426b1be46e72d01d769189b4e9f667005fd8c8bcc5d743c16526e`.
The actual image remains the best accepted result. Evidence and reproducible
experiment scripts for 077–081 are recorded in `queen-mission/iteration-007`.

| Trial | Outline IoU | Form | Color | Grain | Lighting | Mean | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 077 rolled socket shoulder | 97.722 | 79 | 80 | 77 | 60 | 78.74 | Reject: outline and shoulder regress |
| 078 distant reflectors | 97.961 | 80 | 77 | 76 | 55 | 77.19 | Reject: false crown/stem/socket highlights |
| 079 subtler relief | 97.961 | 80 | 80 | 76 | 59 | 78.59 | Reject: crisp but misplaced reflections |
| 080 fresh light fit for 079 | 97.961 | 80 | 77 | 75 | 54 | 76.79 | Reject: false spots and shiny bands |
| 081 circumferential polish | 97.961 | 80 | 80 | 77 | 61 | 79.19 | Reject: no convincing improvement |

The current working score stays **79.19%**, holistic 75–80%; it is not a
perfect match. Only 077 changes geometry, and its original IoU falls from
97.9109% to 97.7050%. The other trials retain both outlines exactly. Lower
numeric light-fitting loss did not produce a better-looking model. The
surface and reflected-light errors remain conspicuous in enlarged crops.

At 2026-11-05 12:58:07 UTC, Luna reports weekly 21% used / 79% remaining,
reset 2026-11-11 13:19:48 UTC. Five-minute monitoring continues. No model,
reference, public control, other piece, or approved side default is changed
by this checkpoint. Scripts ran in Blender; comparisons are actual saved
renders. Source hashes and unchanged delivery assets are checked before
committing this evidence. No push or deployment is performed.

Next test light linking to isolate regional reflections, beginning with a
render-equivalence check of temporary render partitions against the accepted
closed editable mesh. Preserve the current model unless the actual linked
render improves the reference match and all delivery checks pass.


## Eighth iteration: compact finial reflections

Start from `0390d4b`, retaining the sixth accepted model as the baseline.
Detailed evidence is in `queen-mission/iteration-008`. Broad fits using linked
reflectors (083–085) strengthened some edges but added a gray sheen and false
body highlights. Direct-only lighting and high-sample diagnostics did not
make those rigs acceptable. Their lower fitting loss did not establish a
better image. All were rejected.

| Trial | Outline IoU | Form | Color | Grain | Lighting | Mean | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 082 exact render partitions | 97.961 | 80 | 80 | 77 | 61 | 79.19 | Technique check only |
| 083 linked regional rig | 97.961 | 80 | 74 | 75 | 58 | 76.99 | Reject gray sheen |
| 084 direct-only paths | 97.961 | 80 | 74 | 75 | 58 | 76.99 | Reject; sheen persists |
| 085 full-wood area fit | 97.960 | 80 | 77 | 76 | 59 | 77.99 | Reject false highlights |
| 086 finial areas and spots | 97.961 | 80 | 80 | 77 | 63 | 79.59 | Improved; superseded |
| 087 finial spots only | 97.961 | 80 | 80 | 77 | 64 | 79.79 | Selected direction |
| 088 two receivers | 97.961 | 80 | 80 | 77 | 64 | 79.79 | Accept simplified equivalent |

088 preserves every accepted light's power but prevents 25 non-finial glossy
reflectors from directly lighting the finial. Three intended spots remain.
The long merged streak becomes three compact glints, closer to the reference.
The geometry, UVs, color and relief remain unchanged. Original IoU stays
97.9109%. The holistic assessment is still 75–80%; the mission is incomplete.

The closed editable control remains the viewer/export source. Two exact
surface copies provide light receivers for final rendering. Validation checks
positions and UVs face-for-face, smooth normals, material sharing and links,
as well as the original closed-mesh, eight-tip, 54-degree and sizing checks.
A geometry helper refuses stale receiver-bearing inputs. The side views are
regenerated with the same shared material and show no new regression.

Current model SHA-256:
`c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004`.
A clean rebuild from `history/queen-mission-006` is checked against the trial.
The six earlier geometry/light changes remain archived; failed new models
are not added to the public controls. No push or hosting deployment occurs.

At 2026-11-05 13:51:43 UTC Luna reports weekly 23% used / 77% remaining,
reset 2026-11-11 13:19:48 UTC. Monitoring continues. Next target the coarse
relief on the bowl and rim: color and relief currently derive from different
atlas revisions, and thick etched-looking lines remain unlike the reference.


The eighth checkpoint passes both review interaction harnesses, camera
regression (maximum error 0.0000382 pixels), all eight site pages and 55 local
links, original/candidate hashes and all 39 protected projection inputs.
Control positions, UVs and topology are byte-identical to the sixth model.
The reproduced render differs from the selected trial by mean
0.00002537/255, maximum one byte level, with identical alpha; the delivered
render differs by 0.00002809/255. No native browser GPU result is claimed.
The current camera-check evidence now copies the fresh build report rather
than the stale report previously left in assets; the actual check passed
against the current model hash. Earlier archived reports are left intact.


## Ninth iteration: texture diagnostics; owner-requested pause

The eighth checkpoint is committed as `7d7d55a` and synchronized to the local
preview. Six material trials (090–095) were rendered, compared at fixed
coordinates and rejected. See `queen-mission/iteration-009` for evidence,
all five scores, hashes and a mission-start/current progress comparison.

| Trial | Outline IoU | Form | Color | Grain | Lighting | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 090 current pigment relief | 97.961 | 80 | 80 | 77 | 64 | 79.79 |
| 091 no bump | 97.961 | 80 | 80 | 74 | 61 | 78.59 |
| 092 no procedural pores | 97.961 | 80 | 80 | 76 | 62 | 79.19 |
| 093 bypass atlas baking | 97.961 | 80 | 80 | 77 | 64 | 79.79 |
| 094 stronger fine grain | 97.961 | 80 | 79 | 74 | 64 | 78.99 |
| 095 subtler fine grain | 97.961 | 80 | 80 | 76 | 64 | 79.59 |

Removing bump or pores does not remove the coarse color pattern. Projection
coverage is broad in the bowl and base, and bypassing the two atlas bakes
does not provide a convincing gain. Stronger fine grain looks more etched;
weaker grain loses detail. These results corroborate earlier material
diagnoses; do not repeat them without a different, supported hypothesis.

The accepted model stays
`c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004`,
working mean 79.7922%, holistic 75–80%. Both reference IoUs, the saved camera,
viewer and local preview remain unchanged. There is no pending promotion.

The owner explicitly asks to finish the current task, then pause and chat.
The current trial recording and progress comparison are complete. Final
usage at 2026-11-05 14:16:40 UTC is 25% used / 75% remaining, reset
2026-11-11 13:19:48 UTC. Luna stopped monitoring on request. This pause is
owner-directed, not a usage threshold crossing. On resume, restart Luna and
inspect bowl/rim and collar curvature from the current profile before any
new targeted geometry trial. The mission remains incomplete.


## Tenth iteration: smaller finial seated deeper

Owner resumed the mission with a correction visible in both references.
Trial 096 reduced exposed finial height 15%; 097 reduced it 10%. Both narrowed
it 4%. The 10% version fits better and was reproduced as 098, validated, and
accepted. No body vertices, camera, UVs, pigment or light powers changed.
Render receivers were regenerated. The intentional 0.0467-unit top lowering
is documented in the adjusted height check; gallery defaults are unchanged.

Scores: silhouette 97.9583 measured / form 81 / color 80 / grain 77 / lighting
64. Mean 79.9917; holistic 75-80%. Original IoU 97.9123%. Full evidence and
checks are in iteration-010. Model SHA-256: 6bbc7d1dbeffd54e846895eb1f9f3854092c8b57d4267fa49c621e7f67e74325.

Next: distinguish bowl curvature from the broad pale rear-bowl reflection,
then test one focused correction. Coarse wood pattern remains unresolved.
The mission remains active and incomplete. The earlier monitoring/resume
instructions in historical log entries are superseded by the current mission.


## Eleventh iteration: shaped bowl reflections

The three broad bowl reflectors caused most of the misplaced pale band.
Two-light trials 100-107 improved placement but were too broad, too bright,
too weak or too isolated. Shaped eight-emitter trials 108-109 improved the
arcs but were dim. Trial 110 fits only their power through full-wood response
measurements and AgX; its actual full render provides the accepted comparison.
The bowl-region error falls 21.2%, with modest improvement to highlight shape.

All five trial scores, diagnostic images, measured responses, fitted powers
and validation are in iteration-011. Accepted scores: outline 97.9612 measured,
form 81, color 80, grain 77, lighting 65; working mean 80.1922%, holistic 75-80%.
Original IoU 97.9109%. The tenth geometry, camera, atlas and material are retained;
control vertices, UVs and topology match byte-for-byte. Side silhouettes match.
Fixed/side renders and viewer are synchronized, with all relevant checks passed.
No native browser GPU inspection is claimed. Model SHA-256:
1eb382aa47117ded52c6bb32a576fb16c24980d8f68e2f923cf9d0bcc03f19ab.

The front bowl crescent, stray upper-right reflection, collar/socket highlights,
base highlight and coarse pigment pattern remain wrong. Next inspect whether
sampling/denoising hides fine reflected grain, then address the medium-scale
pigment pattern. Do not repeat the failed broad or unshaped light trials.
The mission remains active and incomplete.


## Twelfth iteration: measured pigment correction

Trials 111-115 tested sampling, medium-scale pigment replacement and separate
coat normals without a convincing gain. Trials 116-118 instead used measured
black/white BSDF responses and one bounded actual-render feedback correction.
Strong glints are excluded; hidden surfaces retain the existing wood. Trial
119 bakes only the improved pigment into v5 and is accepted. Saved/reopened
pixels agree to within one byte, with unchanged alpha. Shape, UVs and lighting
remain unchanged. Full trial scores and evidence are in iteration-012.

Accepted scores: outline 97.9612 measured, form 81, color 82, grain 79, lighting
65; working mean 80.9922%, holistic 76-81%. Original IoU stays 97.9109%.
The owner requests updating the local page at each accepted major checkpoint;
this is now explicit in the mission. Overlay, rotating viewer and side views
are regenerated together and synchronized with the existing local preview.

Current model SHA-256: 2cb513a71cf36e6bbaa3619b95cc53208e1245f9dbefebc745470e582fc11a9b.
The prior model and renders are preserved in history/queen-mission-011.
Next inspect the overly strong relief in the base highlight, then the remaining
bowl/rim and collar/socket reflections. The goal remains active and incomplete.


## Thirteenth iteration: base junction and pigment repair

Trials 120-124 separate relief and reflected-light errors; the useful component
is the warmer, reshaped base light. A neutral render reveals a small ledge,
fixed by changing only rings 26-29 (125). Pigment-only diagnostics expose a
second dark imprint. Its initial repair looks too plain in side view (126-129),
so it is rejected until bounded medium grain restores continuity (130-132).
Trial 132 is accepted with v7 pigment, a smoother junction and one changed light.

Scores: outline 97.9612 measured, form 82, color 83, grain 79, lighting 67;
working mean 81.7922%, holistic 77-82%. Original IoU stays 97.9109%.
Shape outside four radial rings, all heights, UVs, topology, camera, finial and
gallery defaults stay unchanged. Saved/reopened and reproduced renders match
within one RGB byte. Overlay, viewer and side views are synchronized together.
See iteration-013 for all trial ratings, diagnostics, side inspection and checks.

Delivered model SHA-256: 358e327b4aa8022117af741f87dc2af835ae9bac266c3f16f42e559739987ed6.
The previous accepted model is preserved in history/queen-mission-012.
Next address the socket's fragmented highlights and missing continuous crescent.
Other shape, grain and lighting discrepancies remain; the goal is incomplete.


## Fourteenth iteration: socket crescent and local pigment repair

The misplaced white socket patch was dominated by six reflectors aimed
elsewhere. Exact receiver isolation preserves their existing action while
excluding them from the stem/socket. Ten overlapping real emitters and fitted
powers reconstruct the crescent (134-136). Two underlying pigment marks exposed
by the corrected lighting are repaired locally and baked to v8 (137-138).

Accepted scores: silhouette 97.9612 measured, form 82, color 84, grain 79,
lighting 70; working mean 82.5922%, holistic 78-83%. Original IoU 97.9109%.
Actual socket-region weighted error falls 10.9%; that is a local
supporting measurement, not whole-model fidelity. See iteration-014 for all
trial scores, native renders, diagnostics, reproduction and validation.

The editable geometry and UVs are unchanged; three exact evaluated receivers
now control lights. Fixed and side renders, viewer and local review are updated
together. Prior model: history/queen-mission-013. Delivered model SHA-256:
eac23f7c9bbead43a22ea621f2a05a0604eeeebcc13a131e53ffabaca6302223.
Next address fragmented collar highlights. The goal remains incomplete.


## Fifteenth iteration: collar reflections

Trials 140-142 were rejected for missing or misplaced glints. Retaining the
accepted illumination as a local fitting basis (143-144) lowered error, but
strengthened a secondary crown-body reflection. A bounce diagnostic isolated
that cause. Trial 145 removes secondary glossy interreflection, preserving
the actual BSDF material, geometry and fixed 54-degree camera. It is accepted.

Scores: outline 97.9612 measured, form 82, color 84, grain 79, lighting 72;
mean 82.9922%, holistic 79-84%. Original IoU 97.9109%. The actual collar crop
error falls 14.61%; that local statistic is not total model fidelity.
Four exact receivers now separate collars from the accepted stem/socket and
finial setup. Reopened and independent reconstruction checks, all comparisons,
rejected trials and persistent defects are recorded in iteration-015.

Delivered model SHA-256: 8b1c052b8c6960c6faf6760635090a7c081b04e5ad779641a4b9e49433f628c0. Prior model: history/queen-mission-014.
Local review, fixed/side renders and viewer are updated together. Next examine
collar normals versus pigment/relief; the mission remains incomplete.


## Sixteenth iteration: middle collar bevel and crescent

Only three lower-bevel radii change; all heights, peak radius, UVs and other
controls stay fixed. Six exact light receivers and measured reference-ridge
targets improve the middle crescent. Eleven local reflected fills omit cast
shadows, explicitly recorded as an artistic approximation. The v8 material
and 54-degree camera are unchanged.

Fresh saved-file renders and independent reconstruction agree within one RGB
byte. The fitting-session beauty failed repeatability and was replaced by the
verified saved-scene result; the failed evidence is retained. No acceptance
thresholds were relaxed. Uniform 256-sample silhouettes are identical.

Scores: outline 97.9612 measured, form 82, color 84, grain 79,
lighting 74; mean 83.3922%, holistic 79-84%. Original IoU 97.9109%.
Actual collar-crop error falls 18.34%; this is not whole-model fidelity.
See iteration-016 for every trial, validation, reproduction and remaining defects.
Delivered model SHA-256: fcb5255f30f89090b5c7fb3b422d15fab2d70c3db4ec478f8bd50e0367c59d94.
Prior model: history/queen-mission-015. Local review, side views and viewer are
updated together. Next inspect fine relief and reflection breakup. Incomplete.


## Seventeenth iteration: finial pigment, polish and reflections

Global coat/relief smoothing and broad bowl pigment repairs are rejected.
The accepted local repair removes negative finial glint imprints, reduces
relief only on the egg, and re-aims three real reflectors at measured reference
glints. Wider cones and explicit .30-unit emitter radii avoid clipped spots;
fitted powers preserve three distinct reflections. Exact prior-light copies
retain illumination on the body. The pigment repair is baked to v9 with all
unmasked atlas texels unchanged.

Scores: outline 97.9604 measured, form 82, color 84, grain 79, lighting 76;
mean 83.7921%, holistic 80-85%. Original IoU 97.9117%. Local
finial RGB error falls 69.21%; this is not whole-piece fidelity.
Geometry/UVs, 54-degree camera, source references and gallery defaults stay exact.
The accepted render uses 256 fixed samples and standard light sampling after repeatability failures;
the tiny silhouette-score changes are antialiasing, not geometry changes.
Saved/reopened and independent rebuild checks, packed-texture verification,
all trial ratings and remaining defects are recorded in iteration-017.

Delivered model SHA-256: cf248e4a1766fbdb1e51b7e823931bc26729531dfda4ffbda12a83ee961ad460. Prior model: history/queen-mission-016.
Local review, fixed/side views and viewer are synchronized. Next address the
bowl/rim reflection shape and grain. The goal remains incomplete.


## Eighteenth iteration - raise the flare around the socket

The owner's comparison with the original black sprite led to a higher inner flare, a 5.4% narrower socket and 19.6% less exposed socket height. The light assignments follow the original faces and two local reflections have lower power. Outline overlap is 97.9122% for the original and 97.9657% for the selected high-res. The new profile reduces lower-body image error against both. Form 84, color 84, grain 79 and lighting 76 are visual estimates. The working mean is 84.1931%. A visible difference remains in the breakup of the base highlight.

Accepted model `8420d47bbbd8cb86c1eee77e5b326f945fe57b4e3acf7d30e18414f9aa0864c6`. See [checkpoint 18](queen-mission/iteration-018/README.md) for dimensions, comparisons and reproduction.


## Nineteenth iteration — profile study, November 11, 2026

The owner allowed camera experiments and identified Chavet/Lardy as whole-set
height guides. Five purposeful variants tested the base, the stem/crown curves,
and a simple plus bounded-refitted 52-degree projection. The accepted radial
edit gives the stem a fuller waist and the crown body a more gradual flare.
All vertical proportions, base, socket, collars, bowl and finial stay exact;
the saved camera remains at 54 degrees. The base trial and both 52-degree
experiments were rejected. Neither a lower image error nor a plausible camera
alone establishes the correct geometry.

Original IoU 97.9177%; high-res IoU
97.9701%. Form 85, color 84, grain 79,
lighting 76; mean 84.3940%, holistic 80–85%. Improvements remain
modest. The socket wall, lower collar underside, finial exposure and fine
reflections still need investigation. Source and opposite-color images remain
unchanged. See [checkpoint 19](queen-mission/iteration-019/README.md) for all
five trial ratings, comparisons and validation. Model `d5882d44aa0dc3f2f72ea7449f353e530e59888fb3804ef32233544ce6feffb0`.


## Twentieth iteration — rounded lower collar underside, November 11, 2026

Four local trials compared edge rounding, a fuller stem shoulder and bounded
radius fitting. The accepted version softens only the lowest collar's underside,
keeping its crest, upper surface, every height and all other queen features.
The shoulder change was unhelpful; expanding the crest traded too much upscale
agreement for a tiny original-outline gain. All material pixels, lights, camera,
topology and UVs are preserved. Six render receivers were rebuilt and checked.

Original IoU 97.9191%; high-res IoU
97.9683%. Both are effectively unchanged;
the high-res reduction is 0.0018 percentage points. The small side-profile
improvement raises the subjective form rating from 85 to 85.5. Color 84, grain
79 and lighting 76 remain unchanged. Working mean 84.4937%, holistic
80–85%. Local image error is effectively unchanged at 256 samples; the draft's
apparent color/shading improvement was not reproduced at full quality. The
camera remains 54 degrees; gallery size defaults are unchanged. This does not resolve
the finial exposure, socket wall or highlight/grain differences.

See [checkpoint 20](queen-mission/iteration-020/README.md) for all trial scores,
renders and validation. The next examination is the finial's relationship to
the crown tips in both original and side views. Model `652bc91ad251ca5a4ea183256b45bae31c7cffe69121ba21582103d91617a63c`. Local overlay,
side renders and interactive mesh are synchronized; the mission is incomplete.


## Twenty-first iteration — lower the exposed egg, November 11, 2026

The cap's upper contour was high in both the fixed reference and side view.
The accepted change compresses control rings 108–116 by 10% toward ring 107,
with every radius and every body, bowl and crown control preserved. Actual
overall height falls 0.0380 units (0.855%), entirely at the egg. Its projection
above the crown tips reduces by about a quarter at the control profile. Three
existing finial glint reflectors follow the changed surface; their power,
color, size, shadows and links remain intact. All other 82 lights, pigment,
relief, UVs and the 54-degree camera are unchanged. Six receivers were rebuilt.

Five actual rendered trials tested the lower cap, reflection re-aiming, a
shallower bowl seat and extra contact reflections. The raised seat and new
emitters were rejected: they strengthened the upscale crescent but worsened
the original-image contact fit. A deeper-cap config was not rendered and is
not counted as an evaluated candidate. The accepted published image reproduces
the saved 256-sample trial within one RGB byte, with identical alpha.

Original outline IoU 97.9191%; high-res
97.9683%, both unchanged. Finial-crop RGB
error improves 6.03% against the original and rises 0.81% against the upscale.
Original contact-area error rises slightly while the upscale contact improves;
the small tradeoff is recorded. Subjective form rises from 85.5 to 86; color
84, grain 79 and lighting 76 stay unchanged. Working mean 84.5937%,
holistic 80–85%. This is a modest shape improvement, not a claim of a perfect
model. The contact crescent, rear-bowl glints, grain and socket wall remain.

See [checkpoint 21](queen-mission/iteration-021/README.md) for every trial's
ratings, source crops, saved-render comparison, scoped checks and reproduction.
Model `6ac2fe2309b0e6046db892be11ffbb986059228341c3b7ea140956e792de8c48`. Fixed and side renders, interactive mesh and local preview are
synchronized. The viewer uses approximate lighting; UI checks used a simulated
DOM/WebGL harness. Gallery defaults and source images remain unchanged. Next
isolate contact illumination on the unchanged accepted bowl. Mission incomplete.


## Twenty-second iteration — pigment at the egg root, November 11, 2026

Six rendered trials separated reflected light, local bowl curvature and pigment.
All seven tested central reflection rays at the accepted contact curve were
blocked by the rim; the measured light contributions were negligible. Raising
the floor cleared the rays but worsened both references, including after fitting
light powers. A half-strength floor edit also failed. Those trials are rejected.

A pigment-only diagnostic found a dark root band without scene illumination:
median linear luminance 0.00557 versus 0.02477 on the egg and 0.02587 in the bowl.
A broad correction made an orange band and was rejected. The accepted narrow
mask reduces this inferred residual shading, preserving the v9 pixels and
grain, all geometry/UVs/relief, all 85 lights and the 54-degree camera. The same
object-space color formula is included in the rotating viewer. This procedural
grade must be retained or baked when exporting to another material system.

Original finial/contact RGB error improves 17.71% / 38.14%; selected-high-res
error improves 1.99% / 4.94%. Both bowl comparisons also improve. These are
local diagnostics, not overall match percentages. Outline IoUs remain
97.9191% original and 97.9683% high-res.
Form 86, color 85, grain 79 and lighting 76 are subjective estimates. Color
rises one point; the other estimates stay fixed. Working mean 84.7937%,
holistic 80–85%. Original and opposite-color images and gallery defaults stay exact.

Saved/reopened and published renders agree within one RGB byte. Geometry,
material/light scope and camera checks pass. A diagnostic verifies the actual
Blender color mask matches the viewer formula and follows a translated piece.
Local overlay, side images and viewer share `f390b7d335ff020b47ec9eab661e21d69254db7c074832e89c3cf5b735cb27e4`. See
[checkpoint 22](queen-mission/iteration-022/README.md) for all six ratings,
rejected experiments, diagnostics and reproduction. Native browser checks are
recorded separately. The thin bright contact crescent remains unresolved, as do
rear-bowl reflections, some grain, the base highlight and socket wall. Mission incomplete.


## Direction change — side shape, November 11, 2026

The owner cleared the prior finishing goal and requested a new shape-focused
version of the same mission: lower the socket, round both faces of the bottom
collar, make the upper collar smaller/thinner with Chavet-like restraint, and
experiment with substantially compressing, broadening and lifting the base
shoulder together with the socket. MISSION-QUEEN.md now records these priorities.
Checkpoint 22 remains the accepted source. The unpromoted contact-light trials
205–209 are parked; none changes the site. The original remains authoritative,
camera experiments are allowed, and source images/gallery defaults stay intact.
No new shape or improved score is claimed by this mission rewrite.


## Twenty-fifth iteration — restrained compact base with fuller flare, November 11, 2026

Starting from the restored shelf/drop of checkpoint 24, the accepted model
compresses the coherent foot-through-socket assembly by 4% through the lower
body, then smoothly returns to the unchanged lower-collar entry. The exposed
socket wall stays horizontal and its radius is unchanged; its height is only
0.14700 to 0.14112 units. A restrained five-ring swell makes the lower flare
less triangular before it drops into that shelf. The accepted collar refinement,
UVs, material, lighting, orthographic 54-degree camera and source registration
are retained. The 6% and 10% compression trials were rejected: the strong
version was visibly squat and both harmed the source fit.

The final selected-high-res IoU is 98.0707%, an increase of 0.1351 percentage
points from checkpoint 24. The authoritative original-black IoU is 97.5207%,
a 0.2360-point decrease, so this is explicitly an owner-directed
side-profile interpretation rather than a claim of a pure source-fit win.
Form remains 86, color 85, grain 79 and lighting 76; the equal-weight working
mean is 84.7041%, with a holistic range of 80–85%. The closed positive-volume
mesh, exact receiver/UV correspondence, 82 light links and saved orthographic
camera all pass. Fixed/side renders, overlay evidence and the embedded viewer
are synchronized. See [checkpoint 25](queen-mission/iteration-025/README.md)
for profile measurements, comparison reports and validation. The active model
is `cae7d51be3faf3743a7a1180daa719477b01ba892c216de6e1e4cf8cdd03d5a3`.


## Twenty-sixth iteration — restore the shelf-and-drop baseline, November 11, 2026

The owner found the checkpoint-25 base/socket interpretation less convincing
while retaining the compact collar treatment. The active queen therefore
returns to the fully validated checkpoint-24 base, flare, raised socket, foot
and stem. Its explicit horizontal socket shelf and steep drop are restored
unchanged; the rounded lower collar and finer upper collar remain.

At the fixed 54-degree orthographic camera, the restored model measures
97.7567% outline IoU against the master original-black sprite and 97.9356%
against the selected high-resolution detail reference. That is +0.2360 and
-0.1351 points respectively versus checkpoint 25. A fully rebuilt 2% outer
shoulder draft scored 97.4066% / 98.0125%; it is rejected because the master
source regressed and the side benefit was too small.

The stored source blend was freshly validated for manifoldness, positive volume,
unchanged declared controls, six exact receiver/atlas-UV regions and 82
receiver-light links. The active blend, fixed and side renders, and embedded
viewer were regenerated together. The publisher now reads scoped validation
evidence so it verifies the actual staged model hash rather than an unrelated
repacked active file. See [checkpoint 26](queen-mission/iteration-026/README.md).

## Twenty-seventh iteration — support the lower foot, November 11, 2026

A fixed 54-degree contour audit of the restored checkpoint-26 model identified
a small, repeatable lower-foot mismatch: the outer support closed inward sooner
than both registered sources at its lowest edge. The raised socket shelf and
steep flare drop were therefore held exactly fixed. Two fully receiver-rebuilt
trials changed only rings 2–9 of the lower foot. The 0.018-unit radius peak
improved the original sprite but visibly overshot the selected high-resolution
rim, so it is rejected. The accepted half-strength 0.009-unit peak creates a
slightly flatter, more supported foot with no separate bulge.

The published saved render scores 97.8523% original-black IoU and 97.9622%
selected-high-res IoU, gains of 0.0956 and 0.0267 points from checkpoint 26.
Form remains 86, color 85, grain 79 and lighting 76; the equal-weight working
mean is 84.7705%, with a holistic range of 80–85%. The staged source validates
as closed positive volume with zero boundary/non-manifold edges, six exact
receiver/atlas-UV regions and 82 light links. The 54-degree orthographic camera
and source registration are unchanged.

The active model is `8aa9492357a703f656189ad479294c5882da3c129cfb99a120b5ee1b7a85e3b3`.
Fixed and side renders, the registered side comparison, embedded viewer mesh
and review page are synchronized. See [checkpoint 27](queen-mission/iteration-027/README.md).

## Twenty-eighth iteration — further seat the queen egg, November 11, 2026

The owner returned attention to the distinctive inverted crown and observed that the finial still read too large and exposed. Starting from checkpoint 27, the accepted trial changes only cap rings 108–116, anchored at ring 107: it compacts their height to 90% of the previous exposed cap and radius to 97%. The maximum height falls 0.034182 units, seating the egg farther into the shallow bowl while retaining an egg-like curve rather than a button. Crown bowl, rim, eight tips, collars, stem, shelf-and-drop socket, flare, foot, material, lighting, UVs and the 54-degree orthographic camera remain fixed.

A stronger 84% height / 94% radial bracket was rejected because the normal-size crown and side crops made the egg too button-like. The accepted midpoint is visibly closer to the compact, submerged egg in both the authoritative original and selected high-res reference. The stronger 0.012 lower-foot bracket and two too-subtle upper-collar brackets are also recorded as rejected; none enters the public review controls.

Both outline IoUs remain 97.8523% against original black and 97.9622% against selected high-res, as expected because the cap sits inside the crown's hole-filled silhouette. Interior-shape judgment rises from 86 to 86.5; color 85, grain 79 and lighting 76 are unchanged regression ratings. The equal-weight working mean is 84.8705%, with holistic range still 80–85%. The result improves a documented interior/crown relationship; it does not claim that the entire queen is finished.

The staged and delivered validators pass: zero boundary/non-manifold edges, positive volume, all undeclared controls identical to the composed source profile, six exact receiver/atlas-UV regions, 715,776 receiver triangles and 82 light links. The saved camera remains orthographic at 54 degrees. Fixed wood/clay, registered side images, comparison crops, the closed-control viewer export, and the embedded review frame are rebuilt from the active `dc29132cdf38208d09452185a16065bc94ee7d6be20b03f11efad193e81b8906` model. The viewer camera and reference interaction harnesses, plus static model/site checks, pass. See [checkpoint 28](queen-mission/iteration-028/README.md).

## Twenty-ninth iteration — recover a slender seated egg, November 11, 2026

Checkpoint 28’s finial was convincingly seated but the crown crop showed it as a little too squat. A narrowly scoped bracket returned part of its vertical presence while reducing its radial width. The accepted 96%-height / 94%-radius cap changes only controls 108–116, remains anchored at ring 107, and is still 0.013673 units lower than checkpoint 27. It reads as a smaller egg nested in the inverted bowl rather than a round button.

Both exterior IoUs remain 97.8523% original black and 97.9622% selected high-res because the finial lies inside the crown’s hole-filled outline. Identical-pixel crown and neutral-profile crops support the interior judgment increase from 86.5 to 87.0; color, grain, and lighting are unchanged. The working mean rises from 84.8705% to 84.9705%, with the same 80–85% holistic range. This is an interior-form refinement, not a claim of full shape completion.

The active `441f40d2ef07e5bf6c5f14380c2d7ba71c94172add6c1891da9eb399907ecea0` model passes both the scoped and delivered-model validation: zero boundary and non-manifold edges, positive volume, all undeclared controls unchanged, six exact receiver/UV regions, 715,776 receiver triangles, and 82 light links. The saved camera remains 54-degree orthographic. The synchronized viewer has 44,924 triangles and passes its camera/reference harness; static model/site checks pass too. Fixed and side renders, comparison crops, the review page, and evidence are updated. See [checkpoint 29](queen-mission/iteration-029/README.md).

### Parked base-shoulder experiment — variant 242, November 11, 2026

The fixed-camera row residuals suggested that the broad upper-base shoulder was a few pixels too wide while the accepted lower-foot support should remain intact. `242-upper-base-taper-008` therefore narrows only rings 13–21, with a 0.008-unit peak taper at ring 17; it leaves the foot, shelf/drop socket, stem, collars, crown, UVs, material, lighting, and camera untouched. Its selected-high-res outline IoU rose from 97.9622% to 98.1338%, but the authoritative original-black IoU fell from 97.8523% to 97.7936%.

The trial is parked rather than promoted. Its neutral side profile is more tapered, but it does not clearly resolve the owner’s concern about the base’s side plausibility, and the original source must arbitrate that tradeoff. The active model remains checkpoint 29. The reusable constrained study script is retained at `scripts/queen/study_base_shoulder_taper.py`; the trial blend and renders remain isolated under ignored `build/queen-mission/242-upper-base-taper-008/` evidence.

### Thirtieth profile bracket — preserve shelf/drop, November 11, 2026

The owner re-emphasized that the raised socket must keep its distinct horizontal
shelf and steep inward drop.  Three isolated drafts therefore avoid the earlier
flare bulge: a 0.003-unit upper-collar narrowing, 3/4/6% Z-only lower-assembly
compression, and 82%/70% socket-wall-height variants with the shelf radius and
stem seat exact.  None changes the active model, receiver partitions, material,
lighting, camera, source registration, or review page.

The upper-collar micro edit is not visibly distinct at normal scale.  The 3%
no-bulk compression improves the selected high-res Workbench-control IoU from
97.8050% to 97.9788% but reduces original-black IoU from 97.8423% to 97.6846%; 4%
and 6% worsen that original-source tradeoff.  Shortening the socket wall to 82%
or 70% has no meaningful selected-image benefit (97.8156% / 97.8092%) and
also lowers original fit (97.7974% / 97.7910%).  These are draft-render
directions rather than acceptance metrics; checkpoint 29's full Cycles scores
remain 97.8523% original and 97.9622% selected.

A read-only source-mask audit confirms that the selected high-res image is an
excellent but not pixel-identical scale-up: its collar crop has a +3-pixel
local vertical preference relative to the registered original, while the base
has no vertical preference.  This explains why some collar adjustments can
appear attractive in the high-res reference without establishing geometry, but
does not explain the remaining base-compression conflict.  The audit is stored
with the iteration-030 evidence and does not alter source pixels or registration.

The bracket is rejected/preserved as evidence, not promoted.  It shows that
the desired compact side interpretation can be made while retaining the
shelf/drop construction, but the current original Lichess sprite does not yet
support it strongly enough to displace checkpoint 29.  See
`docs/queen-mission/iteration-030/` for fixed-registration overlays, the neutral
side sheet, dimensions, and full decision record.  The goal remains active.

## Thirty-first iteration — flatten the lower-collar join, November 11, 2026

The rounded bottom bead still sat on a funnel-like stem transition. Two
production-subdivision drafts raised only controls 48 and 49. The accepted
0.085-unit lift at control 49 (0.01275 at 48) makes the underside flatter
without changing the bead, any radius, the socket/base, crown or egg. Both
draft alpha masks match their elevated baseline exactly. Final 256-sample
Cycles scores remain 97.8523% original and 97.9622% selected-high-res IoU.
Interior/side form rises from 87 to 88 by visual judgment; color 85, grain 79,
lighting 76 and holistic 80–85% are unchanged. The working mean is 85.1705%.

Coupled 6/10/16% whole-base compression with radial refitting kept much closer
exterior matches than the prior Z-only trials. The 10% case reached draft
97.7773% original IoU, but its actual wood render moved the socket's front lip
down and lost the source crescent. It is rejected despite its good silhouette.
Next studies must constrain that interior arc, not just the outside mask.

The accepted `f6cbac79d43ce1e894f498340da4ebb0700c87dd44d0845cf0bab56e13310442`
model is closed with positive volume, six exact receiver/UV regions and 82
verified light links. Packed material pixels, shader graph, 85 lights, camera
and transform are preserved. The height/base ratio stays 2.102978. Checkpoint
29 is archived; current fixed/side images and viewer are regenerated together.
See [checkpoint 31](queen-mission/iteration-031/README.md). The base shape
requirement remains unresolved, so the goal remains active.

## 2026-11-11 — checkpoint 32: compact base with the stem retained

Accepted a 6% shallower foot/flare/socket assembly, with a 6.2% narrower
socket wall and a broader inner flare. The shelf and steep drop remain
distinct. A first fitted proposal made the lower stem too straight; the
accepted variant restores every stem radius from ring 38 and leaves every
control from 48 upward exact. The improved collar join, collars, crown and
egg are retained. The piece stays grounded and its total height/base ratio
remains 2.102978. Camera and reference registration stay at the accepted 54°.

Final scores: original outline 97.7916%, selected high-res outline 97.9975%,
interior/side form 89, wood color 85, grain 79, lighting 76. The working mean
is 85.3583%, holistic 80–85%. The original outline loses 0.0607 percentage
points for a visibly more compact base; the high-res score gains 0.0353.
The socket crescent and base rounding still need work. These percentages
do not establish a perfect reconstruction.

A neutral 54/52/50/48-degree bracket tests round 3D geometry with unchanged
source pixels and explicit socket-arc constraints. Lower-angle fits shorten
the profile but worsen the crown/collars and source outline; none replaces
54°. The more aggressive compression and straight-stem wood trial are also
rejected. Evidence and exact proposals are in
[checkpoint 32](queen-mission/iteration-032/README.md).

The saved accepted model is
`d58316454daad02fafaacbe7ff50215f042911cbd2e1609fbc8431f1c52ab0b4`.
Checkpoint 31 is archived. Mesh, receiver UV/normal/link checks, all 85
lights and packed-material preservation pass; fixed/side renders and the
interactive viewer are regenerated together. The Queen goal stays active,
without watchers or subagents.

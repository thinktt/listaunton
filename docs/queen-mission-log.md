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

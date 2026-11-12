# King checkpoint 011 — separate collar reflections

Accepted **117-collar-fitted-reflections**, using the **fresh saved-file render**.
The repeated pale collar stripes are reduced, and the lower collar catches
warmer, separated reflections. This is a partial improvement: upper/middle
left highlights and gray pigment bands remain visibly wrong. The mission is
active and incomplete. Checkpoint 010 is archived in `history/king-mission-010`.

## Examination and decisions

The earlier light-isolation diagnostic already showed that Front/Upper varnish
create regular pale crescents. Three exact illumination regions now separate
the lower, middle and upper collars. Removing those broad sources from the
collars and fitting local real area lights improves the full image, especially
the bottom collar, without changing the editable king or its material.

| Trial | Decision | Outline IoU | Interior | Color | Grain / surface | Lighting |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 115 initial local lights | Superseded: weak or obstructed glints | 97.8174 | 84 | 82 | 79 | 64 |
| 116 split without lighting changes | Preservation diagnostic | 97.8174 | 84 | 82 | 79 | 64 |
| **117 fitted local lights** | **Accepted after fresh render** | **97.8174** | **84** | **82** | **79** | **66** |
| 118 closer lights | Rejected: unsuitable near-field reflections | 97.8174 | 84 | 82 | 79 | 64 |
| 119 fitted close lights | Rejected: isolated bright dot | 97.8174 | 84 | 82 | 79 | 65 |
| 122 measured varnish-normal targeting | Rejected: near-field artifact remains | 97.8174 | 84 | 82 | 79 | 64 |
| 123 fitted measured-normal lights | Rejected despite lower fitting loss | 97.8174 | 84 | 82 | 79 | 65 |
| 124 one-source shadow omission | Rejected: no useful visible benefit | 97.8174 | 84 | 82 | 79 | 65 |
| 125 fitted shadow-omission study | Not accepted: unnecessary approximation | 97.8174 | 84 | 82 | 79 | 66 |

Only IoU is measured; other percentages are visual judgments under the unchanged
rubric. Original-sprite IoU is **96.8338%**. The equal-weight mean is **81.7635%**,
versus 81.3635% at 010. The holistic estimate is **75–84%**, not a calibrated
probability. Diagnostics 120/121 are not final-render candidates or score gains.
See `scores.json` for exact trial values and retained images.

The foreground collar RGB error falls from 873.586 to 484.720 (about 45%). This
fixed-region squared error is a diagnostic, not a perceptual-match percentage.
The head/base/stem change little in the fixed view. Tiny indirect/sampling
changes are recorded rather than claiming every non-collar pixel is identical.
The socket crop error changes slightly from 201.006 to 201.646. The full image,
enlarged crops, both original sprite colors, neutral, side and rear views were
examined. Back/side collars are darker under this art-directed rig; inferred
hidden finish and broader lighting realism remain unfinished. The rotating
viewer uses the same geometry/pigment with approximate real-time lighting.

## Why the later trials were rejected

At the requested middle-left glint (445, 491), the model normal points partly
downward. Its reflected ray is clear at 0.08 units but blocked by the neighboring
collar by 0.12 units. Moving an emitter into that gap produced an isolated white
dot rather than the reference crescent. Increasing the emitter's width did not
fix it. The upper-left source also illuminates a different nearby part of the
curved collar more strongly than the intended point.

The queen's actual-surface capture technique was adapted for the king. Diagnostic
121 records world positions plus both pigment and coat bump normals; 122/123
aim using those measured normals. They still fail the visual comparison. The
124/125 experiment omits shadows for only one light, but adds no meaningful
visible gain. **No shadow omission, close-light change, material change or
measured-normal re-aiming is included in the accepted scene.** All six accepted
new lights retain shadows. The obstructed middle-left light fits to zero power;
the missing glint is explicitly unresolved.

This evidence suggests inspecting local collar curvature and pigment, not just
forcing more light into an unsuitable surface. It does not prove which inferred
shape is historically correct. The original sprites remain authoritative.

## Exact scene scope

The closed editable body and separate closed cross, all control positions, UVs,
float attributes, v6 pigment, packed images, material, world and camera remain
exact from 010. Physical bounds and exported geometry/camera bytes are unchanged.
The export has 70,364 triangles. The camera remains orthographic **54 degrees
above the board**; reference registration and gallery defaults are unchanged.

The three new evaluated light receivers use mean `King profile ring` intervals:
lower **[34.5, 45.5)**, middle **[45.5, 53.5)**, upper **[53.5, 61.5)**.
There are nine total body receivers. They carry exact control faces, UVs,
attributes, shared material and smooth normals; they are not replacement open
geometry for export. Existing light coverage is migrated unchanged except for
the declared exclusion of Front/Upper varnish from the collars. Every old light's
numeric, ray-visibility and shadow settings is preserved.

The six new AREA sources are 0.24 × 0.04 rectangles, 0.8 units from their target,
RGB (1, .73, .5), glossy-only, linked to their own collar. Fitted powers are:

| Collar | Left | Right |
| --- | ---: | ---: |
| Upper | 0.7849365643 | 2.6509035047 |
| Middle | 0 | 1.6873542426 |
| Lower | 5.5090874531 | 32 |

These are fitting/illumination choices, not recovered original lamp settings.

## Render consistency investigation

The initial partition-only render **failed** the 1/255 maximum-difference check:
115 pixels exceeded one level, mostly at a tiny socket seam glint; maximum
difference was 45/255 at (481, 754), with identical alpha. That failed result
remains in `partition-render-diagnostic.json`, not relabeled as a pass.

Diagnostic 120 found the untouched foot/flare/socket receiver normals
**byte-identical**. At fixed 1024 samples without adaptive sampling or denoising,
old/new socket renders agree to **2.15e-6 linear**, with both four and zero glossy
bounces. This supports sampling/denoising sensitivity rather than a surface edit.
The diagnostic settings were not silently adopted as final scene settings.

The original fitting-session beauty also differed from a fresh reopen at the
same small glint. Its image is retained as `fitting-session-render.png`.
The **fresh reopen and independent reproduction agree within 1/255**, with
identical alpha. The accepted `wood.png`, audits and review assets use the fresh
saved-file render. No tolerance was loosened to pass reproduction. Exact values
and all three image hashes are in `fresh-render-diagnostic.json`.

## Reproduction and checks

From the repository root with Blender 5.2.2:

```sh
blender --background --python-exit-code 1 --python scripts/king/collar_reflection_trial.py -- docs/king-mission/iteration-011/reproduction.json
blender --background --python-exit-code 1 --python scripts/king/export_mission.py -- build/king-mission/126-collar-checkpoint-reproduction/king.blend build/king-mission/126-collar-checkpoint-reproduction
```

The reconstruction begins from archived 010 and requires none of the rejected
trials. The accepted reproduction uses ordinary geometric-normal targeting.
Configs 115–125 preserve experiment inputs separately. Diagnostic 120 is run
with `diagnose_collar_partition.py`; 121 is generated by
`capture_collar_surface.py` using the 115 model and its documented output path.

Scope, closed components, positive volume, all float attributes/UVs/packed
textures, exact export, receiver normals/membership/routes and regeneration
pass. Both the new nine-region and earlier six-region pipelines are checked.
Fresh saved/rebuilt beauty differs by at most 1/255; exported mesh bytes match
exactly. Model hashes and source hashes are recorded alongside the evidence.

The king HTML review, fixed/neutral renders, rotating geometry and side/rear
comparison are synchronized, including all **34** files in the existing Windows
preview. Canonical model, king/candidate interactions, site/model and historical
projection checks pass. Repository and local-preview actual-page DOM/WebGL
checks pass. Native browser screenshot inspection is not claimed.

The whole-set check retains its pre-existing **knight sizing metadata mismatch**;
its three related files are unchanged since `fa0645d`. Assertions after that
failure did not execute. The whole-set check is not reported as passing.

## Remaining work

- Upper and middle left glints are missing or mislocated. Inspect their local
  curvature and pigment against both original colors before another light fit.
- Residual gray bands, uneven grain relief and smooth/patchy varnish differ from
  the selected reference. No pigment or roughness improvement is claimed here.
- Socket glint continuity/center color, base glint size and the smooth foot
  reflection remain imperfect.
- Cross seating, cavity contrast, hidden texture and side/rear illumination
  remain inferred and unfinished. Neutral-clay receiver illumination cutoffs
  are a diagnostic-lighting limitation, not holes in the closed export.

Preserve the current accepted model before further trials. Continue the full
mission; no watchers or subagents were started and nothing was pushed/published.

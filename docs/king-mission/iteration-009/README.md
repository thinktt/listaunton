# Checkpoint 009 — separated socket reflections

The owner resumed work on 2026-11-12 after diagnostic 096. Trial
`103-socket-fitted-glints` is accepted. The broad pale streak on the raised
socket is replaced by smaller, warmer left/right glints with a better
brightness balance. The editable geometry, UVs, float attributes, material,
packed images, physical dimensions and fixed 54-degree camera are unchanged
from checkpoint 007. The mission remains incomplete.

The accepted model, fixed render, rotating viewer and side comparison are
synchronized in `king-review.html` and the existing Windows preview. No other
piece or gallery default is changed. The interactive viewer retains the same
geometry and pigment with approximate browser lighting; the fixed Cycles
render is the illumination comparison.

## What changed

An exact derived socket receiver splits the former upper-body receiver at
interpolated profile ring 28. The five regions are foot, lower flare, upper
flare, socket and upper body, with boundaries at rings 8, 17, 19.8 and 28.
Every evaluated face, UV, float attribute and custom normal matches the
unchanged closed control. The control remains available for editing/export.

`Upper varnish` and `Front varnish` now omit the socket. Their other settings
and the other existing lights remain exact. Four new glossy-only spotlights
illuminate only the socket, with cast shadows enabled. Two nearby sources
shape each glint; isolated real BSDF responses are fitted through AgX to set
their powers. The lights are an artistic matching rig, not recovered original
studio settings. No photograph, emission shader or composited highlight is
used as the model render.

The unchanged foot geometry, satin mask and area reflector from 007 are
retained. Secondary glossy bounces remain enabled. No pigment or relief
changes are accepted in this checkpoint.

![Full reference, previous and current comparison](full-comparison.png)

![Socket comparison](socket-comparison.png)

## Trials and scores

| Trial | Decision | Lighting score | Finding |
| --- | --- | ---: | --- |
| 097 | Preservation diagnostic | 62% | Socket split keeps the baseline image within 1/255. |
| 098 | Rejected | 61% | Area sources create duplicate glints on the inner slope. |
| 099 | Rejected | 60% | Narrow distant sources leave the desired glints too weak. |
| 100 | Rejected | 60% | More power restores the unwanted inner-slope shine. |
| 101 | Superseded | 62% | Nearby sources separate glints; small footprints are too bright. |
| 102 | Superseded | 62% | Paired sources shape crescents, with excessive right-side brightness. |
| 103 | Accepted | 63% | Fitted powers improve separation, warmth and relative brightness. |

Every trial is scored across all five categories in `scores.json`, with its
source parameters and full render preserved under `trials/`. Lower numerical
image error alone did not justify accepting the weak highlights in trial 099.

| Category | Checkpoint 007 | Checkpoint 009 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.8171% | 97.8174% |
| Interior form | 84% | 84% |
| Wood color | 82% | 82% |
| Grain and surface | 79% | 79% |
| Lighting / reflections | 62% | 63% |
| Equal-weight working mean | 80.9634% | 81.1635% |

Only IoU is measured; the other four ratings are visual judgments. The small
outline-number variation is sampling at the alpha threshold on unchanged
geometry, not an improved shape. Original IoU is 96.8338%; the holistic range
remains 74–83%. Neither the mean nor overlap implies a complete visual match.

In the fixed socket rectangle [370,720,630,810], composited RGB MSE falls from
657.79 to 251.47, about 62%. These statistics exclude background and use
unchanged source pixels. Small changes outside the socket remain: head and
base/foot MSE rise about 0.24% and 0.35%, respectively, while collar error falls
slightly. Mean pixel changes outside the socket are below 0.74/255 in the
recorded regions. No obvious broader regression was found in full images,
feature crops, neutral, side or rear views. See `regional-measurements.json`.

## Validation and reproduction

- Saved/reopened and independent reproduction differ from the accepted beauty
  by at most 1/255, with identical alpha.
- Exported position/normal/UV mesh bytes and camera JSON match checkpoint 007
  exactly. Physical bounds, two closed positive-volume components, all original
  control attributes, packed images, material graph and source pixels pass.
- The five receivers cover the exact control surface and preserve light routes
  after regeneration. The earlier four-receiver scene also regenerates correctly.
- Canonical model, repository/local-preview viewer interactions, candidate
  interactions, site/model and historic king projection checks pass. All 34
  king preview files are hash-synchronized.
- The whole-set check retains the pre-existing knight sizing metadata failure.
  Its three relevant shared files are unchanged from the resume commit;
  assertions after that failure were not executed. See `whole-set-limitation.json`
  and `checks/whole-set.log`. This is not a king regression or a full-set pass.
- Native browser screenshot inspection is not claimed. Viewer interaction
  checks use the actual-page DOM/WebGL harness.

Reproduce from the archived accepted seventh model, using repository-relative
paths from the project root:

```text
blender --background --python-exit-code 1 --python scripts/king/socket_reflection_trial.py -- docs/king-mission/iteration-009/reproduction.json
blender --background --python-exit-code 1 --python scripts/king/export_mission.py -- build/king-mission/104-socket-checkpoint-reproduction/king.blend build/king-mission/104-socket-checkpoint-reproduction
```

The reproduction configuration contains the original source SHA, full receiver
setup, reflector placement/size/color and fitted powers. To repeat the fitting
study, use 102-config.json followed by 103-config.json with the recorded source
hash from the newly generated 102 file: Blender serialization hashes may differ
between runs, so inspect the source before updating that execution-only guard.
The recorded fit responses, `fit.json` and final reproduction preserve the
accepted result without requiring the optimizer to choose new values.

`check_socket_checkpoint.py` checks preservation against archived 007.
`check_region_regeneration.py` checks exact receiver rebuilding. Current build
order remains render/export, `validate.py`, `build_side_comparison.py`,
`compare.py`, `build_viewer.py`, and `build_candidate_pages.py --piece king`,
then affected interaction and site checks. Do not use older historical builders
to overwrite this scene.

## Remaining discrepancies

The two socket glints are still too patchy and rounded; the reference's fine
inner seam is brighter and more continuous. A gray pigment band becomes more
visible when broad reflected glare is removed. It cannot all be repaired by
light power. This checkpoint does not finish the socket.

Elsewhere, the foot shine remains too smooth, base glints differ in size and
placement, and the upper collars carry regular pale crescents. Cross seating,
collar curvature and cavity contrast need more work. Projected relief and
residual source shading remain, together with the warm side-base patch and
cross-side/rear finish. The neutral render still exposes an older receiver
illumination cutoff despite exact geometry. Hidden wood is an interpretation.

The original black and white sprites remain the geometric authority; the
selected black high-res candidate supplies detail. Their cross clipping is
missing evidence, not a reason to flatten the model. The opposite-color
inspection is geometric evidence, not a claim of a matched white material.

Next: isolate the inner socket seam and its residual pigment band before
further collar-reflection work. Preserve the accepted outer glints and foot.
The goal is active; no watchers or subagents were started.

# Bishop checkpoint 010 — socket reflections

November 12, 2026. Resumed at the owner's direction from accepted checkpoint
009. This is a small lighting improvement; the full mission remains incomplete.

The former socket reflector placed a conspicuous yellow streak below the lip
and left the reference's cream crescent too weak. It is disabled and replaced
by 17 localized, glossy-only spots following measured surface normals. They
are three units from the surface with one-degree cones. The material, texture
pixels, geometry, UVs, 54-degree camera, other lights and ray-bounce settings
remain unchanged. The final scene was saved, reopened and rendered at 512
fixed samples with Standard/None color management.

![Selected reference, previous model and current model](socket/socket-comparison.png)

## Examination and scores

| Category | Previous | Current | Finding |
| --- | ---: | ---: | --- |
| Silhouette and placement | 96.11% | 96.11% | Measured selected-reference IoU; original-white overlap is 97.79%, original-black 96.66%. Geometry and registration are unchanged. |
| Interior form | 84% | 84% | Continuous head, open slit, seated button and accepted turned body remain intact. Hidden geometry is still inferred. |
| Wood color | 84% | 84% | Pigment is unchanged. The cream lip is closer; broader tonal differences remain. |
| Grain and surface texture | 77% | 77% | Fine grain and reflection breakup are still too smooth or speckled in different areas; the side/rear pigment boundary remains unresolved. |
| Lighting and reflections | 75% | 76% | Better lip brightness/placement and a weaker lower streak. The new crescent remains too thin and uneven. |

Equal-weight working mean: **83.22% → 83.42%**. Holistic fixed-view estimate:
**75–85%**. Only silhouette IoU is a geometric measurement; the other ratings
are subjective progress estimates, not calibrated accuracy percentages.

The unchanged reference's bright lip core contains 246 pixels under the
documented mask. Its RGB error decreases from 82.09 to 45.20 /255. The whole
socket crop improves from 8.61 to 8.12; the lip crop from 15.56 to 13.43; the
lower-streak crop from 9.71 to 8.38. These are registered image diagnostics,
not substitutes for visual assessment.

There is a modest tradeoff outside that crop. Shared-foreground RGB error
across the piece changes from 7.61 to 7.72 /255; base-region error from 10.76
to 11.21, and stem error from 2.88 to 3.21. Light selection and finite sampling
also alter fine glint noise. The base glint remains visibly imperfect. The
local improvement is accepted without claiming a uniformly better image.

## Trials and findings

- 075: re-aiming and whitening the existing area light strengthens unwanted
  lower reflections. Rejected.
- 078: four measured spots make isolated glints and a false crescent on the
  stem above the socket. Rejected.
- 080: nine spots improve the intended bright core but retain that false arc.
  Rejected.
- 082: a denser arc requests half-degree cones, but Blender clamps them to
  one degree. Smaller source radii help, yet the upper arc persists. Rejected.
  The effective values are retained in the trial parameters; the capture and
  preparation tools now reject this silent clamp.
- 083: disabling secondary glossy bounces does not solve the false arc and
  darkens other details. Rejected; the accepted scene keeps four glossy bounces.
- 085/086: moving the emitters closer narrows their actual footprint while
  preserving a valid one-degree cone. The false upper arc is removed without
  changing geometry. 085 is the draft; 086 is its reopened 512-sample result.

The response passes are actual BSDF diagnostics. Their predicted composites
are labeled as predictions and were never installed as model renders.
Intermediate basis configurations 077, 079, 081 and 084 are not beauty
candidates. The 076 lamp-off configuration describes the isolation control.
The source models and reference images are preserved. Checkpoint 009 is
archived in `history/bishop-mission-009`.

The mission comparison now explicitly cleans the model alpha mask using the
same largest-component/hole-fill operation required by `MISSION-SET.md`.
The previous raw-alpha model mask and the cleaned mask differ by **zero
pixels** for the accepted baseline and this final render. The reported
silhouette values therefore do not gain from a changed scoring convention.

## Remaining work

The bishop viewer/workspace checks pass in the canonical repository and the
existing Windows preview. Model-site and candidate-page checks also pass.
The full-set check stops at an unrelated, pre-existing knight metadata hash
mismatch: committed `scale.json` expects `104c1917…`, while committed
`assets/knight/mesh.json` hashes to `530f25c4…`. Neither shared gallery files
nor knight files were changed by this iteration. Checks after that assertion
did not execute; no full-set pass is claimed. `checkpoint.json` records the
complete hashes and unchanged gallery-file checksums.

The socket crescent needs greater width and a more natural, less sparkling
texture. A faint residual lower stripe remains, including pigment and other
light contributions. Collar crescents, the broad base reflection, slit-edge
finish and fine wood relief still differ from the reference. The projected
pigment's side/rear boundary remains a significant usability defect.

Next, inspect the roughness/normal distribution across the socket lip before
adding more lights. Preserve this accepted scene while testing a broader,
smoother crescent. Continue the material-continuity investigation separately;
do not sacrifice the fixed-view fit for another unverified hidden-surface fill.

See `reproduction.json`, `scores.json`, `trials.json` and `checkpoint.json` for
commands, measured overlap, file hashes and completed validation. The review
uses the actual fixed render and matching exported model; rotating-view
lighting remains an approximation.

# King study 015 — upper-base reflections, rejected

The owner requested that the current iteration be finished and then the goal
paused. This study is closed. **Checkpoint 014 remains the accepted model**;
none of trials 165–176 replaces it. The full king mission remains incomplete.

## Findings

The lower base glint is already close in position. The larger error is the
missing upper patch below the socket. With the diagnostic threshold B>65,
G>85 on black, the reference upper component covers 1,466 pixels, centered at
(567.8, 853.6); checkpoint 014 covers only 138 pixels, centered at (567.2, 850.3).
The reference lower component is centered at (612.5, 955.1), versus
(607.6, 952.0) in the accepted model. These are threshold-dependent landmarks,
not visual-match percentages.

Actual shader-field captures show the coat normal close to the geometric
normal. Profile ring 19.8 is the flare/socket boundary; ring 28 is the socket's
upper boundary. The measured ring values agree with the receiver partition.
Two nearby portions of the base curve can reflect the same distant light,
which helps explain the repeated thin bands. The diagnostics do not establish
the original renderer, historical light rig, or a unique reconstruction.

## Trials and decisions

| Trials | Change | Result |
| --- | --- | --- |
| 165–167 | Wider cone, larger emitter, then re-aimed upper spot | Extra low streaks; rejected |
| 169–170 | Bounded coat roughness, alone and with broader light | Little benefit alone; combined result too low and banded |
| 171–172 | Three smaller glint sources, then fitted powers | Larger but misplaced/separated patch; fitting nearly removes the third source |
| 173–174 | Two broader sources, then fitted powers | Two flat bright bands remain |
| 175–176 | Broaden both material reflection layers and refit | Softer bands, but still not the reference's continuous, grain-broken patch |

The last trial's upper-base foreground RGB squared error falls from
1018.784 to 889.291. It is still rejected:
the visual shape of the highlight remains wrong, and useful grain contrast is
softened. Lower fitting error alone does not establish an improvement.
`scores.json` assesses all five categories for every rendered trial.
`regional-measurements.json` records fixed-foreground diagnostics, including
effects outside the targeted upper patch. No reference pixels were edited.

The retained checkpoint scores are unchanged: high-res silhouette IoU
97.8260%, original IoU 96.8466%; subjective interior form 85%, wood color 82%,
grain/surface 80%, lighting/reflections 69%. Equal-weight working mean 82.7652%;
holistic visual range 75–85%. Only overlap is measured. Upper platter and cross
seating, collar pigment bands, grain scale, residual baked illumination, socket
shine, base and foot finish remain visibly imperfect.

## Preserved state and checks

The model, fixed render, neutral/profile/side/rear inspections, mesh export and
camera remain byte-identical to the archived checkpoint 014. Geometry,
materials and lighting in the accepted scene therefore remain unchanged.
Source art, v6 pigment and gallery defaults retain their recorded hashes.
All 34 Windows preview files already match the accepted repository assets;
no rejected render is exposed by the review. The repository and preview viewer
harnesses, candidate harness and site/model checks pass. HTTP model/render hashes
also identify checkpoint 014. No new native-browser screenshot is claimed.
No new render/reproduction suite was run for the unchanged accepted model;
its existing successful checks remain in iteration 014. Historical projections
and the known shared knight sizing limitation were not re-tested.

Accepted model SHA-256: `47538b56ad400f77113af6a79a4fb89fc9b4532964622ca4ffcf7f3599f22ad5`.
Accepted render SHA-256: `02df7625a18d6ca5112e5f0619210f306c558063cad8b95d84ce18e9d4079ea9`.

## Evidence and reproduction

`history/king-mission-014` preserves the accepted source. The diagnostic tools
are read-only with respect to that model and the references:

```sh
python scripts/king/measure_base_reference.py build/king-mission/164-base-response-diagnostic
blender --background --python-exit-code 1 --python scripts/king/capture_base_reflection_layers.py -- history/king-mission-014/king-rebuilt.blend build/king-mission/164-base-response-diagnostic
blender --background --python-exit-code 1 --python scripts/king/capture_collar_surface.py -- history/king-mission-014/king-rebuilt.blend build/king-mission/168-base-actual-surface --crop 500 800 665 1000 --probe 550 840 --probe 568 854 --probe 580 870 --probe 576 895 --probe 608 952 --material-fields
```

Trial input JSON and render evidence are under `trials/`. Rebuild their source
dependencies in numeric order: 165–167 use `edit_base_reflection.py`; 169–170
and 175 use `local_finish_trial.py`; 171 and 173 use `focused_reflections.py`;
172, 174 and 176 use `fit_reflections_display.py`. Pass each saved input JSON
after the Blender `--` separator. These write only isolated build directories.
Trials 173 and 175 are rejected intermediate initial renders; the other recorded
beauties were reopened through `render_fixed_diagnostics.py`. No independent
reproduction or acceptance is claimed for rejected models. Large raw EXR/NumPy
diagnostics stay in ignored build storage and can be recaptured with the commands
above; their compact manifests and PNGs are tracked here.

`record_base_study_015.py` collects the study and verifies preservation without
promoting a candidate. Its score judgments are this study's recorded assessment,
not a general automatic rating function.

If the owner later resumes work, a supported but **untested** next hypothesis
is a nearer light source: changing its distance may separate reflections from
the two similar local normals without changing the accepted shape or pigment.
No such trial was started. No watchers, subagents, push or publication were used.

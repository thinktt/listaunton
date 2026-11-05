# Bishop reconstruction mission log

This mission was activated by the owner on 2026-11-05 under `MISSION-BISHOP.md`.
The owner explicitly excluded quota checks, usage watchers and polling agents.
Only the bishop is assigned here. Concurrent work on other pieces is preserved.

The original white Lichess sprite is authoritative; ungraded white candidate 3
is the selected detail reference. The camera is orthographic at 54° above the
board, with the existing image registration. Generated side and pigment images
are interpretations, not recovered originals.

## Initial examination

Baseline model: `3db345fb65a1d9579344456a717f7960f0a3894dc3a95b209cb0fe1ad52f6a3f`.
Preserved under `history/bishop-mission-000/`. See
[`iteration-000/assessment.md`](bishop-mission/iteration-000/assessment.md).

| Stage | Silhouette | Interior shape | Wood color | Grain/texture | Lighting | Mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Initial clay | 94.88 | 78 | 0 | 0 | 30 | 40.58 |
| First boxwood checkpoint | 94.88 | 78 | 70 | 64 | 54 | 72.18 |

Silhouette is selected-reference IoU; other scores are visual estimates.
The separate original-white IoU is 96.58%. Initial holistic appearance was
about 30–40%, with wood entirely absent.

## Iteration 001 — first boxwood material

The first iteration preserves the control geometry, evaluated geometry within
0.000005 model units, and the exact camera.
It introduces inferred pigment, continuous procedural wood on unseen surfaces,
varnish with fine relief, and separately controlled diffuse and reflection
lights. It also exports pigment UVs for the rotating viewer.

The generated pigment source and exact prompt are recorded in
`assets/bishop/pigment-generation.json`. The authoritative references are
unchanged. Neither an emission image nor a composited reference is used as a
beauty render: the accepted render must come from actual Principled BSDFs.

Trial and validation details are in
[`iteration-001/assessment.md`](bishop-mission/iteration-001/assessment.md).
Original-white silhouette IoU remains 96.58%; estimated holistic appearance is
65–75%. Geometry, finer grain and reflection shapes remain unfinished. Next:
measure and refine the button, base and foot against both image sources.
No claim of completion is made. The
mission remains active until the owner/authorized alerter stops it or its
visual-match criteria are met.

### Checkpoint delivery — main bishop page

The owner requested visible updates at each accepted major iteration.
`bishop-review.html` now opens the current reconstruction overlay and provides
three direct tabs: Reference overlay, Rotate model, and Reference candidates.
The model iframe and its orbit persist between tabs; original/selected/black
reference controls remain inside the overlay. The sidebar-free workspace
suppresses the embedded viewer's duplicate heading and tabs. No model,
material, camera or score changed in this delivery update.

`scripts/bishop/refresh_review.py` rebuilds both pages and can sync the
existing local preview. The iframe revision is derived from the complete
embedded viewer, including the rendered checkpoint. DOM/WebGL harnesses cover
tab commands, parent/source guards, retained orbit and comparison state,
all candidate pairs, and a usable static overlay without WebGL. This is
scripted UI verification, not native browser inspection. The shared candidate
runtime and the other pieces' main pages are left to their existing writers.

# Sixth queen mission checkpoint

The retained change narrows the tall base reflector to a 36-degree spread and
reduces its power from 219.036 W to 10.6422 W. The power is fitted to preserve
its previous base contribution after the spread changes. This modestly
shortens an unwanted finial streak. Geometry, camera, color atlas, surface
relief and the other lights remain unchanged from checkpoint five.

The rig is an art-directed reconstruction aid, not a claim to recover the
source studio. Its diffuse and glossy ray visibility is intentionally separate.
All delivered images remain actual 3D BSDF renders.

| Trial | Silhouette | Interior form | Color | Grain | Lighting | Working mean | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Fifth checkpoint | 97.961 | 80 | 80 | 77 | 59 | 78.79 | Baseline |
| 070 remove broad finial lights | 97.961 | 80 | 80 | 77 | 59 | 78.79 | No whole-image gain |
| 071 narrow base reflector | 97.961 | 80 | 80 | 77 | 61 | 79.19 | Retain |
| 072 confine five lower lights | 97.961 | 80 | 80 | 77 | 60 | 78.99 | Weak rim reflections |
| 073 refit confined lights | 97.961 | 80 | 80 | 77 | 59 | 78.79 | False stem glint; reject |
| 074 confine remaining lights | 97.961 | 80 | 80 | 77 | 58 | 78.59 | Wrong bright bowl arc |
| 075 refit all targeted lights | 97.961 | 80 | 80 | 77 | 58 | 78.59 | False body/stem glints |

Only silhouette overlap is an objective percentage. The other categories are
visual judgments, and their mean is a working progress indicator. Holistic
assessment remains approximately 75–80%; the mission is visibly incomplete.
Both reference overlaps are unchanged: 97.9109% against the original sprite
and 97.9612% against the selected high-resolution image.

Black-BSDF diagnostics show several lower lights reflecting on the finial.
Confining individual beams removes that spill, but some useful reflections
elsewhere disappear too. Refitting powers lowers numerical image error while
introducing visibly wrong highlights. Those results are rejected rather than
being scored as improvements simply because an optimizer converged.

The retained base-light adjustment is small. Finial glints still differ,
the crown rim and collar crescents remain weak, socket reflections are
incomplete, and broad pigment/relief patterns still need work. The next
iteration should examine collar and bowl curvature in neutral views before
more light-power fitting. Side grain stretching and the polished socket
remain known limitations.

Reproduce the retained rig using `reproduction.json` with
`scripts/queen/rebuild_material_checkpoint.py`. It uses the archived fifth
model and unchanged v4 texture. `071-reproduction-config.json` also supports
`place_lights.py`. Adjacent JSON reports record hashes and validation results.
Diagnostic-only images never replace the public beauty renders.

Weekly allowance at 2026-11-05 12:15:20 UTC was 20% used / 80% remaining,
resetting 2026-11-11 13:19:48 UTC. Luna continues five-minute monitoring.

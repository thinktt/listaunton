# Bishop iteration 009 — smoother base curvature and a confined reflection

Date: 2026-11-05. Starting accepted model: checkpoint 007, preserved in
`history/bishop-mission-007`. Research checkpoint `4044ea2` supplies the
preceding investigation. **This iteration accepts a modest local improvement;
the bishop remains unfinished.**

The original white Lichess bishop is authoritative. Ungraded white candidate 3
provides detail. Reference pixels, alignment, the orthographic 54° camera,
overall model height/diameter, and approved side-gallery sizes stay fixed.

## What changed

The previous base highlight was a tall yellow patch, about 16 pixels left and
20 pixels above the selected reference's bright core. Inspecting the evaluated
surface revealed a reversal in the lower flare's normal direction. Along image
column x=584 between y=940 and 1000, accumulated positive normal-tilt steps
totaled 4.70°. Increasing only profile radii 17 and 18 removes that reversal.
Every profile height and all other control rings remain unchanged. This makes
the lower flare smoother; it is an interpretation, not proof of the unknown
source model's exact curvature.

The existing base reflector is then aimed using measured surface position and
BSDF normals. A broad pale emitter puts the reflection in the right place but
creates a white streak on the foot. A smaller disk and 3° spread confine the
beam. Actual lamp-on/off renders guide a power-only adjustment to 0.1302.
The final saved scene is reopened and rendered with 512 fixed Cycles samples.
The material remains a real Principled BSDF; no image is composited onto the
beauty render. Pigment pixels, UVs, relief nodes, world and other lights remain
unchanged.

See the [base comparison](base.png), [full comparison](comparison.png),
[head comparison](head.png), [stem/socket comparison](stem-socket.png),
[50% overlay](overlay-selected.png), and [neutral render](render-clay.png).

## Scores and tradeoffs

Only silhouette is a measured percentage. The other scores are consistent
visual estimates; their equal-weight mean is a working indicator, not proof
of a recovered model or a probability of accuracy.

| Metric | Checkpoint 007 | Checkpoint 009 | Reason |
| --- | ---: | ---: | --- |
| Outside silhouette and placement | 96.20 | 96.11 | Small outline loss from the local radial change; fixed framing. |
| Interior shape and details | 83 | 84 | Smoother lower-flare curvature; upper anatomy and slit preserved. |
| Wood color and tonal variation | 85 | 84 | Broader base is slightly too dark; this regression is recorded despite the better highlight. |
| Grain pattern and surface texture | 77 | 77 | The same pigment and relief remain; no new claim of texture fidelity. |
| Lighting and reflections | 73 | 75 | Main base core is much better placed and less yellow, with excess foot spill removed. |
| Working mean | 82.84 | 83.22 | Small improvement, with explicit limitations. |

Holistic fixed-view appearance remains approximately **75–85%**. Original-white
silhouette IoU changes from 0.978785 to 0.977864; original-black IoU changes from
0.967523 to 0.966610. The selected-reference IoU changes from 0.961987 to
0.961095. These losses are about 0.09 percentage points, not changes to overall
piece scale or camera. The original's lower highlight placement supports the
local lighting improvement. Hole-filled silhouette metrics do not measure the
slit, which is examined and probed separately.

At equal 512-sample quality, the measured bright-core centroid moves from
(566.96, 974.37) to (585.02, 992.56), against reference (583.39, 994.75).
RGB error on the fixed reference bright-core pixels falls from 46.72 to
23.52 /255. Foot-region error falls from 6.63 to 6.41. However, error over the
broader base increases from 9.31 to 10.76, and over the declared main-glint
rectangle from 24.53 to 27.29. The smaller, better placed core does **not** mean
the whole illuminated patch matches. These measurements inform the visual
decision; they are not selectively presented as aggregate numerical progress.

The upper piece remains visually unchanged: mean before/after RGB difference
is 0.07 /255 and the 99th-percentile channel difference is 1. The saved material
atlas is unchanged. See [base diagnostics](base-statistics.json),
[regional statistics](material-statistics.json), and [curvature measurements](curvature-comparison.json).

## Examined trials

Every beauty candidate has all five scores in [trials.json](trials.json),
alongside native render hashes and original/reference outline measurements.

| Trial | Finding / decision |
| --- | --- |
| 067 | Two-radius curvature change only. Better surface continuity, but old light no longer fills the reference core; not accepted alone. |
| 068 / 069 | Measured placement and cream color; 069 is the reopened 512-sample check. Reject this lighting because of foot spill and broader tonal regressions. |
| 070 | Larger, whiter disk gives a stronger core but an obvious extra white foot streak. Reject. |
| 071 | Small disk with 3° spread removes that streak; core remains too weak. Continue with measured power fitting. |
| 072 | Lamp-off BSDF control, not a proposed beauty result; used only to measure 071's contribution. |
| 073 / 074 | Fitted power in 073; 074 is its reopened 512-sample verification. Accept with the tonal/outline tradeoffs above. |

The clean render's core is stronger than the draft's. Finite-sample and
denoising differences remain visible; 512 samples is not claimed to establish
complete convergence. Rejected models are not added to the public controls.

## Preservation and validation

The dedicated base audit checks only radii 17/18 changed, every control height
is exact, and topology, UVs, modifiers, cutter, bounds and upper evaluated
geometry are preserved. The existing foot/button declaration is retained.
The rounded-slit audit runs on the unchanged upper-geometry source, with the
new base audit establishing inheritance to the current model. Current-model
ray probes separately verify the open slit and rounded floor. Both visible
components remain closed, positive-volume meshes with the accepted intersection.

The light audit checks that only declared properties of the existing base
lamp changed. The final scene has packed pigment pixels equal to the atlas,
unchanged color management, and the saved 54° camera. Mesh export, UVs, normals,
button join, source hashes, viewer and workspace checks are recorded in
[checkpoint.json](checkpoint.json). Side, rear and neutral views come from the
same saved model. UI checks use the simulated DOM/WebGL harness; no native
browser inspection is claimed.

At acceptance the repository's bishop page and existing Windows preview are
refreshed together. Reference overlay, Rotate model and Reference candidates
remain the three workspace tabs. Other pieces and historical projections are
preserved. Reproduction commands and exact accepted hashes are in
[reproduction.json](reproduction.json) and [scores.json](scores.json).

## Remaining discrepancies / next step

The broader base illumination is still too weak and its bright core too compact.
The socket has a thin lower glint that does not belong in the reference and
lacks the full cream crescent around its upper lip. Collar reflections remain
too narrow/yellow; button and slit-edge glints lack the reference's detailed
breakup. Fine grain relief is too smooth in places. Reference-derived pigment
still creates a conspicuous transition and false tonal bands in side/rear views.
The opposite-color check establishes shape agreement, not a finished black material.

The owner requested a pause after finishing this checkpoint. On resumption,
isolate the socket reflector's upper crescent and unwanted lower streak
using actual surface normals and light-only response. Retain this checkpoint
as the comparison baseline; do not erase the recorded base-tone regression
or declare the material complete.

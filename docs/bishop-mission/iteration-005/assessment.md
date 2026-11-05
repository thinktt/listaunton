# Bishop iteration 005 — reduce light spill and restore wood color

Starting checkpoint: `612517d`, preserved in `history/bishop-mission-004`.
This iteration keeps the geometry, deep slit, seated button, proportions,
54-degree orthographic camera and source registration fixed. It changes the
lighting and recalibrates the inferred pigment under that lighting. Ungraded
white candidate 3 remains selected; original Lichess images remain authoritative
and unmodified.

## Findings and accepted changes

Independent Cycles light passes identify the socket and base reflectors as
the main named-light contributors to the unwanted glare below the slit.
Simply reducing their powers would also dim useful highlights on the lower
piece. Their emitter spread is now 30 degrees. Measured BSDF responses set
the new powers to preserve each intended glint while reducing light spill
onto the head. The primary-region response difference is approximately
9.45% for the socket and 3.20% for the base, rather than assuming that spread
preserves illumination automatically. Exact regions and powers are recorded.

The previous white environment also produced a broad gray reflective edge.
The world now supplies the same diffuse illumination but zero illumination
to glossy rays. All area-light positions, shapes and colors remain unchanged
from checkpoint 004, including its accepted button reflectors. The two lower
lights alone change power/spread. This is an inferred artistic rig, not a
claim about the original renderer.

Removing that reflection darkened some wood regions. A subsequent measured
black/white BSDF response fit restores the color under the revised lighting.
Its pigment adjustment is bounded to 0.8–1.8 times the prior pigment with
maximum blend weight 0.85. Strong reflections, clipped colors, unreliable
inverse colors and silhouette edges are excluded. The fitted pigment is
baked to the existing UV atlas, input-image preservation is checked, the
Principled BSDF is restored, and the model is saved and reopened before its
96-sample final render. No photograph or emission image replaces the beauty
render.

## Scorecard

| Metric | Previous | Current |
| --- | ---: | ---: |
| Outside silhouette and placement | 96.20 | 96.20 |
| Interior shapes and carved details | 81 | 81 |
| Wood color and tonal variation | 84 | 85 |
| Grain pattern and surface texture | 77 | 77 |
| Lighting and reflections | 66 | 72 |
| Equal-weight working mean | 80.84 | 82.24 |

Only silhouette is measured IoU; the other percentages are subjective visual
assessments. The mean is a working indicator, not proof or probability of
fidelity. Holistic fixed-view appearance remains approximately **75–85%**.
The bishop is still unfinished, particularly from the side and rear.

The lighting increase reflects the removal of the distracting lower-head
glare and gray edge, while preserving the main lower highlights and accepted
button reflections. Regional color is closer after the pigment correction.
The existing grain/relief and geometry have not earned higher scores. Exact
IoUs, hashes and shared-foreground RGB diagnostics are in `scores.json`,
`metrics.json`, `material-statistics.json` and `checkpoint.json`.

Shared-foreground mean RGB error decreases from 7.78 to 7.14 /255. In the
lower-head glare crop it decreases from 9.98 to 6.46 /255. These diagnostics
exclude background and eroded boundaries and combine shape, color and lighting
error; they are not fidelity percentages.

## Rejected continuity experiments

The rear still shows a bright reference-derived pigment patch against darker
wood. A periodic harmonic color fill constrained by visible UV colors was
tested instead of the earlier uniform or per-profile fills. Its conservative
mask left the boundary substantially unchanged. A second version reduced
protection at grazing angles, using a baked smooth-normal facing weight,
while preserving well-facing texels exactly. Its actual front and rear
renders also failed to remove the patch convincingly. Neither extension is
in the accepted atlas.

This changes the next action: more hidden-only filling is not supported by
these results. Part of the boundary lies within material constrained by the
reference view. It requires revisiting inferred pigment and the geometry/
illumination that produced it, rather than claiming the unseen texture is
solved. The rejected scripts and concise evidence remain reproducible.

## Trial decisions

Scores use silhouette / interior / color / texture / lighting. Small draft
alpha differences reflect sampling; no geometry changed.

| Trial | Scores | Decision |
| --- | --- | --- |
| Body reflector response capture | — | Diagnostic light passes, not a beauty candidate. |
| 036 dark glossy environment | 96.20 / 81 / 82 / 77 / 69 | Useful edge correction; reject as final because wood becomes too dark. |
| 037 confined lower reflectors | 96.20 / 81 / 82 / 77 / 71 | Lower-head glare reduced while main lower glints are retained; still needs color correction. |
| 038 bounded pigment correction | 96.20 / 81 / 85 / 77 / 72 | Retain for baking and reopening; front color restored with cleaner lighting. |
| 039 conservative harmonic fill | — | Atlas/scene preparation only; not judged as an actual beauty render. |
| 040 isolated bake and reopened render | 96.20 / 81 / 85 / 77 / 72 | Accepted after validation. |
| 041 grazing-angle harmonic fill | 96.20 / 81 / 85 / 77 / 72 | Reject: no convincing rear continuity gain, despite preserved front fit. |

## Remaining discrepancies and next step

- The slit ends with a squared/faceted visible floor rather than the finer
  tapered end in the reference; its interior still needs geometric examination.
- Collar and foot reflections remain too narrow, smooth and gold. The upper
  head reflection and button glints lack the fine broken pattern of the target.
- A small bright point at the reference slit tip is not yet reproduced.
- The stem/socket still have an unwanted narrow reflection, and some pigment
  retains shading from an estimated camera/light arrangement.
- The side/rear pigment patch remains. The wood is not yet a convincing
  continuous material from every angle, and fine relief is not fully aligned
  with the color grain.

The next geometry hypothesis is to inspect the slit termination in clay and
both originals, then refine that local cut if the evidence supports it.
This can improve a visible internal shape without moving the outside profile
or changing accepted proportions. The remaining material and reflection
issues stay part of the mission, not deferred completion criteria.

## Validation and delivery

Final rendering uses the actual saved and reopened model at 1254 square and
96 samples. Packed pigment equals its saved PNG; the bake checks that its
inputs were not overwritten. Geometry, UVs, fixed camera, source image hashes,
slit and button contact are checked by the current bishop validators. Fresh
clay, profile, head and rear renders come from the same accepted model.
Exact comparison tolerances and current check results are in `checkpoint.json`.

At acceptance, refresh `bishop-review.html`, its embedded model viewer and
the existing local preview. Candidate choices, tab state, wipe controls,
approved gallery sizing and historical projection pages remain intact.
The overlay is the real Cycles render; rotating-view lighting is approximate.
UI checks use the simulated DOM/WebGL harness, not native browser inspection.
Only bishop work is committed; the queen and other pieces remain untouched.

## Reproduction

Use an isolated copy: `bake_mission.py` writes the bishop atlas in `assets`.
Start from `history/bishop-mission-004`, apply `lighting-036.json`, then the
recorded `lighting-037.json`; capture material response and apply the bounded
fit before baking. `reproduction.json` supplies exact script arguments,
source/reference hashes and settings. Optional response/continuity measurements
are documented separately from the accepted build sequence.

# Bishop geometry checkpoint 017

The owner started a new geometry-focused goal on November 12, 2026. This resumes
modeling from accepted checkpoint 015. It does **not** change any mission file
or declare the full material/lighting reconstruction complete.

The previous work relied too heavily on exterior overlap and reference-derived
pigment. The neutral surface reveals mismatches that the wood colors can hide.
This pass examines the actual turned profile, saved mesh, unchanged registered
originals and selected white candidate 3 independently of that pigment.

## Accepted changes

- Narrow the rear base shoulder and retain its original control heights. A
  small lower-turn correction keeps the transition rounded in side view.
- Narrow the stem conservatively, retaining its monotonic taper into the socket.
- Lower the small upper collar slightly. Keep the other collars, head, button,
  slit cutter, socket and foot controls unchanged.

The exact 23 changed controls are in `profile-fit.json`. Every unlisted control
is checked against the archived model. Overall height, widest base diameter,
54-degree camera, registration, source pixels and gallery defaults stay fixed.
The two render receivers are regenerated from the altered body; original light
links are restored. The pigment atlas, material nodes, lights and UV controls
remain unchanged. This is a geometry checkpoint with an unfinished inherited
finish, not a new material fit.

## Evidence and rejected alternatives

The base-shoulder half-width error against the original white falls from
9.559 to 2.167 native comparison pixels over rows 610–794 (1,254-pixel canvas).
Its maximum falls from 28.5 to 5 pixels. This is a regional outline diagnostic,
not an interior-form score. Stable whole-image overlaps are 98.590% against
original white, 97.688% against original black, and 96.814% against selected
white candidate 3. The original settles disagreements with the enlargement.

The first radius-only proposal left the upper shoulder too broad. A stronger
radius-and-height fit improved overlap further but produced an angular side
profile. The final profile retains a rounded lower turn and accepts a small
outline cost. An unconstrained stem fit also produced an unwanted bulge near
the socket; a constrained version and then half of its displacement are better.

The first upper-collar interpretation mistook the photographed shadow trough
for the physical rim. The stronger move put the actual rim at y=515.899, into
that shadow. The independent evaluated-mesh measurement puts the old rim at
y=505.929 and the accepted rim at y=510.914. The approximate photographed rim
is above its dark trough; it is not a perfectly recoverable single-pixel target.
This correction is deliberately smaller than the initial neutral-shadow fit.

`trials.json` records the rendered alternatives and five-category assessments.
`neutral-collars.png`, `neutral-body.png`, `side-comparison.png` and `comparison/`
show unchanged-framing comparisons. The static contour images measure exterior
placement only; inspect the slit and internal turned surfaces separately.

## Assessment

| Category | Previous 015 | Current 017 | Interpretation |
| --- | ---: | ---: | --- |
| Selected-reference silhouette | 96.11% | 96.81% | Measured filled-mask overlap |
| Interior form | 84% | 86% | Local stem/collar/base improvement; subjective |
| Wood color | 86% | 83% | Unchanged pigment is displaced by the shape change |
| Grain and surface | 78% | 77% | Inherited grain and broad shading remain imperfect |
| Lighting and reflections | 77% | 72% | Old reflectors no longer follow all changed surfaces |

The equal-weight working mean is 82.96%, below the previous 84.22%; the holistic
appearance remains roughly 75–85%. This tradeoff is explicit: the owner asked
for shape first. It would be misleading to award a higher full-image score just
because the geometry improved. Checkpoint 015 remains available for rollback.

Remaining geometry questions include the middle/lower collar cross-sections,
socket lip and base-groove rounding, and the slit edge/floor profile. The head
and button were preserved this pass, not proven perfect by preservation. The
neutral and actual-mesh checks must continue before accepting those regions.
The old pigment contains some photographic illumination, side/rear transitions
are still apparent, and glare is too localized. Those are later finish work.

## Validation and review

The new scene was saved, reopened and rendered at 512 fixed Cycles samples;
the neutral diagnostic uses the same geometry and camera without pigment/bump.
Both mesh components are closed with positive volume. Through-slit probes,
solid floor, head curvature and direct button/head contact pass. The button has
no exposed pedestal or gap. This is still two intersecting closed components,
not a fused manufacturing solid.

Independent scope validation checks all intended and unintended vertex changes,
topology, UVs, cutter, button, packed pixels, materials, lights and camera.
Receiver faces cover the body exactly once and agree with its evaluated surface.
The exported viewer has 136,664 triangles and carries the current model hash.
Its saved-camera reprojection error is below 0.000009 pixels on sampled vertices.

The review adds a Neutral/Boxwood surface choice and defaults to Neutral during
this geometry phase. Both fixed images and the rotating mesh come from this
same model. Surface changes preserve reference choice, opacity, framing and
orbit; the fixed neutral overlay also works without WebGL. Both bishop runtime
harnesses pass, including source checks and existing comparison interactions.
Native browser inspection was unavailable; no browser visual QA is claimed.

See `reproduction.json`, `validation/`, `scores.json` and `checkpoint.json` for
commands, current hashes and delivery verification. No mission, other piece,
reference, shared sizing setting or source alignment is edited. No quota
monitoring, subagents, push or publication. The geometry goal remains active.

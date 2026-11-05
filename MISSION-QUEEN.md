# Queen reconstruction mission

## Objective and activation

Refine the accepted queen's actual geometry, wood material and lighting until
its fixed-view render matches the selected reference as closely as can honestly
be assessed. Examine, modify, render, compare, score and repeat. A matching
outline alone is not success. Produce a usable 3D chess piece.

This mission covers only the queen. Creating this file does not start or
resume a goal, launch agents or modify a model. Follow the current owner-directed goal state.
When explicitly activated, use an appropriate goal or assigned subtask pointing
to this file. Do not invent a token budget or mark another unfinished goal
complete merely to replace it.

Sustained iteration and concentrating on one score at a time are authorized.
Choose tools by their usefulness to the visual result; the current material
setup is not a constraint. Creative tools and interpretation are authorized: procedural wood, generated
texture assets, reference-derived pigment, texture painting, custom UVs and
combinations. Develop grain, color, pores, relief and polish together. Keep
references unchanged, separate lighting from pigment where practical, and
inspect other angles so the material remains usable on real geometry. Never
substitute a billboard or composited photograph for an actual BSDF render.
Continue until completion, an execution/token limit, or owner stop. A plateau requires a new supported hypothesis.

## Accepted baseline and references

- Repository: `/home/toby/code/listaunton` in Ubuntu-24.04 WSL.
- Model: `models/queen/queen-rebuilt.blend`.
- Model SHA-256 at drafting: `c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004`.
- Primary original: `references/lichess-staunton-3d/Black-Queen.png`; consult the opposite color too.
- Selected detail reference: `assets/queen/reference.png` — existing selected image.
- Review page: `review.html`.
- Scripts: `scripts/queen`; assets: `assets/queen`.
- Side guide: `assets/queen/concepts/side-01.png` and this piece's entry in
  `assets/side-views/manifest.json`.

Read AGENTS.md, current piece build notes, Git status and the latest mission
log before work. Refine the latest accepted model; the recorded hash is a
baseline, not a command to undo subsequent accepted work. Do not restart from
scratch or restore rejected alternatives without owner direction.

The original Lichess sprite is the ultimate source of truth. The selected
high-res image supports precise detail fitting. Record conflicts and prefer
the original. Imagined side renders guide style and plausible side proportions;
they do not override the elevated original. Verify selections against
`docs/reference-selections.md`; later explicit owner choices take precedence.
Preserve reference pixels, hashes and registration. Never warp, retouch,
recolor or replace a reference to improve a score.

## Camera and proportions

Keep the reference camera orthographic, **54 degrees above the board**. This
is the owner's assumption, not a historically recovered fact. Keep framing,
scale and registration fixed during an iteration and compare identical pixels.

The approved displayed queen height is **83.4% of king**. Preserve
`assets/side-views/defaults.json`, shared foot baseline, gallery order and
uniform image scaling. These are presentation conventions, not independently
measured physical dimensions. Use the existing original-sprite base-width and
model-height normalization to translate them into model dimensions; do not
apply slider percentages directly to mesh scale. Preserve established sizing
tolerances and historical projections. Do not change other pieces to disguise
a discrepancy in this one.

## Feature examination

Compact egg finial seated in a shallow bowl; continuous splash-like crown; eight tips, flattened rim intervals; compact rolled collars; socket and base transitions.

Establish a fresh baseline: historical findings are inspection priorities,
not proof that every defect persists. Inspect full silhouettes and enlarged
head, collar, stem/socket, base and foot crops, including openings and negative
space. Compare wood and neutral renders to distinguish shape from shading.
Inspect grain direction and scale, distinctive markings, regional wood color,
pores, relief, varnish variation, cavity shadows and reflected crescents.

Geometry is shared between black and white originals; finish differs. First
match the selected reference finish. Record opposite-color checks separately;
a selected-color score does not establish that both finishes match.

## Stable scorecard

Rate every category after each candidate, even when only one was targeted.
Maintain separate scores for all six pieces; never transfer the queen's scores
to unexamined models. Use the same rubric throughout.

| Metric | Examine |
| --- | --- |
| Outside silhouette and placement | Actual rendered alpha, outline, head, neck, collar, base and foot boundaries at fixed registration |
| Interior shapes and carved details | Piece-specific anatomy and carving, openings, thicknesses, curvature and transitions |
| Wood color and tonal variation | Regional hue, saturation, light/dark distribution and transitions |
| Grain pattern and surface texture | Grain scale, direction, distinctive markings, pores, relief and polish variation |
| Lighting and reflections | Highlight position, shape, size, brightness and sharpness; shadows and edge reflections |

Silhouette is measured IoU; other percentages are subjective visual assessments.
Use an equal-weight mean of the five scores as a working progress indicator,
not a probability or proof of fidelity. Report a holistic visual range too.
Exclude empty background pixels from material statistics. Explain each score
change with actual visible evidence; lower numerical fitting loss is not an
automatic improvement. Record rejected trials honestly.

Use the existing fixed reference-mask convention: max RGB >12 and alpha >127,
largest component and holes filled; model alpha >127. Record original and
selected-high-res IoUs separately. Verify masking for each reference without
quietly changing thresholds between trials. Use
`scripts/queen/compare_finished_queen.py` for the established queen comparison. Note source cropping and genuine
openings; hole-filled silhouette metrics do not assess the bishop slit or rook
interior, which need separate detailed inspection.

Current accepted scores: 97.9612 / 80 / 80 / 77 / 64; working mean 79.7922%, holistic 75-80%. Original IoU: 97.9109%. Accepted model commit 7d7d55a; latest modeling evidence 103dac6. Preserve the existing queen mission history and never revive rejected reconstruction 2cb3cfd. Re-examine before changing these scores.

## Historical baseline and detailed inspection checklist

This audit predates the accepted checkpoint above. Preserve it as inspection
history, not a claim that every defect still exists or an instruction to
restore the old model. Recheck each item against fresh renders.

The original starting revision was `3096e84`, restoring `cd6dfcd`. Its
height/base-diameter ratio was approximately 2.1799 under the documented
cross-piece normalization. Original scores were silhouette 97.91% measured IoU,
interior shape 70%, color 60%, grain 30%, and lighting 40%; the working mean was
59.58%, with a holistic estimate of 55-65%. These are historical scores, not
the current accepted scores.


The baseline audit was performed on the restored model at the saved 54-degree
camera. Its reference SHA-256 is
`bc510a8f5fff0a1e51fd913f1cf4f4707849d68c5d4dabc8ce6df16cc2e1423a`;
its starting Blender SHA-256 is
`eb7daec22f35f4c282e9e41ac2e1a5eb26b2169b8b30f49673a0d0878b81dcc4`.

### Shape

- Finial is too tall and tapered; the reference has a compact egg partly
  seated in the bowl.
- Bowl reads as a steep funnel instead of the reference's softer depression
  and defined circular hollow around the finial.
- Crown-tip shoulders are too swollen and soft.
- Rim needs flatter faces between tips and the pinched transitions visible
  across the front; the current rim reads as rounded lumps.
- Crown body extends too far downward into the collar assembly.
- Collars read as broad shelves with beveled edges. The reference has compact
  rounded plates with rolled edges and dark recesses. The upper collar is
  under-expressed, and the internal curves miss their reference positions.
- Lower stem/socket transition is too broad and soft; the socket reads as a
  swollen drum instead of a tighter rolled shoulder and compact front wall.
- Base width is close, but curvature, the small lip above the groove, and
  the transition into the foot still differ.

### Wood and surface

- Color is too uniform; reproduce the reference's regional golden orange,
  reddish brown, and dark chocolate rather than one overall color correction.
- Crown body is substantially too bright relative to the reference.
- Grain is too fine, dense and repetitive; larger sweeping lines and
  irregular dark markings are missing.
- Grain flow differs across the crown, collars, and flared base.
- Distinctive base markings, crown mottling, and finial grain are absent.
- Surface relief is too smooth; small pores and irregularities should break
  reflections in the same way as the reference.
- Polish is too uniform; reproduce local variations in gloss/roughness.

### Lighting

- Reflections are too broad and blurry, particularly on the finial and rims.
- Bowl reflection is misplaced on the left wall; the reference's important
  highlight curves behind the finial.
- The model has a broad pale patch on the right collars absent from the
  reference.
- Base has two diffuse front patches instead of the stronger textured
  highlight toward the reference's right side.
- Recesses under collars and around the foot are insufficiently separated,
  while the back-right bowl has an inappropriate strong dark patch.
- Thin bright crescents on the socket, collar rims, and foot are missing.

Some apparent shape differences are amplified by shading. Use both neutral
and wood renders before deciding whether geometry, material, or lighting is
responsible. Confirm each initial finding against fresh renders as work
progresses; do not treat this backlog as immutable measurements.

## Iteration loop

1. **Recover state.** Read the latest mission log, inspect
   Git status, and identify the current best accepted revision. Respect other
   work in the checkout.
2. **Examine.** Inspect the actual high-res reference and current fixed-camera
   wood render side by side, at 50% overlay, and as enlarged piece-specific head, collar,
   stem/socket, and base crops. Check the neutral render, original sprite,
   and side guide. Do not judge a blended overlay alone: it can hide defects.
3. **Choose a concrete improvement.** Select one dominant mismatch or a
   closely related group. Record what is wrong, the intended change, the
   targeted score, and what would count as a visible improvement. Prefer
   changing geometry, material, or lighting separately when it helps isolate
   the cause. Use a small number of purposeful trials, not an indiscriminate
   render sweep.
4. **Modify and render.** Change the actual Blender model/material/lights and
   their reproducible scripts. Use draft renders for decisions and a clean
   render for acceptance. Keep the 54-degree camera fixed. Do not substitute
   a reference photograph, billboard, or composited image for a real model
   render. Reference-derived texture work must remain a usable 3D material.
5. **Re-examine and score everything.** Compare the new render against both
   the reference and the prior best at identical framing. Recompute outline
   metrics; rate all five categories and the overall result. List persistent
   defects and any regressions. Distinguish measured results from estimates.
6. **Accept or revert.** Keep a candidate only when the visible fit improves
   without a material regression in the original-image match or accepted
   proportions. Document any small tradeoff. Revert failed trials without
   disturbing unrelated work; keep brief findings, not extra failed models
   in the public review controls.
7. **Validate and synchronize accepted changes.** Follow the current build
   guide. Check mesh integrity, saved camera, viewer mesh/hash, both reference
   comparisons, and the review page. Regenerate side renders and viewer assets
   from the same accepted model. Run relevant site/interaction checks when
   their assets change; preserve historical projection studies and the
   parts map's sandbox/CSP. Keep edits scoped to the assigned piece; preserve gallery defaults.
8. **Checkpoint and commit.** Record the scores and evidence in the mission
   log, then commit the completed, checked iteration with the required actual
   model co-author trailer. Do not push or publish. Update the existing local
   preview when needed so it shows the same accepted assets as the repository.
9. **Re-examine and repeat.** Select the next discrepancy. A plateau calls for a different
   hypothesis, not a declaration of perfection.

Keep iteration records in `docs/queen-mission-log.md`, created on the first
execution. Store useful evidence in `docs/queen-mission/iteration-NNN/` or an
equally clear repo-local location. Each record should contain:

- Date, iteration, starting/best revision, and model/reference hashes.
- Hypothesis, targeted metric, concrete changes, and render settings.
- All five before/after scores, original and high-res IoU, overall score,
  remaining discrepancies, regressions, and acceptance/rejection reason.
- Comparison images, actual validation results, and the next specific step.

Checkpoints must distinguish completed work from unrendered or unvalidated
changes. Rejected experiments must not displace the best accepted result.

## Validation, coordination and delivery

Follow the current queen pipeline, not obsolete history scripts. Check finite
geometry, intended topology/components, normals and UVs; apply closed/manifold
checks where appropriate. Verify openings and intentional intersections rather
than imposing another piece's construction. Preserve the accepted baseline
until candidate validation passes. Reopen saved materials to check texture
packing and color, not only an in-memory render.

Keep Blender model, fixed wood/clay renders, side renders and interactive
mesh/camera/material synchronized. Browser lighting is approximate; distinguish
it from actual Cycles render fidelity. State whether UI inspection is native
or a simulated DOM/WebGL harness. Do not claim unavailable checks passed.

Run relevant piece/camera checks and affected site, model, candidate, set and
projection checks. Preserve source hashes, gallery defaults, candidate state,
lazy frames, tabs, wipe controls and the queen parts map's sandbox/CSP. Keep
rejected trials out of public controls. Update the existing local preview
with accepted changes. Do not push or publish.

Scope work to this piece's scripts, model, trial outputs and evidence. Shared
page generators and manifests need one coordinated writer. Additional modeling
workers require owner or applicable instruction authorization; this document
does not launch them. Assigned workers report changes, all five scores, hashes,
validation and remaining issues to the parent before integration. Respect owner pauses.

Record work in `docs/queen-mission-log.md` and
`docs/queen-mission/iteration-NNN/`, preserving existing history. Include
starting/accepted hashes, reference comparisons, all five scores, render
settings, decisions, validation, pending work and next steps.
Commit completed checked iterations with the actual-model co-author trailer
required by AGENTS.md. Preserve provenance: original artwork authorship is
unclear; do not attribute it to James Clarke or invent a license.

## Completion

Complete only when this queen is assessed to be visually indistinguishable
from the detailed reference in the fixed view while consistent with the original.
Independently re-examine the full image, native/enlarged crops, original
comparison, neutral and side views; resolve every remaining issue across all
five metrics. Do not round high scores to perfection or mistake outline fit
for texture/lighting accuracy. If stopped by resources or the owner, checkpoint
honestly as incomplete. Unseen geometry and original camera/material settings
remain inferred even after a successful visual match.

Read `docs/queen-54-wood.md`. Export the closed editable control rather than derived light receivers. Regenerate receivers after geometry edits and validate evaluated faces, UVs, normals, shared material and links against the control. Preserve the established height/base tolerance.

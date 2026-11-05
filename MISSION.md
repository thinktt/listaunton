# Queen reconstruction mission

## Objective

Refine the accepted queen until its rendered appearance matches the selected
high-resolution reference as closely as can be honestly assessed. Examine,
change, render, compare, score, and repeat. Improve the actual geometry, wood
material, and lighting; a close outside silhouette alone is not success.

The owner explicitly authorizes creative ideas, experiments, and appropriate
tools to get the wood texture right. Explore techniques such as procedural
grain, image-generated texture assets, reference-derived texture projection,
texture painting, custom UV mapping, and combinations of these approaches.
Develop color, grain direction and scale, surface relief, and roughness/gloss
together as needed. Choose tools by their usefulness to the visual result;
the current material setup is not a constraint. Keep the reference images
unchanged, separate baked lighting from surface color where practical, and
check the material from other angles so it remains useful on a real 3D model.
Judge each experiment through the same reference comparisons and scorecard,
preserving the best accepted result.

The owner authorizes sustained iteration and permits concentrating on one
score at a time. Continue until the visual-match completion criteria below
are met, the available execution/token budget ends, or the owner stops the work.

This file records the mission. Writing it does not itself start a goal or
change the model. When the owner starts this mission, use the existing goal
if it already covers this work; otherwise create a goal explicitly tied to
this file. Do not invent a numerical token budget.

## Starting point and fixed references

- Repository: `/home/toby/code/listaunton` in `Ubuntu-24.04` WSL.
- Accepted starting revision: `3096e84`, restoring the queen from `cd6dfcd`.
  Refine this model. Do not resurrect the rejected `2cb3cfd` reconstruction
  or start over without the owner's direction.
- Editable model: `models/queen/queen-rebuilt.blend`.
- Selected high-res image: `assets/queen/reference.png`.
- Ultimate source: `references/lichess-staunton-3d/Black-Queen.png`;
  consult the white original when its shading clarifies a detail.
- Imagined side guide: `assets/queen/concepts/side-01.png`. It helps with
  style and plausible side proportions; it does not override the original
  elevated view.
- Comparison page: `review.html`, including the fixed overlay, rotating
  model, side comparison, and unchanged parts map.
- Build and validation instructions: `docs/queen-54-wood.md` and `AGENTS.md`.

Keep the reference camera **orthographic, 54 degrees above the board**. This
is the owner's chosen reconstruction assumption, not a recovered fact about
the source camera. Preserve the approved 83.4% queen-to-king height convention
and the saved side-gallery defaults. The starting height/base-diameter ratio
is approximately 2.1799 under the documented cross-piece normalization.

The high-res picture is the detailed visual comparison target. Check every
accepted geometry change against the original too; where generated detail
conflicts with the original, record the conflict and prefer the original.
Never silently replace, retouch, warp, or recolor a reference to improve a
score. Keep framing/registration fixed during an iteration and use identical
image coordinates for before/after comparisons.

## Stable scorecard

Rate all five categories after every candidate, even when only one was
targeted. Keep the rubric unchanged across iterations. Scores describe the
specified image view, not the correctness of unseen geometry.

| Metric | What to examine | Starting score |
| --- | --- | ---: |
| Outside silhouette and placement | Actual render alpha versus the fixed reference mask; tip, neck, collar, base and foot boundaries | 97.91% measured IoU |
| Interior shapes and carved details | Finial, bowl, rim faces, crown body, three collars, stem, socket, flare, groove and foot | 70% visual |
| Wood color and tonal variation | Regional hue, saturation, dark/light distribution and transitions | 60% visual |
| Grain pattern and surface texture | Grain scale, direction, distinctive markings, pores, relief and variation in polish | 30% visual |
| Lighting and reflections | Highlight position, size, sharpness and brightness; cavity shadows and edge reflections | 40% visual |

Starting overall visual assessment: **about 60% (roughly 55-65%)**. For a
consistent progress indicator, use an equal-weight mean of the five scores
(starting value 59.58%, displayed as 60%). Label that mean as a working
score, not a calibrated probability or proof of fidelity. Keep the holistic
visual assessment alongside it if they diverge.

Silhouette IoU uses the actual render's alpha and the selected reference's
`max RGB > 12` and `alpha > 127`, taking the largest component and filling
holes, as in `scripts/queen/compare_finished_queen.py`. Record the original
sprite's separate IoU as well. Exclude the black background from color and
texture statistics. Do not count matching empty pixels as model accuracy.

Except for measured IoU, scores are subjective. Explain each score change
with a visible before/after difference and remaining defects. Do not increase
scores just because effort was spent, a shader became more complicated, or
one numerical measurement improved. A failed trial may score lower; keep
that finding and revert the trial rather than inflating its rating.

## Initial findings to address

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
   wood render side by side, at 50% overlay, and as enlarged crown, collar,
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
   parts map's sandbox/CSP. Do not change other pieces or gallery defaults.
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

## Completion

Continue until the model is assessed to be a visually indistinguishable
match in the fixed reference view, or one of the resource/owner stop
conditions applies. Before claiming that match, independently re-examine
the full image and all detail crops at native resolution and enlarged view,
verify both original and high-res comparisons, and explicitly resolve the
remaining discrepancy list across all five categories.

Do not round a high score to perfection, lower the standard because work is
hard, or use a successful outline test as proof of the material or lighting.
If a visible mismatch remains, the mission remains incomplete. A completed
visual match still does not prove the unseen geometry or recover the original
artist's actual camera/material settings. Report those limits honestly.

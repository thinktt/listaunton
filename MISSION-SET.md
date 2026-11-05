# Staunton set reconstruction mission

## Objective and activation

Recover all six Lichess Staunton piece types: king, queen, bishop, knight,
rook and pawn. Refine their actual geometry, wood materials and lighting by
repeating examine, change, render, compare and score. A matching outline alone
is not success. Produce usable three-dimensional pieces for a digital board.

This is the set-wide version of [the queen mission](MISSION.md). Preserve that
file and its historical evidence. Creating this document does not start or
resume a goal, launch workers, or change any models. The queen goal remains
paused until the owner resumes work. On activation, use a goal explicitly
covering this file; do not invent a token budget or mark an unfinished queen
goal complete merely to replace it.

Creative tools and artistic interpretation are authorized: procedural wood,
image-generated texture sources, reference-derived pigment, texture painting,
custom UVs and combinations. Develop color, grain direction and scale, pores,
relief and polish together. Keep references unchanged, separate lighting from
pigment where practical, and inspect other angles so the material remains
usable on a real model. No reference billboard or composited photograph may
substitute for an actual BSDF model render.

Continue the authorized loop until every piece meets the completion criteria,
an execution/token limit ends work, the owner stops it, or weekly allowance
reaches the pause threshold. A plateau requires a new supported hypothesis,
not inflated scores or repetition of already rejected experiments.

## Repository, accepted baselines and reference hierarchy

Repository: `/home/toby/code/listaunton` in Ubuntu-24.04 WSL. Read AGENTS.md,
the relevant piece build notes, current Git status and latest iteration log
before work. All six pieces already have editable models. Refine the latest
accepted version of each; do not start over or restore rejected alternatives
without owner direction. Record starting model and reference SHA-256 hashes.

1. Original sprites in `references/lichess-staunton-3d` are the ultimate
   source of truth. Consult both colors for geometry and shading clues.
2. Owner-selected high-res images guide precise detail fitting. If generated
   details conflict with an original, record the conflict and prefer the original.
3. Generated side views guide style and plausible side proportions. They are
   imagined views, not recovered geometry and not authority over the originals.

| Piece | Selected detailed reference | Primary original | Review page |
| --- | --- | --- | --- |
| King | `assets/candidates/king/candidate-1.png` — black 1 | Black-King.png | king-review.html |
| Queen | `assets/queen/reference.png` — existing selected image | Black-Queen.png | review.html |
| Bishop | `assets/candidates/bishop/white-candidate-3.png` — white 3 | White-Bishop.png | bishop-review.html |
| Knight | `assets/candidates/knight/candidate-2.png` — black 2 | Black-Knight.png | knight-review.html |
| Rook | `assets/candidates/rook/color-tests/candidate-6-direct-grade.png` — black 8 | Black-Rook.png | rook-review.html |
| Pawn | `assets/candidates/pawn/candidate-2.png` — black 2 | Black-Pawn.png | pawn-review.html |

Verify selections against `docs/reference-selections.md` on activation; later
explicit owner selections take precedence. Preserve original and candidate
files and their provenance. The bishop selection is the ungraded white 3,
chosen for clearer modeling edges, not the later color-graded candidate.

Use `models/<piece>/<piece>-rebuilt.blend`, `scripts/<piece>` and
`assets/<piece>` for each piece. Side guides are recorded in
`assets/side-views/manifest.json` and the piece's concepts directory. Preserve
existing reference registration, including explicit knight mirroring where
applicable. Record genuine cropping in original sprites, including the king's
clipped cross; do not distort a complete model to reproduce a cropped boundary.

The queen baseline at drafting is accepted commit 7d7d55a; the latest evidence
checkpoint is 103dac6. Model SHA-256:
`c32bccbf33e5e137d982bdeafd881a783b006f62e644dbd5db2df57d02801004`.
Continue from it or a later accepted checkpoint. Do not revive rejected queen
reconstruction 2cb3cfd. Read the latest queen mission log before repeating
material or lighting hypotheses.

## Camera and proportions

Use an orthographic reference camera **54 degrees above the board** for every
piece. This is the owner's chosen assumption, not a historically recovered
camera angle. Preserve each piece's saved scale, framing and registration
within an iteration; never move the comparison image to conceal a discrepancy.

Preserve `assets/side-views/defaults.json` and its foot-anchored uniform scales.
The approved displayed heights relative to king are king 100%, queen 83.4%,
bishop 75.3%, knight 66.2%, rook 58.9%, pawn 49.2%. These are presentation and
proportion conventions, not independently measured physical dimensions. Use
the existing original-sprite base-width/model-height normalization to translate
them into geometry; do not apply the gallery slider values as raw mesh scales.
Keep the established queen height/base tolerance and record equivalent sizing
checks for other pieces. Preserve shared ground level, gallery order, slider
state, original image aspect ratios and historical projection alternatives.

## Piece-specific examination

These are inspection priorities and owner constraints, not claims that every
listed defect is still present. Establish a fresh baseline before editing.

| Piece | Distinctive features to inspect |
| --- | --- |
| King | Cross shape, thickness and seating; crown flare; stacked collars; tapered stem, socket, base and foot. Separate crop uncertainty from geometry. |
| Queen | Compact egg finial seated in a shallow bowl; continuous splash-like crown; eight tips, flattened rim intervals; compact rolled collars; socket and base transitions. |
| Bishop | Continuous curved head, deep open mitre slit, and button-like finial seated directly on the head without a gap or pedestal. |
| Knight | Recognizable horse anatomy, conical muzzle, jaw, eyes, ears, mane and neck flowing into the base. Use the approved imagined side guide for style while preserving the original elevated fit. |
| Rook | Thin, consistent turret walls and battlements, interior opening, shaft taper and compact base; avoid thickening far-side turret sections merely because an upscale did. |
| Pawn | Rounded head comfortably seated in its collar with no floating gap; collar, stem taper, socket, flare, groove and foot. |

For every piece inspect grain orientation through turned/carved surfaces,
regional wood color, pores, varnish variation, reflected crescents, cavity
shadows and highlight shape. Geometry is shared between black/white originals;
finish differs. First finish the selected reference color for each piece.
Document opposite-color inspection separately and never count the chosen-color
score as proof that both finishes match. Preserve the source images of both.

## Resource check and pause rule


Use [check-codex-usage](skills/check-codex-usage/SKILL.md). A discoverable copy
is installed at `C:/Users/toby/.codex/skills/check-codex-usage/SKILL.md`.

The owner selected a **Luna subagent** for usage monitoring. Reuse
`/root/usage_guard_luna` when it is available. Otherwise spawn
`usage_guard_luna` with `model: gpt-6-luna`, `reasoning_effort: low`, and
`fork_turns: none`; supply only the usage skill, the 3% rule, and the current
mission state, rather than the modeling conversation.

Luna's initial read-only check succeeded: it can access the live usage tool.
It is idle until the mission starts. At mission start, assign it to check
immediately and every 5 minutes during active work, using bounded,
interruptible waits rather than busy polling. It reports threshold crossings
and reading failures to the parent with `collaboration.send_message`.
Routine readings need no user-facing commentary.

Ask Luna for a fresh check at the beginning and end of each goal turn,
between substantial iterations, and before a new expensive batch when the
last reading is stale. The parent handles checkpoints and goal transitions;
Luna does not modify models or pause a potentially different child goal.
Stop the worker when the mission stops, pauses, or completes. Confirm its
status on continuation, and restart it if it ended; a session subagent is
not an independently scheduled service and must not be assumed to survive
an app restart. If Luna cannot run, use the live tool directly and disclose
the fallback rather than silently dropping the usage check.

Use the applicable **weekly** window (normally `windowDurationMins: 10080`).
Calculate `remainingPercent = clamp(100 - usedPercent, 0, 100)`.
Do not confuse remaining allowance with consumed allowance, a short-window
limit, purchased credit balance, or the current goal's token budget.

**When weekly remaining allowance is 3% or lower:**

1. Start no new modeling, image-generation, or render batch.
2. Save a concise checkpoint of completed work, outstanding validation,
   current/best scores, and the next action. Preserve the best accepted model.
3. If the mission goal is active, call `update_goal` with `status: paused`.
   The owner explicitly authorized this conditional pause. Report the status
   returned by the tool and the observed remaining percentage, then stop.
4. Stop Luna's monitoring loop and keep the old heartbeat disabled until
   the owner resumes. Do not resume automatically after a weekly reset or
   spend a reset credit to continue.

If a weekly reading is missing or the tool fails, it means **unknown**, not
zero or unlimited. Retry once; if still unknown, checkpoint and report that
the threshold cannot currently be verified before starting more substantial
work. Do not claim that the 3% threshold was crossed without evidence.

If the execution/goal token budget runs out first, leave an honest incomplete
checkpoint and allow the platform's budget status to take precedence. Never
mark the goal complete merely because time or tokens are ending.

The earlier main-chat heartbeat, `queen-mission-usage-guard`, remains
**paused**. Do not activate it automatically with the mission: Luna replaces
its routine checks, avoiding duplicate scheduled main-agent work. A skill
contains instructions; the actual checks are tool calls made by the Luna
worker. This guard is still a precaution rather than a guaranteed hard cap:
messages can wait for a tool call to finish, and other chats share the same
allowance. Preserve the iteration-boundary checks.


## Stable scorecard for every piece

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
quietly changing thresholds between trials. Note source cropping and genuine
openings; hole-filled silhouette metrics do not assess the bishop slit or rook
interior, which need separate detailed inspection.

At drafting, the accepted queen scores are 97.9612 / 80 / 80 / 77 / 64,
working mean 79.7922%, holistic 75–80%; original IoU is 97.9109%. Other pieces
require fresh full-material baselines. Mark them unassessed until examined;
diagnostic clay is not a finished wood material. Never fabricate missing scores
or average unassessed pieces into a reassuring set-wide percentage.

## Work allocation and shared files

The parent coordinates accepted baselines, evidence and integration. Reuse Luna
for the five-minute usage guard. Additional modeling subagents require owner
or applicable instruction authorization; this file does not launch them.
When parallel modeling is authorized, give each worker one piece and isolated
trial outputs. Keep shared page generators, manifests, defaults and integration
under one writer. Respect the actual available concurrency limit; the monitor
consumes an active slot. Workers report all metrics, hashes, validation and
remaining issues before their changes are accepted. Stop all mission workers
on an owner pause or usage threshold and preserve partial checkpoints.

## Iteration loop


1. **Check resources and recover state.** Read the latest mission log, inspect
   Git status, and identify the current best accepted revision. Respect other
   work in the checkout. Perform the weekly usage check.
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
9. **Check usage and repeat.** Recheck the weekly allowance, enforce the pause
   rule, and select the next discrepancy. A plateau calls for a different
   hypothesis, not a declaration of perfection.

Keep iteration records in `docs/set-mission-log.md`, created on the first
execution. Store useful evidence in `docs/set-mission/<piece>/iteration-NNN/` or an
equally clear repo-local location. Each record should contain:

- Date, iteration, starting/best revision, and model/reference hashes.
- Weekly limit source, timestamp, used/remaining percentages, and reset time.
- Hypothesis, targeted metric, concrete changes, and render settings.
- All five before/after scores, original and high-res IoU, overall score,
  remaining discrepancies, regressions, and acceptance/rejection reason.
- Comparison images, actual validation results, and the next specific step.

Checkpoints must distinguish completed work from unrendered or unvalidated
changes. Rejected experiments must not displace the best accepted result.


## Set-wide validation and delivery

Follow each piece's current pipeline, not obsolete history scripts. Check
finite geometry, normals, topology, UVs and intended component construction;
use closed/manifold checks where appropriate. Do not silently require the
king's separate cross and body to be boolean-fused. Validate actual openings
and negative space on bishop, rook and knight. For queen light receivers,
compare derived faces, UVs and normals with the closed editable control, and
regenerate receivers after geometry changes before rendering.

Keep saved Blender model, fixed wood/clay renders, side renders and browser
mesh/camera/material assets synchronized. Browser lighting is approximate;
label it separately from Cycles render fidelity. Preserve the queen parts
map's sandbox/CSP, lazy model frames, tab state, candidate choices and wipe
behavior. Keep rejected trials out of public controls.

Use the relevant piece checks plus `scripts/check_model_site.py`,
`scripts/check_site.py`, candidate/set interaction checks and historical
projection checks when affected. Report whether browser inspection was native
or a simulated DOM/WebGL harness. Do not claim unavailable checks passed.
After accepted changes, inspect the complete set side by side at the saved
relative scales for a coherent family without overriding individual references.

Maintain `docs/set-mission-log.md` with a per-piece latest/best score table,
accepted hashes, blockers and next steps. Link the queen's existing history
rather than rewriting it. Evidence belongs in
`docs/set-mission/<piece>/iteration-NNN/`; include reference/original comparisons,
neutral and side inspections, render settings, five scores, decisions,
validation, usage timestamps and pending work. Distinguish unrendered,
unvalidated and accepted states explicitly.

Commit each completed checked iteration with the actual-model co-author
trailer required by AGENTS.md. Do not push or publish. Preserve provenance;
original artwork authorship remains unclear and must not be attributed to
James Clarke. Update local preview assets when needed so the owner sees the
accepted model on the existing pages.

## Completion


Continue until all six models are individually assessed to be a visually indistinguishable
match in the fixed reference view, or one of the resource/owner stop
conditions applies. Before claiming that match, independently re-examine
the full image and all detail crops at native resolution and enlarged view,
verify both original and high-res comparisons, and explicitly resolve the
remaining discrepancy list across all five categories.

Do not round a high score to perfection, lower the standard because work is
hard, or use a successful outline test as proof of the material or lighting.
If a visible mismatch remains on any piece, the set mission remains incomplete. A completed
visual match still does not prove the unseen geometry or recover the original
artist's actual camera/material settings. Report those limits honestly.

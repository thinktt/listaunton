# Pawn reconstruction mission

> This is a static statement of the goal and acceptance standards.
> Change it only at the owner's direction. Put progress, scores, model hashes,
> checkpoints, trials and current status in the piece mission log.

## Goal

Recover a usable, editable 3D pawn faithful to the Lichess Staunton set.
Refine its geometry, wood color, grain, surface finish and lighting until its
fixed-view render is visually indistinguishable from the selected detail
reference while consistent with the authoritative original. A matching outline
alone does not complete the mission.

This mission covers the pawn. Reading or editing it does not activate a
modeling goal or launch workers. When activated, iterate until the full goal is
met, an execution limit is reached, or the owner stops work. A plateau calls
for a new supported hypothesis.

## References and working locations

- Master original: `references/lichess-staunton-3d/Black-Pawn.png`; inspect the opposite color for additional geometry clues.
- Selected detail reference: `assets/candidates/pawn/candidate-2.png` — black candidate 2.
- Side guide: this piece's entry in `assets/side-views/manifest.json` and `assets/pawn/concepts/`.
- Editable model: `models/pawn/pawn-rebuilt.blend`.
- Scripts and assets: `scripts/pawn/` and `assets/pawn/`.
- Review: `pawn-review.html`.
- Progress and accepted state: `docs/pawn-mission-log.md`; evidence: `docs/pawn-mission/`.

The original settles conflicts. Generated enlargements help interpret detail;
imagined side views guide style and plausible proportions, and cannot overrule
the original. Verify the owner's selections in `docs/reference-selections.md`.
Preserve source pixels, hashes and registration; never alter a reference to
improve a score.

## Defining features

Match the rounded head comfortably seated in its collar with no floating gap, the collar profile, stem taper, raised socket, flare, single base groove and foot. Inspect the head-to-collar contact in both the original view and side profile.

## Camera and proportions

Use the orthographic camera at **54 degrees above the board** for the standard
reference comparison. This is a working assumption, not recovered historical
metadata. Keep framing, scale and registration fixed within each comparison.
Keep the standard camera fixed during refinement; a different acceptance camera requires owner direction.

The approved side-gallery relationship is **49.2% of king**. Preserve gallery
defaults, order, uniform scaling and the shared foot baseline. These are display
conventions, not independently measured physical dimensions; use the documented
normalization rather than applying slider percentages directly to mesh scale.
Keep side comparisons at a shared physical scale. Follow the whole-set height
interpretation in [MISSION-SET.md](MISSION-SET.md).

## Work and evaluation

Read `AGENTS.md`, the current build guide and the latest piece log before work.
Start from the latest accepted model. Preserve it until a candidate is checked;
do not restart or revive rejected alternatives without owner direction.

Examine, choose a concrete discrepancy, modify, render, compare and repeat.
Use wood and neutral renders, unchanged originals of both colors, the selected
high-res reference, enlarged feature crops, overlays and side views. Assess all
five categories every iteration: silhouette and placement; interior form;
wood color; grain and surface texture; lighting and reflections. Apply the
stable rubric and mask convention in [MISSION-SET.md](MISSION-SET.md).
Distinguish measured overlap from subjective ratings. Report tradeoffs and
remaining defects; an improved fitting loss alone does not justify acceptance.

Creative tools are authorized: procedural wood, generated texture assets,
reference-derived pigment, painting, custom UVs and combinations. Keep the
result a real material on real geometry, usable from other angles. Separate
pigment from illumination where practical. A billboard, composited reference,
or emission diagnostic cannot stand in for the final shaded render.

Validate the saved geometry, normals, UVs, packed textures, camera and applicable
render receivers using the current piece pipeline. Reopen the saved scene.
At accepted checkpoints synchronize the local review, fixed renders, rotating
mesh and side comparison from that same model. Preserve source selections,
historical studies and existing review interactions. Record findings, scores,
hashes, accepted/rejected decisions and next steps in the piece log and evidence.
Commit completed checked iterations with the actual-model attribution required
by `AGENTS.md`. Pushing or publishing requires owner direction.

## Completion

Complete only after an independent examination finds no unresolved visible
mismatch across all five categories in the fixed reference view, consistent
with the original and a plausible usable 3D form. Inspect full images, native
and enlarged crops, neutral renders, side views and the synchronized viewer.
A geometry-only phase, a high silhouette score, or a rounded-up percentage
does not establish a complete visual match. Assess the selected finish first;
record opposite-color checks separately.

If stopped before that standard is met, record an honest incomplete checkpoint
in the log. Unseen geometry and original camera/material settings remain
inferred even after a successful visual match.

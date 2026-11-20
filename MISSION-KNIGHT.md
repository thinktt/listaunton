# Knight reconstruction mission

> This is a static statement of the goal and acceptance standards.
> Change it only at the owner's direction. Put progress, scores, model hashes,
> checkpoints, trials and current status in the piece mission log.

## Goal

Recover a usable, editable 3D knight faithful to the Lichess Staunton set.
Refine its geometry, wood color, grain, surface finish and lighting until its
fixed-view render is visually indistinguishable from the selected detail
reference while consistent with the authoritative original. A matching outline
alone does not complete the mission.

Once the owner activates the knight mission, the lead model may create and
coordinate subagents at its discretion. It chooses what to delegate and how
many workers to use. Iterate until the full goal is met, an execution limit is
reached, or the owner stops work. A plateau calls for a new supported hypothesis.

## References and working locations

- Master original: `references/lichess-staunton-3d/Black-Knight.png`; inspect the opposite color for additional geometry clues.
- Selected detail reference: `assets/candidates/knight/candidate-2.png` — black candidate 2.
- Editable model: `models/knight/knight-rebuilt.blend`.
- Scripts and assets: `scripts/knight/` and `assets/knight/`.
- Review: `knight-review.html`.
- Progress and accepted state: `docs/knight-mission-log.md`; evidence: `docs/knight-mission/`.

The original Lichess sprite settles conflicts. Use black candidate 2 for fine
detail and the opposite-color sprite for a second reading of the carving.
Exclude the imagined side view from the entire knight reconstruction, including
design, proportions, geometry, materials, lighting, comparisons and scoring.
Infer unseen form from the carving visible in the approved references. To judge
the profile, rotate the actual model or render it from the side.

Verify the owner's selections in `docs/reference-selections.md`.
Preserve source pixels, hashes and registration; never alter a reference to
improve a score.

## Defining features

This is a stylized, partly abstract carving. At playing size, the sweep of the
mane, the angle of the brow and the taper of the conical muzzle should be
enough to suggest the horse. Keep the cheek and jaw broad and simple. Give
the eye, ears and mouth only as much definition as the approved references
show. Where the carving turns out of view, carry those same simple surfaces
around the form. Account for the mirrored facing of the opposite-color
original when checking the carving.

### Owner's style notes

1. **Mane.** The mane has a clean, stylized form reminiscent of Art Deco. It
   sweeps in one continuous curve from the top of the head, around the back of
   the neck, and down to the platform. Three distinct faces define the mane.
   The top is nearly flat, with only a hint of rounding across its width. The
   two side faces are especially flat. The edges are lightly buffed, just
   enough to soften the corners while keeping the three faces distinct.

2. **Back of the neck.** The back of the neck follows a smooth, continuous
   curve from the top of the head down to the platform. Treat the darker area
   near the base as shading alone. Carry the same rounded contour through that
   shadow, preserving the clean sweep of the profile.

3. **Base and platform.** The base curves upward to a flat platform that
   supports the carved horse head. The neck sits directly on this platform,
   with a narrow margin of flat surface visible all around its footprint,
   including at both the front and the back.

4. **Neck shape.** The rounded back of the neck sweeps from beside the ear down
   to the platform in one continuous curve. At the front, the neck cuts inward
   to form three distinct faces. Each face is nearly flat through most of its
   length, then curves gently as it meets the base.

## Camera and proportions

Use the orthographic camera at **54 degrees above the board** for the standard
reference comparison. This is a working assumption, not recovered historical
metadata. Keep framing, scale and registration fixed within each comparison.
Keep the standard camera fixed during refinement; a different acceptance camera requires owner direction.

The approved side-gallery relationships are recorded in
`assets/side-views/defaults.json`. Preserve gallery defaults, order, uniform
scaling and the shared foot baseline. These are display
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
high-res reference, enlarged feature crops, overlays and side renders of the
actual model. Inspect the model from the side for the head profile and from
above for the narrow margin around the foot of the neck. Assess all
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
mesh and side render from that same model. Preserve source selections,
historical studies and existing review interactions. Record findings, scores,
hashes, accepted/rejected decisions and next steps in the piece log and evidence.
Commit completed checked iterations with the actual-model attribution required
by `AGENTS.md`. Pushing or publishing requires owner direction.

## Completion

Complete only after an independent examination finds no unresolved visible
mismatch across all five categories in the fixed reference view, consistent
with the original and a plausible usable 3D form. Inspect full images, native
and enlarged crops, neutral renders, model profiles and the synchronized viewer.
A geometry-only phase, a high silhouette score, or a rounded-up percentage
does not establish a complete visual match. Assess the selected finish first;
record opposite-color checks separately.

If stopped before that standard is met, record an honest incomplete checkpoint
in the log. Unseen geometry and original camera/material settings remain
inferred even after a successful visual match.

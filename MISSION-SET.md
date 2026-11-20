# LiStaunton reconstruction missions

Recover the six Lichess Staunton pieces as usable, editable 3D models whose
geometry, wood materials and lighting match the source art. Each piece has its
own static mission:

- [King](MISSION-KING.md) · [progress](docs/king-mission-log.md)
- [Queen](MISSION-QUEEN.md) · [progress](docs/queen-mission-log.md)
- [Bishop](MISSION-BISHOP.md) · [progress](docs/bishop-mission-log.md)
- [Knight](MISSION-KNIGHT.md) · [progress](docs/knight-mission-log.md)
- [Rook](MISSION-ROOK.md) · [progress](docs/rook-mission-log.md)
- [Pawn](MISSION-PAWN.md) · [progress](docs/pawn-mission-log.md)

## Keep goals and progress separate

Mission files define objectives, reference authority, permanent piece features,
comparison standards and completion criteria. Change them only at the owner's
direction. Routine model work must not rewrite the goal, declare its status,
change its standard, or append checkpoint summaries here.

Current model hashes, scores, defects, trial decisions, phase completion,
accepted state and next actions belong in `docs/<piece>-mission-log.md`.
Reproduction configurations and comparison evidence belong in
`docs/<piece>-mission/`. Build procedures belong in the piece build guides.
Earlier mission wording remains in Git history; dated observations migrated
out of the statements are preserved in the individual logs.

Reading or editing a mission does not start a goal, resume work or launch
workers. Use the assigned piece's mission when the owner activates modeling.
Do not invent a token budget or mark an unfinished goal complete to replace it.

## Reference authority and shared proportions

The original Lichess sprites settle conflicts. Selected high-resolution
candidates support detailed interpretation. Use generated side views and design
studies only where the piece mission accepts them. For those pieces they guide
plausible unseen form; they do not establish original geometry,
camera settings, or design ancestry. Preserve source images and registration.
Record uncertainty and distinguish observed features from interpretation.

Derive each piece's profile from its own references. Feature shapes or
proportions approved for one piece do not automatically become requirements
for another piece.

The owner's intended height progression is **pawn < rook < knight < bishop <
queen < king**, with the queen relatively close to the king. Chavet and Lardy
examples are useful visual guides. Preserve `assets/side-views/defaults.json`,
gallery order, uniform scaling and the common ground line until the owner
makes a separate sizing decision. Gallery percentages are presentation
conventions, not independent physical measurements. Changes to one piece must
not silently rescale the others.

## Stable evaluation standard

Assess all five categories after each candidate, even when targeting one:

| Category | Examine |
| --- | --- |
| Silhouette and placement | Actual rendered outline, proportions and position at fixed registration |
| Interior form | Curvature, transitions, carving, openings, thickness and negative space |
| Wood color | Regional hue, saturation and light/dark distribution |
| Grain and surface texture | Grain scale, flow, distinctive markings, pores, relief and polish variation |
| Lighting and reflections | Highlight position, shape, size, sharpness and brightness; shadows and edge reflections |

Silhouette overlap (IoU) is measured; other percentages are visual judgments.
Use an equal-weight mean as a working progress indicator and report a holistic
visual range. Neither is a calibrated probability or proof of recovered form.
Keep scores separate for each piece. Explain changes with visible evidence;
do not reward effort or numerical fitting loss alone.

Use the established mask convention consistently: reference max RGB >12 and
alpha >127, largest component with holes filled; model alpha >127, largest
component with holes filled. Record original and selected-high-res overlap
separately. Inspect openings and interior contours directly because filled
silhouettes cannot measure them. Exclude background pixels from material
statistics. Do not silently change masks, registration or tolerances to pass.

## Iteration and acceptance

Examine the latest accepted result, choose a concrete mismatch, modify the
actual model/material/lights, render, compare, score, and accept or reject.
One category may be targeted at a time; assess regressions across all five.
Use full images, enlarged feature crops, neutral renders, overlays and side
views. Compare before/after at identical framing. Preserve the best accepted
result until a replacement is validated, and document any justified tradeoff.
Rejected experiments must not replace accepted assets or appear as current
choices in the public review.

Use a real shaded material on actual 3D geometry. Creative texture techniques
are permitted; projected references must remain usable on the model from
other angles. A photograph, billboard, composite or emission diagnostic does
not establish a final material/lighting match.

Validate the saved model, source hashes and relevant geometry, UV, material,
receiver, export and camera checks. Reopen the saved scene and inspect its
render. Synchronize the local review, fixed renders, rotating viewer and side
comparisons from that same accepted model. Browser lighting is approximate;
report actual checks honestly. Preserve existing review controls, candidate
state, historical projection studies, and the parts map's sandbox/CSP.

Record dated evidence and next actions in the piece log. Commit completed,
checked iterations using the actual-model attribution in `AGENTS.md`. Do not
push or publish without owner direction. Coordinate shared generators and
manifests; additional workers require owner or applicable instruction authority.

The full mission is complete only when independent visual examination resolves
every visible discrepancy across all five categories in the fixed reference
view, consistent with the original. A completed phase or high outline score
does not complete it. Record an incomplete checkpoint when work stops early.
Unseen geometry and historical rendering settings remain inferred.

Preserve provenance: original artwork authorship is unresolved. Do not attribute
the pieces to James Clarke or invent a license for the supplied images.

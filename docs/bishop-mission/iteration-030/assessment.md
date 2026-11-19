# Bishop 030 — base, socket and collars in the king/queen style

The owner requested a consistent turning style across the bishop, king and
queen, including the socket, base and three collars. Work starts from the
restored tall bishop 024. This is a local shape revision, not another attempt
to shorten the piece. The reference camera remains orthographic at 54°.

## Shape changes

- The flared base now follows a more continuous curved slope into a shallower
  groove. The straight foot wall and original maximum foot diameter remain.
- The socket rolls into the stem with a smooth shoulder instead of a flat ledge.
- All three collars have thinner rims with rounded corners. The first trial
  made their edges too sharp; the second retains more rounding.
- The upper stem, head, button and slit retain their restored controls. The
  total height remains 4.59200668335 model units and the foot diameter remains
  2.0130200386. No rescaling, camera change or reference realignment was used.

The current king and queen were inspected from their actual saved Blender
controls and evaluated sections. Their hashes, source commits and extracted
profiles are recorded in [style-sources.json](style-sources.json). Their
geometry was not changed. The bishop uses the same family of curved transitions
and thin rounded rims, fitted to its own reference; it is not a literal scaled
copy of the king's entire base.

[Neutral side comparison](geometry-side-comparison.png) ·
[Original/selected/before/after](comparison/comparison.png) ·
[Base crop](comparison/base.png) · [Head and collars](comparison/head.png)

## Comparison at the unchanged reference camera

| Measured outline overlap | Restored 024 | Revised 030 |
| --- | ---: | ---: |
| Original white | 98.7742% | 98.5534% |
| Selected white candidate 3 | 97.0347% | 97.0519% |
| Original black | 97.8272% | 97.9130% |

Outline overlap is not a measurement of internal shape or finish. The small
original-white regression is retained for the requested side style, not hidden
by changing the alignment. See [registered edge traces](comparison/original_white-contours.png).

Measured rim thickness at half of each rim's radial protrusion changes from
0.1905 to 0.1385 (lower), 0.1810 to 0.1220 (middle), and 0.1110 to 0.0735
(upper). These are roughly 27%, 33% and 34% thinner. Their front projected
edges move by less than 1.7 pixels in the 1254-pixel comparison: upper
510.91 → 509.30, middle 564.59 → 566.28, and lower 607.78 → 607.18.
The upper edge is slightly higher than before; it is not claimed to be an
exact match.

The physical groove moves from image row 1046.38 to 1054.52, near the original's
blurred dark line around row 1053. Its radial recess is shallower. These
measurements are independent of the wood shading. Full measurements are in
[measurements.json](measurements.json).

## Status and limits

This revision improves the common turning style while retaining the tall
reference fit. The bishop base still has its own height and the collars their
own radii to follow the bishop's original. The upper head and slit are unchanged
in this task. The full reconstruction mission remains incomplete.

The outline score is measured; an interior-form estimate of 84% is subjective.
The previous color/grain/light estimates of 83/77/72 are retained as unfinished
work, not new finish improvements. The inherited wood and lighting can still
suggest details that are not in the neutral geometry. No material, texture
pixel, UV, light or mission changes are part of this revision.

## Reproduction and verification

From the repository root, with Python + NumPy + Pillow and Blender available:

1. `python scripts/bishop/prepare_family_style.py` recreates the accepted
   control edits in `family-style.json` from the recorded original controls.
   `--variant a` recreates the sharper rejected first trial.
2. `blender -b --python scripts/bishop/profile_shape_trial.py -- docs/bishop-mission/iteration-030/family-style.json`
   creates the saved model, wood render and neutral render under
   `build/bishop-mission/186-family-style-b`. It reopens and checks the saved
   file, regenerates exact render receivers, and verifies preserved scene data.
3. `blender -b --python scripts/bishop/render_family_evidence.py` renders the
   neutral before/after evidence without altering either saved scene.
   `measure_family_style.py` independently measures those saved surfaces.
4. Promote that checked trial's model/profile/render/neutral files to the
   current bishop paths, then run `validate_checkpoint.py` in Blender,
   `render_diagnostics.py`, `compare.py`, `refresh_review.py`, and the
   bishop viewer/review checks. Refresh only the bishop records in the shared
   set page with `refresh_set_entry.py`.

`inspect_set_style.py` can reproduce the recorded donor measurements, retrieving
the pinned Blender sources from Git if its private copies are absent. It rejects
hash mismatches. Neutral side panels use an identical camera and scale.
Validation reports and the delivery manifest record the actual saved model
hash and served assets.

# Collar investigation — rejected, checkpoint 017 retained

On 2026-11-12 the owner asked the current workers to finish their iteration
and pause. This investigation is complete. None of its trials replaces the
accepted pawn. The fixed overlay, rotating mesh and side comparison remain
checkpoint 017, at `pawn-review.html` / `http://localhost:8080/pawn-review.html`
when the local server is running. The full visual-match mission is incomplete.

## What was tested

The selected image has a wider brown band beneath the left collar reflection.
Coordinate inspection found that the accepted mesh reaches the stem too early
in that area. Both original colors were examined; they support a rounded edge,
but cannot establish every detail of the generated enlargement.

- 116 separates pigment-only, studio clay and neutral clay diagnostics. The
  emission pass is diagnostic only; it is never a delivered material.
- 117–118 compare bounded underside profiles in cropped renders. Lowering the
  edge fills more of the brown band but also shifts the front reflection.
- 119 lowers only meridian controls 35 and 36, preserving every radius and
  other control. The full render exposes a substantially worse front glint.
- 120 tries a bounded local adjustment of the existing lower-collar light.
  Its small fitting-loss gain does not resolve the visible defect.
- 121–122 transfer existing collar pigment, polish and fine-slope maps onto
  the changed surface. Only roughly 0.15–0.23% of their texels change. This
  helps slightly but does not restore the reflection. Newly exposed underside
  and invisible surfaces retain their existing material. No reference pixels
  or beauty render are composited into the output.
- 123 isolates the four collar sources, remaining lights, world and secondary
  gloss. Removing the lower-collar source removes the displaced bright patch;
  the defect is not resolved by the map transfer alone.
- 124 re-aims that source from the revised surface and fits its actual Cycles
  response. It reduces the regression, but the glint is still displaced and
  fragmented. The thicker, flatter underside is not an overall improvement.

## Final comparison

All measurements retain the fixed orthographic 54-degree camera and reference
registration. RGB errors are on common foreground under the established mask;
collar luma/pattern measurements use the same explicit patches as earlier work.

| Measurement | Accepted 017 | Rejected 124 |
| --- | ---: | ---: |
| Selected silhouette IoU | 96.811% | 96.911% |
| Original black silhouette IoU | 98.499% | 98.503% |
| Original white silhouette IoU | 98.136% | 98.102% |
| Whole collar/stem RGB error, 0–255 | 2.306 | 2.628 |
| Left collar luma error, 0–255 | 6.65 | 6.22 |
| Front collar luma error, 0–255 | 2.96 | 13.83 |
| Front fine-pattern correlation | 0.890 | 0.157 |
| Native original RGB error, 0–255 | 16.67 | 16.70 |

The selected front glint's bright center is approximately (521.33, 626.38).
Checkpoint 017 is (521.34, 626.49); trial 124 is (515.67, 630.15). The small
outline gain does not justify losing the matched front reflection. See the
full-frame, collar, native-source and side images saved beside this document.

| Category | Retained 017 | Rejected 124 |
| --- | ---: | ---: |
| Silhouette and placement | 96.81 | 96.91 |
| Interior form | 91 | 91 |
| Wood color | 93 | 93 |
| Grain and surface | 94 | 93 |
| Lighting and reflections | 92 | 90 |
| Equal-weight working mean | 93.36 | 92.78 |

Only silhouette overlap is measured. Other scores are visual judgments, not
probabilities. The accepted holistic estimate remains 90–95%. Interior-form
credit for the lower left edge is offset by its thicker side profile. The
accepted model still has collar residuals, an incomplete inner groove line,
a fragmented stem reflection and inferred rear grain. It is not a perfect match.

## Verification and preserved state

`124-scope-validation.json` records an actual reopen of the saved trial:
only controls 35–36 and the existing lower-collar reflector changed. All
other control vertices, UVs, topology, smoothing, modifiers, shaders, packed
maps, ramps, 46 other lights, world, sampling and camera remain unchanged.
The evaluated surface is closed and manifold, with Euler characteristic 2.
This scope check does not make the trial visually acceptable.

The rejected trial was not delivered or independently replayed. No new
native-browser GPU inspection is claimed. Accepted public assets and their
existing Windows preview are verified byte-for-byte by `preservation.json`;
checkpoint 017's prior render/replay, orbit, geometry and site checks remain
the applicable accepted validation. No source images, selections, gallery
defaults, shared review controls or other pieces were changed.

The preserved source scene is `history/pawn-mission-017/pawn-rebuilt.blend`.
The exact diagnostic and trial configurations are included here. For example,
`shape_trial.py` uses `119-rounded-collar-underlip.json`; `fit_lighting.py`
then uses `124-retargeted-collar-source.json`. The saved scope check uses
`124-direct-reproduction.json`. These are rejected research recipes, not the
current build pipeline. Diagnostic coordinate arrays and failed trial models
remain in the private build directory; they are not public model alternatives.

Further modeling requires the owner's instruction to resume. A future attempt
would need to resolve the collar profile, material coordinates and reflection
together; repeating the small reflector shift alone is unsupported by these
results.

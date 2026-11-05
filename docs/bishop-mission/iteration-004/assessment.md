# Bishop iteration 004 — rounder button reflections

Starting checkpoint: `10fb56b`, preserved in `history/bishop-mission-003`.
The accepted change affects only the two button reflectors: their area shape,
orientation, power and color. Geometry, pigment, relief, other lighting,
registration, and the fixed 54-degree orthographic camera remain unchanged.
Ungraded white candidate 3 remains the detail reference; the original white
Lichess sprite remains authoritative. No reference image was edited.

## Findings and experiments

The side/rear pigment boundary remains conspicuous. A conservative visibility
mask was baked from ray casts and used to protect the visible atlas texels.
Continuing per-row visible color around the rear produced dark horizontal
bands; using one amber color removed those new bands but did not remove the
main patch boundary. A no-bump diagnostic showed that this boundary is mainly
pigment/residual shading, rather than a relief discontinuity. Neither atlas
was accepted. The previous atlas is preserved byte for byte. The next material
attempt needs to address visible pigment and illumination together.

The button originally had two small gold flecks. Fitting only their powers
made the larger reflection a clipped smooth oval. The accepted approach
uses reflected rays from the center and four edges of each target glint to
estimate elliptical area lights in 3D. Their first-order shape comes from
the local smooth surface normals, not an image pasted over the model.

Actual Cycles response passes measure each reflector separately. RGB powers
are fitted through the unchanged Standard sRGB display transform. Stronger
basis passes and a two-pixel response blur reduce subtraction noise. The fit
emphasizes the two glints rather than trying to correct the whole button's
pigment with light. Clipped red pixels leave red power poorly constrained;
an unconstrained fit made a red halo. Limiting red to 1.35 times green keeps
the reflectors warm white. This is an artistic constraint, not a recovered
property of the original renderer. The final full BSDF render, not the
linear prediction, governs acceptance.

## Scorecard

| Metric | Previous | Current |
| --- | ---: | ---: |
| Outside silhouette and placement | 96.20 | 96.20 |
| Interior shapes and carved details | 81 | 81 |
| Wood color and tonal variation | 84 | 84 |
| Grain pattern and surface texture | 77 | 77 |
| Lighting and reflections | 64 | 66 |
| Equal-weight working mean | 80.44 | 80.84 |

Silhouette is measured IoU; the other scores are subjective visual judgments.
The working mean is not proof or probability of fidelity. Holistic fixed-view
appearance remains approximately **75–85%**. This is a modest improvement,
not a finished bishop or a change to its proportions.

The clean render's selected-reference IoU is 0.96197246, original-white IoU
0.97876433 and original-black IoU 0.96753166, exactly the previous 96-sample
values. Shared-foreground RGB error decreases from 7.93 to 7.78 /255;
within the button crop it decreases from 12.39 to 8.89 /255. These diagnostics
combine pigment, geometry and lighting error and are not fidelity scores.

The lighting increase is justified by the rounder large highlight and the
more visible small companion, with cream-colored centers closer to both the
selected image and original sprite. Other category scores stay unchanged.
The specular pattern is still too smooth, and the dark button rim persists.

## Trial decisions

All scored rows use silhouette / interior / color / texture / lighting.
Draft alpha differences come from sampling; no geometry changed.

| Trial | Scores | Decision |
| --- | --- | --- |
| 029 hidden profile continuation | 96.20 / 81 / 83 / 73 / 64 | Reject: new horizontal color bands; patch boundary remains. |
| 030 no-bump diagnostic | — | Diagnostic rear view only; boundary persists without relief. No full candidate score. |
| 031 uniform hidden amber | 96.20 / 81 / 84 / 77 / 64 | Reject: warmer rear, but no convincing seam improvement. |
| 032 power-only button fit | 96.20 / 81 / 84 / 76 / 63 | Reject: bright, clipped oval reads smoother and more artificial. |
| 033 unconstrained shaped prediction | — | Diagnostic prediction only, not an actual beauty candidate; excessive red halo. |
| 034 constrained shaped reflectors | 96.20 / 81 / 84 / 77 / 66 | Retain for clean rendering: rounder, cream-colored glints. |
| 035 reopened 96-sample render | 96.20 / 81 / 84 / 77 / 66 | Accepted after final geometry, material, camera, side-view and page checks. |

Rejected trials remain evidence, not public choices. The archived checkpoint
003 remains the fallback.

## Remaining discrepancies and next step

- Button highlights still lack the reference's fine broken grain pattern;
  the rim remains too dark and uniform.
- The broad reflection below the slit and the long stem/socket reflection
  remain misplaced; collar and foot glints remain too narrow and sharp.
- The slit mouth/floor and some internal curvatures still differ despite
  strong outside silhouette agreement.
- Side and rear views retain the bright projected pigment patch against
  darker hidden wood. The hidden-only fills did not solve this.
- Some inferred pigment retains view-dependent shading. Grain relief does
  not yet follow all the pigment markings, and polish can read as resin.

The next supported lighting hypothesis is to isolate the head's intended
reflection from the lower-head glare, using the exact evaluated surface and
measuring any spill. Material continuity still needs a joint pigment/light
approach; repeating the rejected hidden-only fills is not supported.

## Validation and delivery

The accepted model was saved, reopened and rendered at 1254 square, 96 samples,
with actual Principled BSDFs. Packed pigment pixels exactly match the disk
atlas. Mesh positions, normals and indices are identical to checkpoint 003.
Control UVs are unchanged; evaluated exported UVs differ by at most
0.0000000596, within the existing single-precision tolerance. The fixed camera
and source reference bytes are unchanged. Existing
anatomy, manifold, deep-slit and gap-free button checks remain applicable.

Fresh side, head and rear renders come from the same saved model. The main
bishop workspace and existing local preview are refreshed at acceptance.
Overlay, rotation and source-candidate tabs retain their state. Browser
lighting is approximate; the overlay shows the actual Cycles result.
UI checks use the simulated DOM/WebGL harness, not native browser inspection.
Actual check results and synchronization status are recorded in
`checkpoint.json`. Gallery sizes/order and the other pieces are unchanged.

## Reproduction

For the accepted result, start with `history/bishop-mission-003` and run
`lighting_trial.py` with the adjacent `lighting-config.json`, then
`finalize_render.py` on its saved trial. `reproduction.json` records exact
arguments and hashes. The finalizer saves, reopens, checks packed pixels,
and renders; it does not bake or alter pigment.

To reproduce the measurement instead of using the recorded final settings:
run `shading_reflection_landmarks.py` on `shape-points.json`, then
`shape_button_reflectors.py`; capture the two light responses with
`capture_button_lights.py` at a 20000-unit white basis and fit with
`fit_button_lights.py --response-blur 2 --glints-only --max-red-green 1.35`.
Render the resulting scene before judging it. Numerical fitting alone is
not an acceptance criterion.

# King checkpoint 012 — middle collar and continuous join

Accepted **135-middle-collar-clean-join**, using the standardized fresh saved-file
render from **140**, confirmed by repeat **141** and independent rebuild **136**.
The middle collar has a rounder edge and better placed left/right glints. A
pre-existing self-crossing join between the middle and lower collars is repaired.
This is a partial improvement; the full mission remains active and incomplete.

## Examination and decisions

Diagnostic 127 separated pigment, diffuse shading and neutral form. Pale bands
remain in the pigment. A broad blend with the existing inferred unlit wood source
(128) made the collars too orange and softened the source pattern. A more limited
neutral-component subtraction (129) darkened the wood without improving its overall
match. Both pigment trials are rejected. **The v6 atlas, relief and finish remain
unchanged.** Emission images are diagnostics, never replacement beauty renders.

The earlier middle-left target landed on a downward-facing surface. Small changes
to controls 48–50 round the middle edge and allow a clear reflected ray. Trial 130
established that improvement. Power fitting (131) produced a narrow bright stripe;
a broader but off-center source (132) remained misplaced. Measured reference glints
at (476, 497) and (592, 476) guided 133. Fitting them harder (134) over-brightened the
inner groove, so the gentler powers were retained.

A new evaluated-section check found a crossing near radius 0.539 and height 2.955.
It existed in checkpoint 011 as well as the initial trials. The failed check is
retained. Trial 135 raises three joining controls so the profile flows continuously
between collars. The complete positive-X evaluated lathe section now has no detected
crossings; both closed controls still have positive volume and manifold edges.
The body and separate cross remain intersecting components, not a Boolean-fused solid.

| Metric | Checkpoint 011 | Checkpoint 012 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.8174% | 97.8258% |
| Interior form | 84% | 85% |
| Wood color | 82% | 82% |
| Grain / surface texture | 79% | 79% |
| Lighting / reflections | 66% | 67% |
| Equal-weight working mean | 81.7635% | 82.1652% |

Original-sprite IoU is **96.8464%**. Only IoU is measured;
the other percentages are visual judgments, not recovered ground truth. The
holistic range is **75–85%**. All trial scores and rejection reasons are in
`scores.json`. The mask convention and registration are unchanged.

Middle-collar foreground RGB squared error changes from 734.071
to 631.659; the wider collar region changes from
484.720 to 462.304. These diagnostics are
not perceptual-match percentages. Full images, both original sprite colors,
enlarged crops, neutral form and profile/side/rear views were examined. The middle
edge and glints improve, while other collar bands and uneven varnish remain visible.

## Exact scope

Only body controls **45–50** change. Radius changes by +0.010 at control 48.
Height changes are +0.020 at 45, +0.033 at 46, +0.020 at 47, −0.035 at 49 and
−0.015 at 50. All other coordinates, topology, UVs, float attributes, material,
packed images, world, color management and camera are exact from checkpoint 011.
Physical bounds and overall proportions are unchanged. Nine exact light receivers
are regenerated; the closed controls are exported to the viewer.

Only the existing middle-collar lights are re-aimed/resized: left targets (476, 497),
power 5, rectangle 0.24 × 0.10; right targets (592, 476), power 4, rectangle 0.20 ×
0.08. Both remain 0.8 units from their target, glossy-only, shadow-enabled and linked
only to the middle collar. Their warm color and every other light setting are
preserved. These are art-directed choices, not recovered historical lamps.

The standard view remains orthographic **54 degrees above the board**. Source
images, gallery defaults, other pieces and historical projection studies are unchanged.
Checkpoint 011 is archived exactly under `history/king-mission-011`.

## Rendering repeatability: passing path and remaining limitation

The standardized fresh renderer, its repeat and an independently rebuilt scene
agree within **1/255**, with identical alpha. Rebuilt mesh bytes also match exactly.
Use `render_fixed_diagnostics.py --beauty-only` for the delivered fixed image.

An alternate fresh-render entry point changes a tiny socket glint at approximately
(481, 754): maximum 45/255 over 112 pixels above one level, despite exact scene
data and otherwise nearly identical images. Fixed 256-sample rendering (137/138)
does not fix it. Raw undenoised comparison 139 still differs at a few pixels;
denoising spreads the discrepancy. The precise execution-context cause is unresolved.
**Those failed checks are retained and are not reported as passes.** No tolerance
was loosened, and the sampling experiments are not accepted settings. The source
retains 128 samples with adaptive sampling and denoising, as at checkpoint 011.
The canonical renderer's passing reproduction does not establish identical output
under every rendering entry point or environment.

See `reproduction-checks.json`, `standardized-render-diagnostic.json`,
`adaptive-render-repeatability-failure.json`, `raw-repeatability-139/`, and the
retained alternate-entry-point image. This remains a rendering limitation, not a
claim that the model/reference match is finished.

## Reproduction and validation

From the repository root with Blender 5.2.2:

```sh
blender --background --python-exit-code 1 --python scripts/king/refine_collar_turning.py -- docs/king-mission/iteration-012/reproduction.json
blender --background --python-exit-code 1 --python scripts/king/render_fixed_diagnostics.py -- build/king-mission/136-collar-turning-reproduction/king.blend build/king-mission/136-collar-turning-reproduction --beauty-only
blender --background --python-exit-code 1 --python scripts/king/export_mission.py -- build/king-mission/136-collar-turning-reproduction/king.blend build/king-mission/136-collar-turning-reproduction
```

`check_collar_turning.py` verifies the declared controls and two lights, exact
material/UV/image/camera preservation and the repaired collar section.
`diagnose_full_profile.py` checks the complete evaluated lathe section.
Receiver faces, attributes, UVs, normals, routes and regeneration pass, as do
closed-component, exact-export and canonical-model checks.

The review, fixed/neutral renders, rotating mesh and side views are synchronized,
including all 34 files in the existing Windows preview.
King/candidate interactions, site/model and historical projection checks pass.
Actual-page DOM/WebGL harnesses pass in the repository and preview. Live in-app
browser inspection confirms the original overlay, selected high-res fixed render,
wood front preset and side comparison load correctly with the full piece visible.
This checks page behavior, not perfect reference fidelity. The shared
whole-set check still stops at its documented pre-existing knight sizing metadata
mismatch; subsequent assertions do not run. It is not reported as passing.

## Remaining work

- Upper-collar highlights and the middle inner groove are still misplaced or
  incomplete. The new middle glints are gentler but not exact in extent or finish.
- Pale baked pigment bands, grain scale/flow, relief and varnish variation remain.
- Socket glint continuity and center color, broad base highlights, foot texture,
  cross seating and cavity contrast need further improvement.
- Alternate-entry-point socket-glint variation remains unresolved. Hidden wood
  and side/rear illumination are inferred, not historical evidence.

Next: continue with the upper collar's local curvature/reflection placement,
preserving the repaired middle join and the unchanged accepted material. No
watchers or subagents were started, and nothing was pushed or published.

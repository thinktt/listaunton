# Sixteenth queen iteration: middle collar bevel and crescent

Accepted 2026-11-05, starting queen checkpoint 72c2863.
Starting model: 8b1c052b8c6960c6faf6760635090a7c081b04e5ad779641a4b9e49433f628c0.
Accepted trial: 155-fitted-ridge-crescents. Delivered model: fcb5255f30f89090b5c7fb3b422d15fab2d70c3db4ec478f8bd50e0367c59d94.
Reference: bc510a8f5fff0a1e51fd913f1cf4f4707849d68c5d4dabc8ce6df16cc2e1423a.

## Examination and changes

Removing bump did not restore the missing front-left reflection. A wider coat
lobe (147) softened the remaining highlights without solving it. Projected
control contours were close, so the collar heights, peak radius and spacing
were retained. Only lower-bevel rings 64, 65 and 66 change radially to .565,
.580 and .584; their heights and every other control remain identical.
The maximum displacement is .01500008 model units. UVs and topology are unchanged.

Six exact evaluated receivers preserve the closed control surface, UVs,
custom normals and shared material: turned body, stem/socket, finial and each
of the three collars. Regional light links avoid neighboring-ring spill.
Eleven middle-collar reflected fills omit cast shadows because their inferred
reflection paths lie beneath adjacent collars. This is an explicit artistic
lighting approximation, not a claim to recover the original lighting rig.
Other lights retain their shadow settings; secondary glossy bounces remain zero.
Variants 149, 150, 152 and 154 are emitter setup fixtures, not scored beauty candidates.

Native position and textured-normal passes locate the true visible surface.
The first fitted targets produced isolated, misplaced glints (151). Extending
the shadow-free fill alone (153) was insufficient. Measuring the reference's
actual bright ridge within a narrow fixed-coordinate corridor corrects several
targets by 4-16 pixels. The source images and their registration are unchanged.
Actual linked-light responses through the full wood BSDF are fitted through
AgX at 512 samples, then examined in full fixed and side renders. The v8 pigment,
relief, roughness, finial, other geometry and 54-degree camera remain unchanged.

## Saved-file discrepancy and resolution

The first fitting-session beauty failed the saved-render check: opaque mean
difference 1.393 RGB bytes, p99.9 37 bytes, and 43 binary-alpha pixels differed.
This failed result is retained in the evidence. Promotion was withheld until the saved-scene result was verified.
A fresh saved-file render and the independent reconstruction agree within one
RGB byte, with identical alpha. A second fresh-file render also passes the
established tolerances. Acceptance uses that saved-file result, not the transient
fitting-session image. The fitter now reopens its saved scene before the final
beauty render. The precise internal cause of the transient discrepancy is not
established; it is not treated as a material improvement or geometric regression.

A separate native 256-sample uniform geometry diagnostic finds zero differing
binary silhouette pixels at identical cameras. Fresh-file beauty IoUs equal
the prior checkpoint exactly. No reference-mask or promotion threshold was
relaxed. See material-reproduction and uniform-silhouette reports for measurements.

## Scores

| Metric | Before | Accepted |
| --- | ---: | ---: |
| Silhouette, measured high-res IoU | 97.9612 | 97.9612 |
| Interior form, subjective | 82 | 82 |
| Wood color, subjective | 84 | 84 |
| Grain and relief, subjective | 79 | 79 |
| Lighting, subjective | 72 | 74 |

Equal mean 83.3922%; holistic range remains 79-84%.
Original sprite IoU 97.9109%.
The actual collar-crop weighted error falls 18.34%. This local statistic
supports the visible crescent improvement; it is not whole-piece fidelity.
The small bevel correction does not justify increasing the overall form score.

## Remaining discrepancies

- The middle crescent still breaks into uneven patches; its right half differs
  in width and position. The upper and lower collar highlights remain too coarse.
- Fine pores and varnish breakup do not reproduce the reference's texture.
- Crown-tip shoulders, bowl curvature and reflection shapes remain approximate.
- Socket and foot glints still have hard, irregular edges; the base sheen differs.
- Side and hidden wood are inferred. Browser lighting is approximate and is
  not the Cycles fidelity result shown in the fixed renders.

## Reproduction and checks

Run `blender -b --python scripts/queen/rebuild_collar_checkpoint.py --
docs/queen-mission/iteration-016/reproduction.json` from the repository.
The source is archived checkpoint 15; output is separate trial 156.
Use `check_material_geometry.py --allow-middle-collar-edge` with that archive,
then `validate_finished_queen.py`, `check_middle_collar_reproduction.py`, mesh
export and the established camera/site pipeline. The scope validator checks
the actual archived controls, not just metadata. Six receivers must be regenerated
with socket_band, collar_band and split_collars all enabled after future edits.

Native Blender images and saved scenes were examined. UI regressions use the
simulated DOM/WebGL harness; native browser GPU appearance is not claimed tested.
Delivered reports, local-preview hashes and check output are included separately.
No push or public deployment. The mission remains incomplete. Next investigate
fine relief and reflection breakup, beginning with the collar's right crescent.

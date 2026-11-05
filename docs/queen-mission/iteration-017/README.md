# Seventeenth queen iteration: finial pigment, polish and reflections

Accepted 2026-11-05, starting queen commit 59d924c.
Starting model: fcb5255f30f89090b5c7fb3b422d15fab2d70c3db4ec478f8bd50e0367c59d94.
Delivered model: cf248e4a1766fbdb1e51b7e823931bc26729531dfda4ffbda12a83ee961ad460.
Reference: bc510a8f5fff0a1e51fd913f1cf4f4707849d68c5d4dabc8ce6df16cc2e1423a.

## Examination

The three finial highlights had dark eye-shaped pigment marks beneath them,
sat too low, and were clipped by narrow spot cones. Whole-material smoothing
failed because the flared base needs its existing relief. Material-component
passes isolated pigment from real reflections; no diagnostic emission image
is delivered as a beauty render. Clean linear captures changed the fields
only slightly, so denoising was not the primary defect.

A broad finial/bowl pigment repair (160-161) improved the finial but worsened
the bowl. Fitting the existing light powers (162) could not correct their
positions: it dimmed two glints. These alternatives are rejected. The accepted
repair affects only the finial. It harmonically fills bounded negative marks
from adjacent log pigment, then restores bounded medium/fine variation from
the existing height field and high-frequency reference grain outside expanded
highlight masks. It does not copy broad reference lighting into Base Color.

## Accepted changes

- Existing geometry, all control vertices, UVs, topology, camera, compact
  finial dimensions and gallery defaults remain unchanged.
- The v9 pigment atlas replaces 68,682 texels (1.64% of a 2048-square atlas).
  Every texel outside the repair mask stays byte-identical to v8. The packed
  PNG bytes and decoded pixels match the external atlas after reopening.
- The finial relief distance falls from .007 to .00175, with a smooth height
  transition from z=4.04 to 4.12 and radius below .235. The rest of the queen
  retains its original relief. Roughness, IOR and coat settings stay exact.
  The final mask uses object coordinates. A rendered emission-field check
  verifies that translating the piece and camera together preserves its actual
  polish field; the inherited source model remains unchanged.
- Three reference glints are measured near (478.52,186.45), (494.72,180.80)
  and (499.96,204.24). Native surface-position and bump-normal passes locate
  their reflection directions on the actual seated finial.
- Three real glossy spot emitters are aimed at those locations and linked
  only to the finial. Their cones widen from 1.2 to 12 degrees. The old size
  field described diameter: actual radius changes from .15 to about .30.
  This radius distinction was discovered by inspecting saved Blender data;
  final reproduction records explicit shadow_soft_size values and rotations.
- Exact copies of the old three emitters retain their prior contribution on
  the other five receivers. Other original lights and settings are unchanged.
  The final powers are fitted through AgX using actual 512-sample BSDF responses.

The body copies avoid a lighting regression seen in trials 164-165. At 64
samples, repeated renders differed in a few body highlight pixels; their
physical settings remain verified. The first build-session beauty failed
the maximum-pixel bound (75 RGB bytes at one rim glint, despite only .00743-byte
opaque mean error). A subsequent fresh render failed the p99.9 bound (3 bytes
versus the allowed 2), so one agreeing pair was not treated as sufficient.
Disabling adaptive stopping at 64 samples (171) still left a 75-byte outlier.
The failed evidence is preserved. The final checkpoint uses 256 fixed samples
(172), and both its fresh-file and independent reconstruction meet the existing
pixel-error bounds for one pair. Trial 174 retains those settings and makes the
polish mask follow the piece in object coordinates, but another pair still
fails p99.9 (3 bytes versus 2). Disabling the light-tree sampling accelerator
(176) restores agreement within one RGB byte after reopening and in the
independent reconstruction. This points to the light-tree sampling path in
this scene; its exact internal mechanism has not been established. Final
settings are 256 fixed samples with use_light_tree=False. No threshold was relaxed.
The publish/reopen helpers now honor explicit render_sampling metadata and
retain the previous 64-sample default for earlier checkpoints.
The existing artistic approximations (zero secondary glossy bounces and eleven
shadow-free middle-collar fills) remain explicit and unchanged.

## Scores and inspection

| Metric | Before | Accepted |
| --- | ---: | ---: |
| High-res silhouette IoU (measured) | 97.9612% | 97.9604% |
| Interior form (subjective) | 82% | 82% |
| Color (subjective) | 84% | 84% |
| Grain/surface (subjective) | 79% | 79% |
| Lighting (subjective) | 74% | 76% |
| Equal-weight working mean | 83.3922% | 83.7921% |

Original-sprite IoU: 97.9117%. The tiny changes in
both silhouette measurements result from higher-sample antialiasing; the
vertices, UVs, topology and camera remain exact. The original/high-res promotion
thresholds remain unchanged and pass.
Holistic visual estimate: 80-85%. The local finial RGB error falls 69.21%.
That statistic supports the visible glint improvement; it is not a claim of
the same percentage improvement across the whole piece. Every beauty trial is rated in scores.json.
Trial 166 is a shader/capture fixture, without a separate beauty candidate.

Full fixed, enlarged head/collar/socket/base, original-sprite, overlay and
side comparisons were inspected. The finial no longer has the conspicuous
negative glint rings, and its three reflections read as distinct polished
highlights. They are still a little narrow/vertical compared with the reference.
The side view retains continuous wood but has inherited shading/texture seams
and an art-directed studio appearance. Hidden-side fidelity remains inferred.

Persistent defects: bowl crescents remain broad and patchy; crown tips/rim
reflections are fragmented; the bowl lip and inner curvature differ; much
grain is softer/coarser than the reference; collar/socket glints still break
up; the base highlight is too uniformly smooth in places. The mission is
unfinished. Next inspect the crown's bowl/rim reflection shape and local
surface relief without disturbing this finial improvement.

## Validation and reproduction

See accepted-finish-validation.json, accepted-material-geometry-check.json,
accepted-finial-material-check.json and accepted-material-reproduction-check.json.
The control remains closed, and all six render receivers preserve evaluated
faces, UVs and custom normals. Reopening and an independent reconstruction
verify that the delivered artifact reproduces its accepted render.

Rebuild from the archived checkpoint and delivered UV atlas:

```sh
blender -b -t 6 --python scripts/queen/rebuild_finial_checkpoint.py -- docs/queen-mission/iteration-017/reproduction.json
```

This creates trial 177-reproduced-stable-finial without changing the accepted model.
For the source pigment experiment, inspect_surface_components.py and
prepare_crown_pigment_repair.py accept --source history/queen-mission-016/queen-rebuilt.blend.
Use --only-finial --medium-grain 1.7 --reference-grain .7 for the repair.
The recorded masks, capture manifests, measured targets, actual saved light
properties, fit and bake manifests explain the derivation. No source reference
is changed. Bake only pigment and coverage with bake_pigment_patch.py, then
merge_pigment_patch.py preserves all unmasked texels exactly.

The review's fixed/side renders and interactive mesh/UV atlas are synchronized
from the same accepted model. Browser shading remains an approximation of
Cycles. Interaction checks use the established simulated DOM/WebGL harness,
not a claim of native browser GPU inspection. Local-preview sync and final
site checks are recorded separately. No push or publishing.

The full-set check_model_site.py run failed on a stale king model/export while
that piece was being edited separately. Its current-model loop covers the
other five pieces; the queen's dedicated viewer/camera/review checks, root-site
hash/link checks and queen projection validation passed. The king was not
modified. See whole-set-check-failure.txt and site-check-scope.json.

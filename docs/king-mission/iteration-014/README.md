# King checkpoint 014 â€” collar grain and stable light sampling

Accepted **162-no-tree-collar**, independently rebuilt as **163**, starting from
the archived checkpoint 013. The collar highlights carry more grain and look
less uniformly smooth. This is a modest finish improvement, not a full match.
The fixed 54-degree camera, all geometry, v6 pigment and lights are preserved.
The king mission remains active and incomplete.

## Examination and decision

A chroma-only pigment repair (153) and a new black/white-response pigment
estimate (155) did not visibly resolve the pale collar bands. Neither is kept.
The diagnostic emission view still shows residual illumination in the pigment,
while the black-pigment BSDF response shows that much of the visible streaking
comes from real reflections. Those images are analysis only; they never replace
the shaded beauty.

Local fine-varnish relief at 0.60 (157) gives the collar reflections more grain.
Adding coat roughness (158) loses useful contrast without a clear improvement.
Raising relief to 0.90 (159) makes the surface too dotted. The accepted material
therefore retains the medium relief alone. Upper bands, the missing breadth of
some glints, coarse/soft grain patches and residual pigment lighting remain.

The collar common-foreground RGB squared error changes from
410.153 to 415.961.
This is a supporting diagnostic, not a perceptual score or an acceptance rule.
The local appearance was judged in enlarged crops, the full image, both original
sprite colors and side/rear views. Original sprites remain authoritative; their
clipped cross is missing evidence rather than a desired flat cut.

| Metric | Checkpoint 013 | Checkpoint 014 |
| --- | ---: | ---: |
| High-res silhouette IoU | 97.8258% | 97.8260% |
| Interior form | 85% | 85% |
| Wood color | 82% | 82% |
| Grain / surface | 79% | 80% |
| Lighting / reflections | 69% | 69% |
| Equal-weight working mean | 82.5652% | 82.7652% |

Original overlap is 96.8466%. Only overlap is measured;
the other values are subjective visual ratings. Holistic range remains 75â€“85%.
No shape or lighting-score gain is awarded for the sampling change.

## Repeat-render failure and remedy

Trial 157 passed scene identity and independent reconstruction, but its repeated
saved-file beauty failed the existing 1/255 maximum bound: a small socket glint
changed by 45/255, with exact alpha and mean channel difference 0.0005383/255.
This is the earlier instability recurring through the canonical entry point,
not merely through the alternate renderer. All failed evidence is retained in
`failed-157-reproduction`; no tolerance was relaxed.

Following the queen checkpoint-017 investigation, trial 161 disables only
`cycles.use_light_tree`. Its geometry, material, emitters, camera, world and
other render settings are validated unchanged. Trial 162 combines that setting
with the selected finish. It retains 128 samples, adaptive sampling and denoising.
The canonical repeat differs by at most
1/255, and the independent
saved-file rebuild by at most
1/255, both with
exact alpha. The alternate entry point differs by at most
1/255 in this check.
This supports the light-tree sampling path as the cause in this scene; the
internal mechanism and universal determinism are not established.

## Exact scope and reproduction

The new point attribute `Collar varnish texture 014` smoothly rises over body
control rings 34â€“37, remains full through ring 60, and fades out over 60â€“63.
It is zero on the cross. It blends only `Fine varnish relief` strength to 0.60.
Its grain height signal, relief distance, base normal, roughness, coat, IOR,
v6 pigment, all previous material nodes and their inputs remain unchanged.
The attribute follows the model and is retained in the editable Blender file.
All nine exact render receivers are regenerated from the closed controls.

The two closed, intersecting body/cross components are not Boolean-fused.
Every control coordinate, original UV and attribute, packed image and light
setting is checked. The exported positions, normals, UVs and camera are
byte-identical to checkpoint 013. Physical dimensions and side-gallery defaults
remain unchanged. The only additional render setting is `use_light_tree=False`.

From the repository root:

```sh
blender --background --python-exit-code 1 --python scripts/king/local_finish_trial.py -- docs/king-mission/iteration-014/reproduction.json
blender --background --python-exit-code 1 --python scripts/king/render_fixed_diagnostics.py -- build/king-mission/163-no-tree-finish-reproduction/king.blend build/king-mission/163-no-tree-finish-reproduction --beauty-only
blender --background --python-exit-code 1 --python scripts/king/export_mission.py -- build/king-mission/163-no-tree-finish-reproduction/king.blend build/king-mission/163-no-tree-finish-reproduction
blender --background --python-exit-code 1 --python scripts/king/check_local_finish.py -- history/king-mission-013/king-rebuilt.blend build/king-mission/163-no-tree-finish-reproduction/king.blend docs/king-mission/iteration-014/reproduction.json build/king-mission/163-no-tree-finish-reproduction/scope-check.json
```

`verify_finish_candidate.py` runs the full scope, regeneration, export, saved
views, repeat and independent-build checks. Its candidate directory needs an
`input.json` matching the configuration used to build that candidate.
`record_finish_checkpoint_014.py` collects the evidence without publishing.
`diagnose_collar_pigment_response.py` creates the new read-only response analysis;
the older `diagnose_collar_finish.py` remains unchanged.

The rejected pigment prototype adds optional lower/upper bounds and unique
attribute/UV names to `recover_pigment.py`, so a collar experiment does not
replace older response fields. Trial 155 used the legacy render helper, which
overwrites `original_source_sha256` with the prepared-file hash. Its response
metadata and input still identify the real checkpoint-013 hash; the mislabeled
field is preserved in the evidence. An optional `preserve_light_rig` path avoids
that metadata overwrite for future work. That optional path is not part of this
accepted model. The new chroma-repair mode was tested as a shader only; its bake
path was not used. None of those pigment experiments changes current atlas pixels.

## Review, validation and remaining work

The fixed render, neutral inspection, side/rear views, registered side comparison
and rotating mesh are synchronized from the same accepted model. All
34 existing Windows preview files
match the repository by hash. King model validation, receiver regeneration,
exact export, king/candidate interaction harnesses and site/model checks pass.
The existing browser review was reloaded and its complete fixed-view frame
was inspected. HTTP model/render hashes match this checkpoint. The browser's
rotating view still uses approximate lighting; the fixed render
shows the actual Blender finish. Historical projection studies are unchanged
and were not rerun. The pre-existing whole-set knight sizing-metadata failure
remains separately documented; it is not reported as a passing check.

Remaining mismatches include the crown-platter rim and cross seat, collar band
shape and brightness, fine grain scale, baked illumination in parts of the
pigment, socket glint distribution, the small/low broad-base reflection and the
foot finish. Hidden wood is inferred. Next, examine the broader base reflection
and upper platter while preserving the accepted local collar relief and the
now-tested sampling configuration.

Model SHA-256: `47538b56ad400f77113af6a79a4fb89fc9b4532964622ca4ffcf7f3599f22ad5`.
Render SHA-256: `02df7625a18d6ca5112e5f0619210f306c558063cad8b95d84ce18e9d4079ea9`.
v6 pigment SHA-256: `6fc71802159bf7c9742a4c2adf83b6e3bdb5f0a8e57d31c864e1a1d2acaf73b4`.
